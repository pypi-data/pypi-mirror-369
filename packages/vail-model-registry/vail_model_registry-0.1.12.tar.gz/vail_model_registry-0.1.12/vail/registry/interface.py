"""
Registry Interface for the Unified Fingerprinting Framework

This module provides an interface to the model registry database for fingerprinting.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector

from vail.utils import setup_logging

from .models import Model, ModelFilterCriteria

# Set up logging
logger = setup_logging(log_file_name="model_registry.log")


class RegistryInterface:
    """Interface for interacting with the model registry database."""

    @property
    def registry_type(self) -> str:
        return "global"

    def __init__(self, connection_string: str, use_production: bool = False):
        """
        Initialize the registry interface.

        Args:
            connection_string: PostgreSQL connection string
            use_production: Whether to use the production database schema (default: False, use dev)
        """
        self.connection_string = connection_string
        self.schema = "prod" if use_production else "dev"

    # ============= Private Methods =============

    def _get_connection(self):
        """Get a database connection."""
        conn = psycopg2.connect(self.connection_string)
        # The following enables the pgvector extension to work in these schemas
        conn.cursor().execute("SET search_path TO dev, prod, public;")
        register_vector(conn)
        return conn

    @staticmethod
    def setup_global_registry(connection_string: str):
        """Set up the necessary database tables and extensions in both dev and prod schemas."""
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                # Create pgvector extension if it doesn't exist
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                # Create schemas if they don't exist
                cur.execute("CREATE SCHEMA IF NOT EXISTS dev;")
                cur.execute("CREATE SCHEMA IF NOT EXISTS prod;")

                for schema in ["dev", "prod"]:
                    # Create models table
                    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.models (
                        id SERIAL PRIMARY KEY,
                        model_maker TEXT,
                        model_name TEXT,
                        params_count BIGINT,
                        context_length BIGINT,
                        quantization TEXT,
                        license TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    """)

                    # Create model_sources table
                    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.model_sources (
                        id SERIAL PRIMARY KEY,
                        model_id INTEGER REFERENCES {schema}.models(id),
                        source_type TEXT NOT NULL,                            -- huggingface_api, openai, anthropic, ollama, etc.
                        source_identifier JSON NOT NULL,                      -- repo_id, model name, etc.
                        requires_auth BOOLEAN DEFAULT FALSE,                  -- Whether authentication is required
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    """)

                    # Create fingerprints table
                    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.fingerprints (
                        id SERIAL PRIMARY KEY,
                        model_id INTEGER REFERENCES {schema}.models(id),
                        fingerprint_type TEXT NOT NULL,                       -- input_output, weight, architecture
                        fingerprint_vector vector,                      -- Vector representation for similarity search
                        fingerprint_config JSONB,                             -- Configuration used to generate the fingerprint
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    """)

                    # Create model_observations table
                    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {schema}.model_observations (
                        id SERIAL PRIMARY KEY,
                        model_id INTEGER REFERENCES {schema}.models(id) ON DELETE CASCADE,
                        observation TEXT NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT,
                        tags TEXT[],
                        metadata JSONB
                    );
                    """)

                    # Create materialized view for fingerprint similarities cache
                    # Drop existing view first to ensure we get the new schema with cosine_similarity
                    cur.execute(
                        f"DROP MATERIALIZED VIEW IF EXISTS {schema}.fingerprint_similarities_cache CASCADE;"
                    )

                    cur.execute(f"""
                    CREATE MATERIALIZED VIEW {schema}.fingerprint_similarities_cache AS
                    WITH fingerprints_cte AS (
                        SELECT
                            f.model_id,
                            m.model_name,
                            f.fingerprint_type,
                            string_to_array(trim(BOTH '[]' FROM f.fingerprint_vector::text), ',')::float[] AS fingerprint_array
                        FROM {schema}.fingerprints f
                        JOIN {schema}.models m ON m.id = f.model_id
                    ),
                    fingerprint_pairs AS (
                        SELECT
                            f1.model_id AS model_id_1,
                            f2.model_id AS model_id_2,
                            f1.model_name AS model_name_1,
                            f2.model_name AS model_name_2,
                            f1.fingerprint_array AS fp1,
                            f2.fingerprint_array AS fp2,
                            f1.fingerprint_type
                        FROM fingerprints_cte f1
                        JOIN fingerprints_cte f2
                            ON (f1.model_id < f2.model_id)
                            AND (f1.fingerprint_type = f2.fingerprint_type)
                    ),
                    element_comparisons AS (
                        SELECT
                            model_id_1,
                            model_id_2,
                            model_name_1,
                            model_name_2,
                            fingerprint_type,
                            ABS(fp1[i] - fp2[i]) AS abs_diff,
                            fp1[i] + fp2[i] AS sum_vals,
                            (fp1[i] - fp2[i]) * (fp1[i] - fp2[i]) AS squared_diff,
                            fp1[i] * fp2[i] AS dot_product_element,
                            fp1[i] * fp1[i] AS fp1_squared,
                            fp2[i] * fp2[i] AS fp2_squared
                        FROM fingerprint_pairs
                        CROSS JOIN LATERAL generate_series(1, array_length(fp1, 1)) AS i
                    )
                    SELECT
                        model_id_1,
                        model_id_2,
                        model_name_1,
                        model_name_2,
                        fingerprint_type,
                        SUM(abs_diff) AS l1_distance,
                        SUM(sum_vals) AS total_sum,
                        1.0 - (SUM(abs_diff) / NULLIF(SUM(sum_vals), 0)) AS l1_similarity,
                        1.0 - (SQRT(SUM(squared_diff)) / (SQRT(SUM(fp1_squared)) + SQRT(SUM(fp2_squared)))) AS euclidean_similarity,
                        SUM(dot_product_element) AS dot_product,
                        SUM(dot_product_element) / NULLIF(SQRT(SUM(fp1_squared)) * SQRT(SUM(fp2_squared)), 0) AS cosine_similarity,
                        CURRENT_TIMESTAMP AS computed_at
                    FROM element_comparisons
                    GROUP BY
                        model_id_1,
                        model_id_2,
                        model_name_1,
                        model_name_2,
                        fingerprint_type;
                    """)

                    # Create indexes on the materialized view for better query performance
                    # First create a unique index to enable concurrent refresh
                    cur.execute(f"""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_{schema}_fingerprint_similarities_cache_unique
                    ON {schema}.fingerprint_similarities_cache (model_id_1, model_id_2, fingerprint_type);
                    """)

                    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{schema}_fingerprint_similarities_cache_model_ids 
                    ON {schema}.fingerprint_similarities_cache (model_id_1, model_id_2);
                    """)

                    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{schema}_fingerprint_similarities_cache_fingerprint_type 
                    ON {schema}.fingerprint_similarities_cache (fingerprint_type);
                    """)

                    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{schema}_fingerprint_similarities_cache_l1_similarity 
                    ON {schema}.fingerprint_similarities_cache (l1_similarity DESC);
                    """)

                    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{schema}_fingerprint_similarities_cache_euclidean_similarity 
                    ON {schema}.fingerprint_similarities_cache (euclidean_similarity DESC);
                    """)

                    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{schema}_fingerprint_similarities_cache_cosine_similarity 
                    ON {schema}.fingerprint_similarities_cache (cosine_similarity DESC);
                    """)

                conn.commit()

    # ============= Public Methods =============

    def get_model_loader_info(self, model_id: str) -> Dict:
        """
        Get model loader information from the registry.

        Args:
            model_id: ID of the model

        Returns:
            Dictionary with model loader information including all model data and sources
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Query model and sources in a single join query
                cur.execute(
                    f"""
                    SELECT 
                        m.id as model_id,
                        m.model_maker,
                        m.model_name,
                        m.params_count,
                        m.context_length,
                        m.quantization,
                        m.license,
                        m.created_at as model_created_at,
                        m.last_updated as model_last_updated,
                        s.id as source_id,
                        s.source_type,
                        s.source_identifier,
                        s.requires_auth,
                        s.created_at as source_created_at,
                        s.last_updated as source_last_updated
                    FROM {self.schema}.models m
                    LEFT JOIN {self.schema}.model_sources s ON m.id = s.model_id
                    WHERE m.id = %s
                """,
                    (model_id,),
                )

                results = cur.fetchall()

                # Construct comprehensive model info dictionary
                model_info = {
                    "id": str(results[0][0]),
                    "model_maker": results[0][1],
                    "model_name": results[0][2],
                    "params_count": results[0][3],
                    "context_length": results[0][4],
                    "quantization": results[0][5],
                    "license": results[0][6],
                    "created_at": results[0][7].isoformat() if results[0][7] else None,
                    "last_updated": results[0][8].isoformat()
                    if results[0][8]
                    else None,
                    "sources": [],
                }

                # Add all sources
                for row in results:
                    if row[9]:  # If source_id is not None
                        source = {
                            "source_id": row[9],
                            "source_type": row[10],
                            "source_identifier": row[11],
                            "requires_auth": row[12],
                            "created_at": row[13].isoformat() if row[13] else None,
                            "last_updated": row[14].isoformat() if row[14] else None,
                        }
                        model_info["sources"].append(source)

                return model_info

    def remove_model(self, model_id: str):
        """
        Remove a model from the registry.

        Args:
            model_id: ID of the model to remove
        """
        with self._get_connection() as conn:
            logger.info(f"Removing model with ID: {model_id} from {self.schema} schema")
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    DELETE FROM {self.schema}.fingerprints
                    WHERE model_id = %s
                """,
                    (model_id,),
                )

                cur.execute(
                    f"""
                    DELETE FROM {self.schema}.model_sources
                    WHERE model_id = %s
                """,
                    (model_id,),
                )

                cur.execute(
                    f"""
                    DELETE FROM {self.schema}.models
                    WHERE id = %s
                """,
                    (model_id,),
                )

                conn.commit()

    def add_model(self, model_info: Dict, override_checks: bool = False) -> str:
        """
        Add a model to the registry.

        Args:
            model_info: Dictionary containing model information
            override_checks: Whether to override validation checks (for prod schema)

        Returns:
            str: ID of the added model
        """
        with self._get_connection() as conn:
            logger.info(f"Adding model: {model_info} to {self.schema} schema")

            # For production schema, perform validation checks
            if self.schema == "prod" and not override_checks:
                with conn.cursor() as cur:
                    # Check if model with same name already exists
                    cur.execute(
                        f"""
                        SELECT id FROM {self.schema}.models 
                        WHERE LOWER(model_name) = LOWER(%s)
                    """,
                        (model_info.get("model_name", ""),),
                    )

                    existing_model = cur.fetchone()

                    if existing_model:
                        logger.warning(
                            f"Model with name {model_info.get('model_name')} already exists in production database. Skipping."
                        )
                        return str(existing_model[0])

            with conn.cursor() as cur:
                # First try to get existing model
                cur.execute(
                    """
                    SELECT id FROM models WHERE model_name = %s
                """,
                    (model_info.get("model_name", None),),
                )
                existing = cur.fetchone()

                if existing:
                    logger.info(f"Model {model_info.get('model_name')} already exists")
                    return str(existing[0])

                # If not exists, insert new model
                cur.execute(
                    """
                    INSERT INTO models (model_maker, model_name, params_count, context_length, quantization, license, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        model_info.get("model_maker", None),
                        model_info.get("model_name", None),
                        model_info.get("params_count", None),
                        model_info.get("context_length", None),
                        model_info.get("quantization", None),
                        model_info.get("license", None),
                        model_info.get("created_at", datetime.now()),
                    ),
                )
                return str(cur.fetchone()[0])

    def add_model_source(
        self,
        model_id: str,
        source_type: str,
        source_info: Dict,
        override_checks: bool = False,
    ) -> str:
        """
        Add a source for a model in the registry.

        Args:
            model_id: ID of the model
            source_type: Type of source (huggingface, openai, anthropic, ollama, etc.)
            source_info: Dictionary containing source information
            override_checks: Whether to override validation checks (for prod schema)

        Returns:
            str: ID of the added model source
        """
        with self._get_connection() as conn:
            logger.info(f"Adding model source: {source_info} to {self.schema} schema")

            # For production schema, perform validation checks
            if self.schema == "prod" and not override_checks:
                with conn.cursor() as cur:
                    # Check if source with same identifier already exists
                    source_identifier = source_info.get("source_identifier", None)
                    if source_identifier:
                        # Ensure source_identifier is converted to JSON string for comparison
                        source_identifier_json = json.dumps(source_identifier)
                        cur.execute(
                            f"""
                            SELECT id FROM {self.schema}.model_sources 
                            WHERE LOWER(source_identifier::text) = LOWER(%s)
                        """,
                            (source_identifier_json,),
                        )

                        if cur.fetchone():
                            logger.warning(
                                f"Model source with identifier {source_identifier} already exists in production database. Skipping."
                            )
                            return None

            # Convert source_identifier to JSON string if it's a dictionary
            source_identifier = source_info.get("source_identifier", None)
            if isinstance(source_identifier, dict):
                source_identifier_json = json.dumps(source_identifier)
            else:
                source_identifier_json = source_identifier

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self.schema}.model_sources (model_id, source_type, source_identifier, requires_auth, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        model_id,
                        source_type,
                        source_identifier_json,
                        source_info.get("requires_auth", False),
                        source_info.get("created_at", datetime.now()),
                    ),
                )
                source_id = str(cur.fetchone()[0])

                # Update the parent model's last_updated timestamp
                cur.execute(
                    f"""
                    UPDATE {self.schema}.models 
                    SET last_updated = CURRENT_TIMESTAMP
                    WHERE id = %s
                """,
                    (model_id,),
                )

                return source_id

    # ============= Model Observation Methods =============

    def add_model_observation(
        self,
        model_id: str,
        observation: str,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Add an observation for a model.

        Args:
            model_id: ID of the model to add observation for
            observation: Text description of the observation
            created_by: Optional identifier of who created the observation
            tags: Optional list of tags to categorize the observation
            metadata: Optional dictionary of additional metadata

        Returns:
            str: ID of the added observation

        Raises:
            ValueError: If observation is empty or contains only whitespace
        """
        # Validate observation
        if not observation or not observation.strip():
            raise ValueError("Observation cannot be empty")

        with self._get_connection() as conn:
            logger.info(f"Adding observation for model {model_id}")

            with conn.cursor() as cur:
                # Verify model exists
                cur.execute(
                    f"SELECT id FROM {self.schema}.models WHERE id = %s", (model_id,)
                )

                if not cur.fetchone():
                    raise ValueError(f"Model with id {model_id} not found")

                # Insert observation
                cur.execute(
                    f"""
                    INSERT INTO {self.schema}.model_observations 
                    (model_id, observation, created_by, tags, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        model_id,
                        observation,
                        created_by,
                        tags,
                        json.dumps(metadata) if metadata else None,
                    ),
                )

                observation_id = str(cur.fetchone()[0])

                # Update the parent model's last_updated timestamp
                cur.execute(
                    f"""
                    UPDATE {self.schema}.models 
                    SET last_updated = CURRENT_TIMESTAMP
                    WHERE id = %s
                """,
                    (model_id,),
                )

                logger.info(f"Added observation {observation_id} for model {model_id}")
                return observation_id

    def get_model_observations(
        self,
        model_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Get observations for a model.

        Args:
            model_id: ID of the model to get observations for
            limit: Maximum number of observations to return
            offset: Number of observations to skip
            tags: Optional list of tags to filter by (returns observations with ANY of the tags)

        Returns:
            List of observation dictionaries
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                query = f"""
                    SELECT 
                        id,
                        model_id,
                        observation,
                        created_at,
                        created_by,
                        tags,
                        metadata
                    FROM {self.schema}.model_observations
                    WHERE model_id = %s
                """
                params = [model_id]

                # Add tag filter if provided
                if tags:
                    query += (
                        " AND tags && %s"  # && is the "overlaps" operator for arrays
                    )
                    params.append(tags)

                query += " ORDER BY created_at DESC"

                # Add pagination
                if limit is not None:
                    query += " LIMIT %s"
                    params.append(limit)
                if offset is not None:
                    query += " OFFSET %s"
                    params.append(offset)

                cur.execute(query, params)

                columns = [desc[0] for desc in cur.description]
                observations = []

                for row in cur.fetchall():
                    obs_dict = dict(zip(columns, row))
                    observations.append(obs_dict)

                return observations

    # ============= Fingerprint Methods =============

    def register_fingerprint(
        self,
        model_id: str,
        fingerprint_type: str,
        fingerprint_vector: np.ndarray,
        fingerprint_config: Dict,
        override_checks: bool = False,
    ) -> str:
        """
        Register a fingerprint with the registry.

        Args:
            model_id: ID of the model
            fingerprint_type: Type of fingerprint (input_output, weight, architecture)
            fingerprint_vector: Fingerprint data as numpy array
            fingerprint_config: Configuration used to generate the fingerprint
            override_checks: Whether to override validation checks (for prod schema)

        Returns:
            str: ID of the registered fingerprint
        """
        # Convert the fingerprint data to the format expected by the registry
        fingerprint_vector = fingerprint_vector.flatten()

        # Register the fingerprint
        with self._get_connection() as conn:
            logger.info(
                f"Registering fingerprint of type {fingerprint_type} for model {model_id} in {self.schema} schema"
            )

            # For production schema, perform validation checks
            if self.schema == "prod" and not override_checks:
                with conn.cursor() as cur:
                    # 1. Check if identical fingerprint_vector already exists
                    cur.execute(
                        f"""
                        SELECT id FROM {self.schema}.fingerprints 
                        WHERE fingerprint_vector = %s::vector
                    """,
                        (fingerprint_vector.tolist(),),
                    )

                    if cur.fetchone():
                        logger.warning(
                            "Identical fingerprint vector already exists in production database. Skipping."
                        )
                        return None

                    # 2. Check if another fingerprint already exists for this model_id and fingerprint_type
                    cur.execute(
                        f"""
                        SELECT id FROM {self.schema}.fingerprints 
                        WHERE model_id = %s AND fingerprint_type = %s
                    """,
                        (model_id, fingerprint_type),
                    )

                    if cur.fetchone():
                        logger.warning(
                            f"Fingerprint for model_id {model_id} with type {fingerprint_type} already exists in production database. Skipping."
                        )
                        return None

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self.schema}.fingerprints 
                    (model_id, fingerprint_type, fingerprint_vector, fingerprint_config)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        model_id,
                        fingerprint_type,
                        fingerprint_vector.tolist(),
                        json.dumps(fingerprint_config),
                    ),
                )

                fingerprint_id = cur.fetchone()[0]
                conn.commit()

                # Automatically refresh similarity cache when new fingerprints are added
                try:
                    result = self.refresh_similarity_cache(incremental=True)
                    if result["status"] == "success":
                        logger.debug(
                            f"Refreshed similarity cache: {result['cache_count']} similarities in {result['duration_seconds']:.2f}s"
                        )
                    else:
                        logger.warning(
                            f"Cache refresh failed: {result.get('error', 'Unknown error')}"
                        )
                except Exception as e:
                    logger.warning(f"Similarity cache refresh failed: {e}")
                    # Don't fail the fingerprint registration if cache refresh fails

                return str(fingerprint_id)

    def get_fingerprint(
        self, model_id: str, fingerprint_type: str
    ) -> Optional[np.ndarray]:
        """
        Get a fingerprint from the registry.

        Args:
            model_id: ID of the model
            fingerprint_type: Type of fingerprint (input_output, weight, architecture)

        Returns:
            Fingerprint as numpy array, or None if not found
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT fingerprint_vector
                    FROM {self.schema}.fingerprints
                    WHERE model_id = %s AND fingerprint_type = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """,
                    (model_id, fingerprint_type),
                )

                row = cur.fetchone()

                if row is None:
                    return None

                # Convert to numpy array
                return np.array(row[0])

    def get_fingerprint_config(
        self, model_id: str, fingerprint_type: str
    ) -> Optional[Dict]:
        """
        Get a fingerprint configuration from the registry.

        Args:
            model_id: ID of the model
            fingerprint_type: Type of fingerprint (input_output, weight, architecture)

        Returns:
            Fingerprint configuration as a dictionary, or None if not found
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT fingerprint_config
                    FROM {self.schema}.fingerprints
                    WHERE model_id = %s AND fingerprint_type = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """,
                    (model_id, fingerprint_type),
                )

                row = cur.fetchone()

                if row is None:
                    return None

                # Convert from JSON string to dictionary
                if isinstance(row[0], str):
                    return json.loads(row[0])
                return row[0]

    def get_all_fingerprints(self, model_id: str) -> Dict[str, Dict]:
        """
        Get all fingerprints for a model from the registry.

        Args:
            model_id: ID of the model

        Returns:
            Dictionary mapping fingerprint types to their data and config, or empty dict if none found
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT
                        id,
                        fingerprint_type,
                        fingerprint_vector,
                        fingerprint_config,
                        created_at,
                        last_updated
                    FROM {self.schema}.fingerprints
                    WHERE model_id = %s
                    ORDER BY created_at DESC
                """,
                    (model_id,),
                )

                fingerprints = {}
                for row in cur.fetchall():
                    fingerprint_type = row[1]
                    fingerprint_vector = row[2]
                    fingerprint_config = row[3]
                    created_at = row[4]
                    last_updated = row[5]

                    # Convert config from JSON string if needed
                    if isinstance(fingerprint_config, str):
                        fingerprint_config = json.loads(fingerprint_config)

                    fingerprints[fingerprint_type] = {
                        "id": row[0],
                        "vector": fingerprint_vector,
                        "config": fingerprint_config,
                        "created_at": created_at,
                        "last_updated": last_updated,
                    }

                return fingerprints

    # ============= Model Search & Count Methods =============

    def get_model_id_from_source_id(self, source_id: str) -> str:
        """Retrieve the model_id associated with a given source_id."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT model_id FROM {self.schema}.model_sources WHERE id = %s",
                        (source_id,),
                    )
                    result = cur.fetchone()
                    if result:
                        return str(result[0])
                    else:
                        return None
        except Exception as e:
            logger.error(f"Error fetching model_id for source_id {source_id}: {e}")
            return None

    def count_models(self) -> int:
        """
        Count the total number of models in the registry.

        Returns:
            int: Total number of models
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {self.schema}.models
                """
                )
                return cur.fetchone()[0]

    def find_model(self, model_id: str) -> Optional[Model]:
        """
        Find a model in the registry by its ID.

        Args:
            model_id: ID of the model to find

        Returns:
            Model object with its sources and fingerprints, or None if not found
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT 
                        m.id as model_id,
                        m.model_maker,
                        m.model_name,
                        m.params_count,
                        m.context_length,
                        m.quantization,
                        m.license,
                        m.created_at,
                        (
                            SELECT json_agg(
                                json_build_object(
                                    'source_id', s.id,
                                    'source_type', s.source_type,
                                    'source_identifier', s.source_identifier,
                                    'requires_auth', s.requires_auth,
                                    'created_at', s.created_at
                                )
                            )
                            FROM {self.schema}.model_sources s
                            WHERE s.model_id = m.id
                        ) as sources,
                        m.last_updated
                    FROM {self.schema}.models m
                    WHERE m.id = %s
                """,
                    (model_id,),
                )

                row = cur.fetchone()

                if row is None:
                    return None

                # Construct model dictionary from row data
                model_dict = {
                    "id": row[0],
                    "model_maker": row[1],
                    "model_name": row[2],
                    "params_count": row[3],
                    "context_length": row[4],
                    "quantization": row[5],
                    "license": row[6],
                    "created_at": row[7],
                    "sources": row[8] if row[8] else [],
                    "last_updated": row[9],
                }

                # Instantiate Model correctly using name and model_info
                return Model(name=model_dict["model_name"], model_info=model_dict)

    def find_models(
        self,
        filters: Optional[ModelFilterCriteria] = None,
    ) -> List[Model]:
        """
        Find models in the registry that match the given criteria.

        Args:
            filters: ModelFilterCriteria object with filter conditions.

        Returns:
            List of Model objects with their sources and fingerprints
        """
        with self._get_connection() as conn:
            logger.debug("Finding models by criteria")
            with conn.cursor() as cur:
                # Build the query
                query = f"""
                    SELECT 
                        m.id as model_id,
                        m.model_maker,
                        m.model_name,
                        m.params_count,
                        m.context_length,
                        m.quantization,
                        m.license,
                        m.created_at,
                        m.last_updated,
                        (
                            SELECT json_agg(
                                json_build_object(
                                    'source_id', s.id,
                                    'source_type', s.source_type,
                                    'source_identifier', s.source_identifier,
                                    'requires_auth', s.requires_auth,
                                    'created_at', s.created_at,
                                    'last_updated', s.last_updated
                                )
                            )
                            FROM {self.schema}.model_sources s
                            WHERE s.model_id = m.id
                        ) as sources
                    FROM {self.schema}.models m
                    WHERE 1=1
                """
                params = []

                # Add filters if provided
                if filters and not filters.is_empty():
                    filter_conditions, filter_params = filters.to_sql_filters(
                        table_alias="m", placeholder_style="%s"
                    )
                    logger.debug(f"Filter conditions: {filter_conditions}")
                    logger.debug(f"Filter params: {filter_params}")
                    # Add last_updated filter if provided
                    query += f" AND {filter_conditions}"
                    params.extend(filter_params)

                query += " GROUP BY m.id, m.model_maker, m.model_name, m.params_count, m.context_length, m.quantization, m.license, m.created_at, m.last_updated"

                cur.execute(query, params)
                rows = cur.fetchall()

                # Convert rows to Model objects
                models = []
                for row in rows:
                    model_dict = {
                        "id": row[0],
                        "model_maker": row[1],
                        "model_name": row[2],
                        "params_count": row[3],
                        "context_length": row[4],
                        "quantization": row[5],
                        "license": row[6],
                        "created_at": row[7],
                        "last_updated": row[8],
                        "sources": row[9] if row[9] else [],
                    }

                    # Create a Model object
                    model = Model(name=model_dict["model_name"], model_info=model_dict)
                    models.append(model)

                return models

    # ============= Model Management Methods =============

    def copy_model_to_production(
        self, model_id: str, override_checks: bool = False
    ) -> Optional[str]:
        """
        Copy a model from dev to production database.

        Args:
            model_id: ID of the model in dev schema
            override_checks: Whether to override validation checks

        Returns:
            str: ID of the copied model in production, or None if checks failed
        """
        # First get model and source info from dev
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        m.model_maker,
                        m.model_name,
                        m.params_count,
                        m.context_length,
                        m.quantization,
                        m.license,
                        m.created_at
                    FROM dev.models m
                    WHERE m.id = %s
                """,
                    (model_id,),
                )

                model_data = cur.fetchone()
                if not model_data:
                    logger.error(f"Model with ID {model_id} not found in dev schema")
                    return None

                # Get source info
                cur.execute(
                    """
                    SELECT 
                        s.source_type,
                        s.source_identifier,
                        s.requires_auth,
                        s.created_at
                    FROM dev.model_sources s
                    WHERE s.model_id = %s
                """,
                    (model_id,),
                )

                source_data = cur.fetchone()

        # Create prod registry interface
        prod_registry = RegistryInterface(self.connection_string, use_production=True)

        # Create model info dict
        model_info = {
            "model_maker": model_data[0],
            "model_name": model_data[1],
            "params_count": model_data[2],
            "context_length": model_data[3],
            "quantization": model_data[4],
            "license": model_data[5],
            "created_at": model_data[6],
        }

        # Add model to production
        prod_model_id = prod_registry.add_model(
            model_info, override_checks=override_checks
        )
        if not prod_model_id:
            return None

        # Add source info
        if source_data:
            source_info = {
                "source_identifier": source_data[1],
                "requires_auth": source_data[2],
                "created_at": source_data[3],
            }

            prod_registry.add_model_source(
                model_id=prod_model_id,
                source_type=source_data[0],
                source_info=source_info,
                override_checks=override_checks,
            )

        return prod_model_id

    def copy_fingerprint_to_production(
        self,
        model_id: str,
        fingerprint_type: str,
        prod_model_id: str,
        override_checks: bool = False,
    ) -> Optional[str]:
        """
        Copy a fingerprint from dev to production database.

        Args:
            model_id: ID of the model in dev schema
            fingerprint_type: Type of fingerprint to copy
            prod_model_id: ID of the model in production schema
            override_checks: Whether to override validation checks

        Returns:
            str: ID of the copied fingerprint in production, or None if checks failed
        """
        # Get fingerprint data from dev
        fingerprint_data = self.get_fingerprint(model_id, fingerprint_type)
        if fingerprint_data is None:
            logger.error(
                f"Fingerprint of type {fingerprint_type} for model {model_id} not found in dev schema"
            )
            return None

        # Get fingerprint config
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT fingerprint_config
                    FROM dev.fingerprints
                    WHERE model_id = %s AND fingerprint_type = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """,
                    (model_id, fingerprint_type),
                )

                config_data = cur.fetchone()
                if not config_data:
                    logger.error(
                        f"Fingerprint config for model {model_id} and type {fingerprint_type} not found in dev schema"
                    )
                    return None

                fingerprint_config = config_data[0]

        # Create prod registry interface
        prod_registry = RegistryInterface(self.connection_string, use_production=True)

        # Register fingerprint in production
        return prod_registry.register_fingerprint(
            model_id=prod_model_id,
            fingerprint_type=fingerprint_type,
            fingerprint_vector=fingerprint_data,
            fingerprint_config=fingerprint_config,
            override_checks=override_checks,
        )

    def check_duplicate_fingerprints_in_prod(self) -> List[Dict]:
        """
        Check for duplicate fingerprints in the production database.

        Returns:
            List of dictionaries with duplicate fingerprint information
        """
        if self.schema != "prod":
            # Create prod registry interface
            prod_registry = RegistryInterface(
                self.connection_string, use_production=True
            )
            return prod_registry.check_duplicate_fingerprints_in_prod()

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Find duplicate fingerprint vectors
                cur.execute("""
                    SELECT 
                        f1.fingerprint_vector,
                        array_agg(f1.id) as fingerprint_ids,
                        array_agg(f1.model_id) as model_ids
                    FROM prod.fingerprints f1
                    JOIN prod.fingerprints f2 ON 
                        f1.fingerprint_vector::text = f2.fingerprint_vector::text AND 
                        f1.id < f2.id
                    GROUP BY f1.fingerprint_vector
                """)

                duplicates = []
                for row in cur.fetchall():
                    duplicates.append(
                        {
                            "fingerprint_ids": row[1],
                            "model_ids": row[2],
                            "duplicate_type": "identical_vector",
                        }
                    )

                return duplicates

    def check_multiple_fingerprints_per_model_in_prod(self) -> List[Dict]:
        """
        Check for multiple fingerprints for the same model_id and fingerprint_type in production.

        Returns:
            List of dictionaries with information about models that have multiple fingerprints
        """
        if self.schema != "prod":
            # Create prod registry interface
            prod_registry = RegistryInterface(
                self.connection_string, use_production=True
            )
            return prod_registry.check_multiple_fingerprints_per_model_in_prod()

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Find models with multiple fingerprints of the same type
                cur.execute("""
                    SELECT 
                        model_id,
                        fingerprint_type,
                        COUNT(*) as fingerprint_count,
                        array_agg(id) as fingerprint_ids
                    FROM prod.fingerprints
                    GROUP BY model_id, fingerprint_type
                    HAVING COUNT(*) > 1
                """)

                multiples = []
                for row in cur.fetchall():
                    multiples.append(
                        {
                            "model_id": row[0],
                            "fingerprint_type": row[1],
                            "fingerprint_count": row[2],
                            "fingerprint_ids": row[3],
                        }
                    )

                return multiples

    # ============= Phase 2: Similarity Cache Methods =============

    def refresh_similarity_cache(self, incremental: bool = True) -> Dict:
        """
        Refresh the fingerprint similarities materialized view.

        Args:
            incremental: If True, use REFRESH MATERIALIZED VIEW CONCURRENTLY for non-blocking updates.
                        If False, use full refresh which may block queries but is faster.

        Returns:
            Dictionary with refresh status and timing information
        """
        start_time = datetime.now()

        refresh_command = "REFRESH MATERIALIZED VIEW"
        if incremental:
            refresh_command += " CONCURRENTLY"

        refresh_command += f" {self.schema}.fingerprint_similarities_cache"

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                logger.info(
                    f"Starting similarity cache refresh for {self.schema} schema (incremental={incremental})"
                )

                cur.execute(refresh_command)
                conn.commit()

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Get cache statistics
                cur.execute(
                    f"SELECT COUNT(*) FROM {self.schema}.fingerprint_similarities_cache"
                )
                cache_count = cur.fetchone()[0]

                logger.info(
                    f"Similarity cache refresh completed in {duration:.2f} seconds. Cache contains {cache_count} similarity pairs."
                )

                return {
                    "status": "success",
                    "schema": self.schema,
                    "incremental": incremental,
                    "duration_seconds": duration,
                    "cache_count": cache_count,
                    "refreshed_at": end_time.isoformat(),
                }

    def get_model_similarities(
        self,
        model_ids: Optional[List[int]] = None,
        fingerprint_type: Optional[str] = None,
        threshold: Optional[float] = None,
        similarity_metric: str = "l1_similarity",
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get similarity scores from the cached materialized view.

        Args:
            model_ids: List of model IDs to filter results (optional)
            fingerprint_type: The specific type of fingerprint to compare (optional)
            threshold: Similarity score threshold for filtering results (optional)
            similarity_metric: Which similarity metric to use for threshold filtering
                             ('l1_similarity', 'euclidean_similarity', 'dot_product', 'cosine_similarity')
            limit: Maximum number of results to return (optional)

        Returns:
            List of dictionaries containing similarity data
        """
        query = f"SELECT * FROM {self.schema}.fingerprint_similarities_cache WHERE 1=1"
        params = []

        # Add model ID filters
        if model_ids:
            placeholders = ",".join(["%s"] * len(model_ids))
            query += f" AND (model_id_1 IN ({placeholders}) AND model_id_2 IN ({placeholders}))"
            params.extend(model_ids)
            params.extend(model_ids)

        # Add fingerprint type filter
        if fingerprint_type:
            query += " AND fingerprint_type = %s"
            params.append(fingerprint_type)

        # Add threshold filter
        if threshold is not None:
            # All metrics are now similarity metrics, higher is better
            query += f" AND {similarity_metric} >= %s"
            params.append(threshold)

        # Add ordering and limit
        query += f" ORDER BY {similarity_metric} DESC"  # Higher similarity is better

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                results = cur.fetchall()

                # Get column names
                columns = [desc[0] for desc in cur.description]

                # Convert to list of dictionaries
                similarities = []
                for row in results:
                    similarity_dict = dict(zip(columns, row))
                    # Convert datetime to ISO string for JSON serialization
                    if (
                        "computed_at" in similarity_dict
                        and similarity_dict["computed_at"]
                    ):
                        similarity_dict["computed_at"] = similarity_dict[
                            "computed_at"
                        ].isoformat()
                    similarities.append(similarity_dict)

                return similarities

    def find_similar_models(
        self,
        model_id: int,
        fingerprint_type: Optional[str] = None,
        threshold: float = 0.99,
        similarity_metric: str = "l1_similarity",
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Find models similar to a given model using the cached similarities.

        Args:
            model_id: The ID of the model to find similar models for
            fingerprint_type: The specific type of fingerprint to compare (optional)
            threshold: The similarity score threshold
            similarity_metric: Which similarity metric to use for threshold filtering
                             ('l1_similarity', 'euclidean_similarity', 'dot_product', 'cosine_similarity')
            limit: Maximum number of results to return (optional)

        Returns:
            List of dictionaries containing information about similar models
        """
        query = f"""
            SELECT * FROM {self.schema}.fingerprint_similarities_cache 
            WHERE (model_id_1 = %s OR model_id_2 = %s)
        """
        params = [model_id, model_id]

        if fingerprint_type:
            query += " AND fingerprint_type = %s"
            params.append(fingerprint_type)

        # All metrics are now similarity metrics, higher is better
        query += f" AND {similarity_metric} >= %s"
        params.append(threshold)

        # Add ordering
        query += f" ORDER BY {similarity_metric} DESC"  # Higher similarity is better

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                results = cur.fetchall()

                # Get column names
                columns = [desc[0] for desc in cur.description]

                # Convert to list of dictionaries and add helper fields
                similar_models = []
                for row in results:
                    similarity_dict = dict(zip(columns, row))

                    # Add the "other" model ID and name (the one that's not the input model_id)
                    if similarity_dict["model_id_1"] == model_id:
                        similarity_dict["similar_model_id"] = similarity_dict[
                            "model_id_2"
                        ]
                        similarity_dict["similar_model_name"] = similarity_dict[
                            "model_name_2"
                        ]

                    elif similarity_dict["model_id_2"] == model_id:
                        similarity_dict["similar_model_id"] = similarity_dict[
                            "model_id_1"
                        ]
                        similarity_dict["similar_model_name"] = similarity_dict[
                            "model_name_1"
                        ]

                    # Convert datetime to ISO string for JSON serialization
                    if (
                        "computed_at" in similarity_dict
                        and similarity_dict["computed_at"]
                    ):
                        similarity_dict["computed_at"] = similarity_dict[
                            "computed_at"
                        ].isoformat()

                    similar_models.append(similarity_dict)

                return similar_models

    def get_similarity_cache_stats(self) -> Dict:
        """
        Get statistics about the similarity cache.

        Returns:
            Dictionary with cache statistics
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                stats = {"schema": self.schema}

                # Total number of cached similarities
                cur.execute(
                    f"SELECT COUNT(*) FROM {self.schema}.fingerprint_similarities_cache"
                )
                stats["total_similarities"] = cur.fetchone()[0]

                # Number of unique models in cache
                cur.execute(f"""
                    SELECT COUNT(DISTINCT model_id) FROM (
                        SELECT model_id_1 as model_id FROM {self.schema}.fingerprint_similarities_cache
                        UNION 
                        SELECT model_id_2 as model_id FROM {self.schema}.fingerprint_similarities_cache
                    ) unique_models
                """)
                stats["unique_models"] = cur.fetchone()[0]

                # Number of fingerprint types
                cur.execute(
                    f"SELECT COUNT(DISTINCT fingerprint_type) FROM {self.schema}.fingerprint_similarities_cache"
                )
                stats["unique_fingerprint_types"] = cur.fetchone()[0]

                # Cache age (time since last refresh)
                cur.execute(
                    f"SELECT MAX(computed_at) FROM {self.schema}.fingerprint_similarities_cache"
                )
                last_computed = cur.fetchone()[0]
                if last_computed:
                    cache_age = (
                        datetime.now(last_computed.tzinfo) - last_computed
                    ).total_seconds()
                    stats["cache_age_seconds"] = cache_age
                    stats["last_computed_at"] = last_computed.isoformat()
                else:
                    stats["cache_age_seconds"] = None
                    stats["last_computed_at"] = None

                # Average similarity scores by metric
                cur.execute(f"""
                    SELECT 
                        AVG(l1_similarity) as avg_l1_similarity,
                        AVG(euclidean_similarity) as avg_euclidean_similarity,
                        AVG(dot_product) as avg_dot_product,
                        AVG(cosine_similarity) as avg_cosine_similarity
                    FROM {self.schema}.fingerprint_similarities_cache
                """)
                avg_row = cur.fetchone()
                if avg_row:
                    stats["average_l1_similarity"] = (
                        float(avg_row[0]) if avg_row[0] else None
                    )
                    stats["average_euclidean_similarity"] = (
                        float(avg_row[1]) if avg_row[1] else None
                    )
                    stats["average_dot_product"] = (
                        float(avg_row[2]) if avg_row[2] else None
                    )
                    stats["average_cosine_similarity"] = (
                        float(avg_row[3]) if avg_row[3] else None
                    )

                return stats
