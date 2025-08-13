"""
Local Registry Interface for the Unified Fingerprinting Framework

This module provides a local interface to the model registry database using DuckDB as a cache.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import duckdb
import numpy as np

from vail.constants import FP_SIM_THRESHOLD_L1
from vail.fingerprint.metrics import get_similarity_metric
from vail.registry.interface import RegistryInterface
from vail.registry.models import (
    Model,
    ModelFilterCriteria,
    generate_canonical_id,
)
from vail.utils import (
    HardwareInfo,
    HardwareProfiler,
    setup_logging,
)

# Set up logging
logger = setup_logging(log_file_name="local_registry.log")


class LocalRegistryInterface:
    """Interface for interacting with a local DuckDB cache of the model registry."""

    @property
    def registry_type(self) -> str:
        return "local"

    def __init__(
        self,
        connection_string: str,
        local_db_path: str = "local_registry.duckdb",
    ):
        """
        Initialize the local registry interface.

        Args:
            connection_string: PostgreSQL connection string for the main registry
            local_db_path: Path to the local DuckDB database file
        """
        self.local_db_path = local_db_path
        self.global_registry = RegistryInterface(connection_string)
        if not os.path.exists(local_db_path):
            LocalRegistryInterface.setup_local_registry(
                local_db_path, connection_string
            )

    @staticmethod
    def create_local_registry_tables(local_db_path: str):
        """Create all required tables and sequences in the local DuckDB database."""
        with duckdb.connect(local_db_path) as conn:
            # Test table to ensure DB is working
            conn.execute("CREATE TABLE IF NOT EXISTS vail_init_test (id INTEGER);")
            conn.execute("INSERT INTO vail_init_test VALUES (1);")
            conn.execute("DROP TABLE vail_init_test;")

            # Create models table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY,
                    canonical_id TEXT UNIQUE,
                    model_maker TEXT,
                    model_name TEXT,
                    params_count BIGINT,
                    context_length BIGINT,
                    quantization TEXT,
                    license TEXT,
                    created_at TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute(
                "CREATE SEQUENCE IF NOT EXISTS model_id_seq START WITH 1 INCREMENT BY 1;"
            )

            # Create model_sources table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_sources (
                    id INTEGER PRIMARY KEY,
                    model_id INTEGER REFERENCES models(id),
                    source_type TEXT NOT NULL,
                    source_identifier JSON NOT NULL,
                    requires_auth BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute(
                "CREATE SEQUENCE IF NOT EXISTS model_sources_id_seq START WITH 1 INCREMENT BY 1;"
            )

            # Create fingerprints table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fingerprints (
                    id INTEGER PRIMARY KEY,
                    model_id INTEGER REFERENCES models(id),
                    fingerprint_type TEXT NOT NULL,
                    fingerprint_vector FLOAT[],
                    fingerprint_config JSON,
                    created_at TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute(
                "CREATE SEQUENCE IF NOT EXISTS fingerprint_id_seq START WITH 1 INCREMENT BY 1;"
            )

            # Create model_observations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_observations (
                    id INTEGER PRIMARY KEY,
                    model_id INTEGER REFERENCES models(id),
                    observation TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    tags TEXT[],
                    metadata JSON
                );
            """)
            conn.execute(
                "CREATE SEQUENCE IF NOT EXISTS model_observations_id_seq START WITH 1 INCREMENT BY 1;"
            )

            # Create fingerprint_similarities view for real-time similarity computation
            conn.execute("""
                CREATE OR REPLACE VIEW fingerprint_similarities AS
                SELECT
                    f1.model_id AS model_id_1,
                    f2.model_id AS model_id_2,
                    m1.model_name AS model_name_1,
                    m2.model_name AS model_name_2,
                    f1.fingerprint_type,
                    list_cosine_similarity(f1.fingerprint_vector, f2.fingerprint_vector) AS cosine_similarity,
                    1.0 - (list_distance(f1.fingerprint_vector, f2.fingerprint_vector) / 
                           (sqrt(list_sum(list_transform(f1.fingerprint_vector, x -> x * x))) + 
                            sqrt(list_sum(list_transform(f2.fingerprint_vector, x -> x * x))))) AS euclidean_similarity,
                    list_dot_product(f1.fingerprint_vector, f2.fingerprint_vector) AS dot_product,
                    list_sum(list_transform(list_zip(f1.fingerprint_vector, f2.fingerprint_vector), x -> abs(x[1] - x[2]))) AS l1_distance,
                    1.0 - (list_sum(list_transform(list_zip(f1.fingerprint_vector, f2.fingerprint_vector), x -> abs(x[1] - x[2]))) / 
                           list_sum(list_transform(list_zip(f1.fingerprint_vector, f2.fingerprint_vector), x -> x[1] + x[2]))) AS l1_similarity
                FROM
                    fingerprints AS f1
                JOIN
                    fingerprints AS f2
                    ON f1.model_id < f2.model_id AND f1.fingerprint_type = f2.fingerprint_type
                JOIN
                    models AS m1 ON f1.model_id = m1.id
                JOIN
                    models AS m2 ON f2.model_id = m2.id;
            """)

            # Create hardware_info table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hardware_info (
                    id INTEGER PRIMARY KEY,
                    cpu_info JSON NOT NULL,
                    memory_info JSON NOT NULL,
                    gpu_info JSON NOT NULL,
                    disk_info JSON NOT NULL,
                    system_info JSON NOT NULL,
                    last_updated TIMESTAMP
                );
            """)

            # Table to keep track of sync metadata (e.g., last sync timestamps)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_metadata (
                    key TEXT PRIMARY KEY,
                    value TIMESTAMP
                );
            """)

    @staticmethod
    def is_registry_setup(local_db_path: str = "local_registry.duckdb") -> bool:
        """
        Check if the local registry is already set up.

        Args:
            local_db_path: Path to the local DuckDB database file

        Returns:
            True if the registry exists and has the required tables, False otherwise
        """
        # Check if the database file exists
        if not os.path.exists(local_db_path):
            return False

        try:
            # Connect to database and check for required tables
            with duckdb.connect(local_db_path) as conn:
                # Check for all required tables
                required_tables = [
                    "models",
                    "model_sources",
                    "fingerprints",
                    "hardware_info",
                    "sync_metadata",
                ]

                # Query the table information
                result = conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
                ).fetchall()

                existing_tables = [row[0] for row in result]

                # Check if all required tables exist
                return all(table in existing_tables for table in required_tables)
        except Exception as e:
            logger.error(f"Error checking if registry is setup: {e}")
            return False

    @staticmethod
    def setup_local_registry(
        local_db_path: str = "local_registry.duckdb", database_url: Optional[str] = None
    ) -> bool:
        """
        Set up the local registry:
        - Create the DuckDB database and all tables
        - Gather and save hardware info
        - Optionally test global registry connection
        """
        try:
            # First check if registry is already set up
            if LocalRegistryInterface.is_registry_setup(local_db_path):
                logger.info(f"Local registry at {local_db_path} is already set up")
                return True

            # Create the database directory if it doesn't exist
            db_dir = os.path.dirname(local_db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

            # Create all tables and sequences
            LocalRegistryInterface.create_local_registry_tables(local_db_path)

            logger.info(f"Successfully initialized DuckDB database at {local_db_path}")

            # Gather and save hardware info
            LocalRegistryInterface.refresh_hardware_info(local_db_path)

            # Test connection to global registry if provided
            if database_url:
                try:
                    global_registry = RegistryInterface(database_url)
                    global_registry.count_models()
                    logger.info("Successfully connected to global registry")
                except Exception as e:
                    logger.warning(f"Could not connect to global registry: {e}")
                    logger.warning(
                        "You will need to set up DATABASE_URL with a valid connection string."
                    )

            return True
        except Exception as e:
            logger.error(f"Error initializing registry: {e}")
            return False

    @staticmethod
    def refresh_hardware_info(local_db_path: str):
        """Refresh hardware information in the local registry (can be called after setup)."""
        try:
            hardware_info = HardwareProfiler.get_local_hardware_info()
            hardware_dict = hardware_info.to_dict()
            current_time = datetime.now()
            hardware_id = 1
            with duckdb.connect(local_db_path) as conn:
                existing = conn.execute(
                    "SELECT id FROM hardware_info WHERE id = ?", (hardware_id,)
                ).fetchone()
                if existing:
                    conn.execute(
                        """
                        UPDATE hardware_info SET
                            cpu_info = ?, memory_info = ?, gpu_info = ?,
                            disk_info = ?, system_info = ?, last_updated = ?
                        WHERE id = ?
                        """,
                        (
                            json.dumps(hardware_dict["cpu"]),
                            json.dumps(hardware_dict["memory"]),
                            json.dumps(hardware_dict["gpu"]),
                            json.dumps(hardware_dict["disk"]),
                            json.dumps(hardware_dict["system"]),
                            current_time,
                            hardware_id,
                        ),
                    )
                    logger.info(
                        f"Refreshed hardware_info for id {hardware_id} in local registry."
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO hardware_info (
                            id, cpu_info, memory_info, gpu_info, disk_info, system_info, last_updated
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            hardware_id,
                            json.dumps(hardware_dict["cpu"]),
                            json.dumps(hardware_dict["memory"]),
                            json.dumps(hardware_dict["gpu"]),
                            json.dumps(hardware_dict["disk"]),
                            json.dumps(hardware_dict["system"]),
                            current_time,
                        ),
                    )
                    logger.info(
                        f"Inserted new hardware_info with id {hardware_id} into local registry."
                    )
        except Exception as e:
            logger.error(f"Failed to refresh hardware info: {e}")

    # ============= Private Methods =============

    def _get_local_connection(self):
        """
        Get a connection to the local DuckDB database.

        Returns:
            duckdb.DuckDBPyConnection: Connection to the local DuckDB database
        """
        return duckdb.connect(self.local_db_path)

    def _get_local_hardware_info(self) -> HardwareInfo:
        """
        Gather information about the hardware available on the machine.

        Returns:
            HardwareInfo object containing hardware information
        """
        return HardwareProfiler.get_local_hardware_info()

    def _update_hardware_info(self):
        """Update hardware information in the local registry."""
        hardware_info = self._get_local_hardware_info()
        hardware_dict = hardware_info.to_dict()
        current_time = datetime.now()
        hardware_id = 1  # Assuming a single hardware profile entry with id=1

        with self._get_local_connection() as conn:
            # Check if entry exists
            existing = conn.execute(
                "SELECT id FROM hardware_info WHERE id = ?", (hardware_id,)
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE hardware_info SET
                        cpu_info = ?, memory_info = ?, gpu_info = ?,
                        disk_info = ?, system_info = ?, last_updated = ?
                    WHERE id = ?
                    """,
                    (
                        json.dumps(hardware_dict["cpu"]),
                        json.dumps(hardware_dict["memory"]),
                        json.dumps(hardware_dict["gpu"]),
                        json.dumps(hardware_dict["disk"]),
                        json.dumps(hardware_dict["system"]),
                        current_time,
                        hardware_id,
                    ),
                )
                logger.info(
                    f"Updated hardware_info for id {hardware_id} in local registry."
                )
            else:
                conn.execute(
                    """
                    INSERT INTO hardware_info (
                        id, cpu_info, memory_info, gpu_info, disk_info, system_info, last_updated
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        hardware_id,
                        json.dumps(hardware_dict["cpu"]),
                        json.dumps(hardware_dict["memory"]),
                        json.dumps(hardware_dict["gpu"]),
                        json.dumps(hardware_dict["disk"]),
                        json.dumps(hardware_dict["system"]),
                        current_time,
                    ),
                )
                logger.info(
                    f"Inserted new hardware_info with id {hardware_id} into local registry."
                )

    # ============= Sync-Tracking Helper Methods =============

    def _check_for_similar_fingerprints(self, model_id: int) -> List[int]:
        """
        Check for similar fingerprints in the local registry.

        Returns:
            List of model IDs that are similar to the given model
        """
        similar_models = []

        # Get all fingerprints from global registry
        global_fingerprints = self.global_registry.get_all_fingerprints(model_id)
        if not global_fingerprints:
            raise ValueError(
                f"No fingerprints found for model {model_id} in global registry"
            )

        # Get similarity metric
        similarity_metric = get_similarity_metric("l1")

        # Check for similar fingerprints in local registry
        for glb_fingerprint_type, glb_fingerprint_object in global_fingerprints.items():
            glb_fingerprint_vector = glb_fingerprint_object.get("vector")

            # Skip if global fingerprint vector is missing
            if glb_fingerprint_vector is None:
                raise ValueError(
                    f"Missing fingerprint vector for global model {model_id} (type={glb_fingerprint_type})"
                )

            # Get all fingerprints of the same type from local registry
            lcl_fingerprints = self.get_all_fingerprints_by_type(glb_fingerprint_type)

            logger.debug(f"Local Fingerprints: {lcl_fingerprints}")

            for fp_dict in lcl_fingerprints:
                lcl_model_id = fp_dict["model_id"]
                lcl_vector = fp_dict["vector"]
                # Ensure local vector exists
                if lcl_vector is None:
                    logger.warning(
                        f"Missing fingerprint vector for local model {lcl_model_id} (type={glb_fingerprint_type})"
                    )
                    continue

                # Calculate similarity using the metric
                similarity = similarity_metric.compute(
                    np.array(glb_fingerprint_vector), np.array(lcl_vector)
                )

                # If similarity is above threshold, models are considered the same
                logger.debug(f"Similarity score: {similarity}")
                if similarity > FP_SIM_THRESHOLD_L1:
                    logger.info(
                        f"Found similar model {lcl_model_id} in local registry for fingerprint type {glb_fingerprint_type}"
                    )
                    logger.info(f"Similarity score: {similarity}")
                    similar_models.append(lcl_model_id)

        return similar_models

    def _add_model_to_local_registry(
        self, global_model_id: int, model_dict: Dict
    ) -> Optional[int]:
        """
        Add a model to the local DuckDB registry.
        """
        try:
            with self._get_local_connection() as conn:
                current_time = datetime.now()
                # Use global model's created_at if available, else current time.
                model_created_at = model_dict.get("created_at", current_time)
                # last_updated in the local DB will be current_time, as it's just been added/updated.
                # The global model's last_updated is for reference or decision-making before this point.

                # Generate canonical ID from model name and global ID
                canonical_id = generate_canonical_id(
                    model_dict["model_name"], global_model_id
                )

                cursor = conn.execute(
                    """
                    INSERT INTO models (
                        id, canonical_id, model_maker, model_name, params_count, context_length, quantization, license, created_at, last_updated
                    ) VALUES (nextval('model_id_seq'), ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                """,
                    (
                        canonical_id,
                        model_dict["model_maker"],
                        model_dict["model_name"],
                        model_dict["params_count"],
                        model_dict.get("context_length"),
                        model_dict["quantization"],
                        model_dict.get("license"),
                        model_created_at,
                        current_time,
                    ),
                )
                local_model_id = cursor.fetchone()[0]
                self._update_model_sources(
                    local_model_id, model_dict.get("sources", []), current_time
                )
                self._add_model_fingerprints(
                    local_model_id, global_model_id, current_time
                )
            logger.info(
                f"Successfully added model {local_model_id} (canonical_id: '{canonical_id}', name: '{model_dict.get('model_name')}') to local registry."
            )
            return local_model_id

        except Exception as e:
            logger.error(f"Failed to add model to local registry: {str(e)}")
            return None

    def _update_model_properties(
        self,
        local_model_id: int,
        model_properties: Dict,
        current_time: datetime,
        conn=None,
    ):
        """Update the properties of a model in the local registry.

        Args:
            local_model_id: Integer ID of the local model whose properties we are updating.
            model_properties: Dictionary of model properties to update.
            current_time: Timestamp to use for last_updated when not provided.
            conn: Optional database connection to use (if None, creates a new connection).
        """
        try:

            def _do_update(conn):
                # Generate new canonical ID if we have the necessary info
                # The global_model_id should be in the model_properties as 'id' (from global registry)
                global_model_id = model_properties.get("id")
                if global_model_id and model_properties.get("model_name"):
                    canonical_id = generate_canonical_id(
                        model_properties["model_name"], int(global_model_id)
                    )

                    conn.execute(
                        """
                        UPDATE models 
                        SET canonical_id = ?, model_maker = ?, model_name = ?, params_count = ?, 
                            context_length = ?, quantization = ?, license = ?, last_updated = ? 
                        WHERE id = ?
                    """,
                        (
                            canonical_id,
                            model_properties["model_maker"],
                            model_properties["model_name"],
                            model_properties["params_count"],
                            model_properties.get("context_length"),
                            model_properties["quantization"],
                            model_properties.get("license"),
                            current_time,
                            local_model_id,
                        ),
                    )
                else:
                    # Update without canonical_id if we don't have the necessary info
                    conn.execute(
                        """
                        UPDATE models 
                        SET model_maker = ?, model_name = ?, params_count = ?, 
                            context_length = ?, quantization = ?, license = ?, last_updated = ? 
                        WHERE id = ?
                    """,
                        (
                            model_properties["model_maker"],
                            model_properties["model_name"],
                            model_properties["params_count"],
                            model_properties.get("context_length"),
                            model_properties["quantization"],
                            model_properties.get("license"),
                            current_time,
                            local_model_id,
                        ),
                    )

            if conn is None:
                with self._get_local_connection() as conn:
                    _do_update(conn)
            else:
                _do_update(conn)

        except Exception as e:
            logger.error(
                f"Failed to update model properties for model {local_model_id}: {e}"
            )
            raise

    def _update_model_sources(
        self,
        local_model_id: int,
        sources: List[Dict],
        current_time: datetime,
        conn=None,
    ):
        """Delete existing sources for `local_model_id` and insert the provided list.

        Args:
            local_model_id: Integer ID of the local model whose sources we are updating.
            sources: Iterable of source dictionaries (as returned from the registry).
            current_time: Timestamp to use for created_at / last_updated when not provided.
            conn: Optional database connection to use (if None, creates a new connection).
        """

        def _do_update(conn):
            # Insert new sources (deletion handled at transaction level)
            # Insert new ones
            for source in sources:
                if not isinstance(source, dict):
                    logger.error(
                        f"Invalid source format for model {local_model_id}: {source}"
                    )
                    continue

                conn.execute(
                    """
                    INSERT INTO model_sources (
                        id,
                        model_id,
                        source_type,
                        source_identifier,
                        requires_auth,
                        created_at,
                        last_updated
                    ) VALUES (nextval('model_sources_id_seq'), ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        local_model_id,
                        source.get("source_type"),
                        json.dumps(source.get("source_identifier", {})),
                        source.get("requires_auth", False),
                        source.get("created_at", current_time),
                        current_time,
                    ),
                )

        if conn is None:
            with self._get_local_connection() as conn:
                _do_update(conn)
        else:
            _do_update(conn)

    def _add_model_fingerprints(
        self,
        local_model_id: int,
        global_model_id: int,
        current_time: datetime,
        conn=None,
    ):
        """
        Add fingerprints to the local registry.

        Args:
            local_model_id: ID of the local model to add fingerprints to.
            global_model_id: ID of the global model to copy fingerprints from.
            current_time: Timestamp to use for created_at / last_updated when not provided.
            conn: Optional database connection to use (if None, creates a new connection).

        """
        glb_fingerprints = self.global_registry.get_all_fingerprints(global_model_id)

        def _do_update(conn):
            # Insert new fingerprints (deletion handled at transaction level)
            # Insert new fingerprints
            for (
                glb_fingerprint_type,
                glb_fingerprint_object,
            ) in glb_fingerprints.items():
                # Convert numpy array or list to list for DuckDB
                glb_fingerprint_vector = glb_fingerprint_object.get("vector")
                if isinstance(glb_fingerprint_vector, np.ndarray):
                    glb_fingerprint_vector = glb_fingerprint_vector.tolist()

                conn.execute(
                    """
                    INSERT INTO fingerprints (
                        id,
                        model_id, 
                        fingerprint_type,
                        fingerprint_vector, 
                        fingerprint_config,
                        created_at,
                        last_updated
                    ) VALUES (nextval('fingerprint_id_seq'), ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        local_model_id,
                        glb_fingerprint_type,
                        glb_fingerprint_vector,
                        json.dumps(glb_fingerprint_object.get("config", {})),
                        current_time,
                        current_time,
                    ),
                )

        if conn is None:
            with self._get_local_connection() as conn:
                _do_update(conn)
        else:
            _do_update(conn)

    # The new unified sync method
    def sync_models_from_global(
        self,
        filters: Optional[ModelFilterCriteria] = None,
        use_last_sync_time: bool = True,
    ) -> Optional[Tuple[int, int]]:
        """
        Synchronize models from the global registry to the local DuckDB registry.
        Can be filtered and can use the last sync time for incremental updates.

        Args:
            filters: ModelFilterCriteria object with filter conditions.
            use_last_sync_time: If True, only sync models updated since the last sync.

        Returns:
            Tuple (success_count, processed_count) or None if an error occurred.
        """
        try:
            effective_filters = ModelFilterCriteria()
            if filters:
                effective_filters = ModelFilterCriteria(**filters.to_dict())

            if use_last_sync_time:
                last_sync_time_for_query = self._get_sync_value("models_last_sync")
                if last_sync_time_for_query:
                    # This ensures incremental sync logic takes precedence for updated_since
                    effective_filters.updated_since = last_sync_time_for_query

            models_to_sync = self.global_registry.find_models(filters=effective_filters)
            model_ids_to_sync = [model.model_info["id"] for model in models_to_sync]
            total_models_to_process = len(model_ids_to_sync)

            # Log the sync details
            filter_str = (
                effective_filters.to_filter_string()
                if not effective_filters.is_empty()
                else "all models (or all since last sync if incremental)"
            )
            logger.info(
                f"Syncing models from global registry. Effective filters: {filter_str}"
            )
            logger.info(
                f"Found {total_models_to_process} models matching criteria from global registry."
            )

            success_count = 0
            processed_count = 0
            start_time = datetime.now()

            for model_id in model_ids_to_sync:
                processed_count += 1
                status, local_model_id_or_none = self.copy_model_from_global(model_id)
                if status in ["added", "updated", "up_to_date"]:
                    success_count += 1
                    logger.debug(
                        f"Successfully processed model {model_id} ({processed_count}/{total_models_to_process}), status: {status}"
                    )
                else:
                    logger.debug(
                        f"Model {model_id} sync skipped or failed with status '{status}' ({processed_count}/{total_models_to_process})."
                    )

            end_time = datetime.now()
            duration = end_time - start_time

            logger.info(
                f"Completed model sync. Processed {processed_count} models. Synced/updated/verified {success_count} models."
            )
            logger.info(
                f"Sync completed at {end_time}, took {duration.total_seconds():.2f} seconds"
            )

            # Always update the general last sync time for this registry instance
            self._set_sync_value("models_last_sync", end_time)

            return (success_count, processed_count)

        except Exception as e:
            logger.error(f"Failed to sync models from global registry: {str(e)}")
            return None

    def copy_model_from_global(self, global_model_id: int) -> tuple[str, Optional[int]]:
        """
        Copy or update a model from the global registry to the local DuckDB registry.

        Args:
            global_model_id: ID of the model to copy/update.

        Returns:
            tuple: A tuple containing (status, local_model_id) where:
                  status: String indicating the result ("added", "updated", "up_to_date", "not_found", "error")
                  local_model_id: ID of the model in the local registry if applicable, None otherwise
        """
        try:
            glb_model_to_add = self.global_registry.find_model(global_model_id)
            if not glb_model_to_add:
                logger.warning(f"Model {global_model_id} not found in global registry.")
                return ("not_found", None)

            model_properties = glb_model_to_add.to_dict()
            # Assuming global model_dict contains 'created_at' and 'last_updated'
            global_last_updated = model_properties.get("last_updated")

            if not all(
                key in model_properties
                for key in [
                    "model_maker",
                    "model_name",
                    "params_count",
                    "quantization",
                ]
            ):
                logger.error(
                    f"Global model {global_model_id} (name: {model_properties.get('model_name')}) is missing required fields."
                )
                return ("error", None)

            similar_models = self._check_for_similar_fingerprints(global_model_id)

            if len(similar_models) > 0:
                if len(similar_models) > 1:
                    raise ValueError(
                        f"Multiple similar models found by fingerprint in local registry for global model {global_model_id}."
                    )

                local_model_id = similar_models[0]

                with self._get_local_connection() as conn_check:
                    local_model_db_data = conn_check.execute(
                        "SELECT last_updated FROM models WHERE id = ?",
                        (local_model_id,),
                    ).fetchone()
                local_db_last_updated = (
                    local_model_db_data[0] if local_model_db_data else None
                )

                # If global model is not newer than local model, skip update.
                # This relies on global_last_updated being accurate.
                if global_last_updated and local_db_last_updated:
                    # Handle timezone comparison issue by ensuring both are naive or both are aware
                    # Convert to comparable datetime types
                    if (
                        global_last_updated.tzinfo is not None
                        and local_db_last_updated.tzinfo is None
                    ):
                        # Global has tz, local doesn't
                        local_db_last_updated = local_db_last_updated.replace(
                            tzinfo=global_last_updated.tzinfo
                        )
                    elif (
                        global_last_updated.tzinfo is None
                        and local_db_last_updated.tzinfo is not None
                    ):
                        # Local has tz, global doesn't
                        global_last_updated = global_last_updated.replace(
                            tzinfo=local_db_last_updated.tzinfo
                        )

                    # Now the comparison should work
                    if global_last_updated <= local_db_last_updated:
                        logger.debug(
                            f"Local model {local_model_id} (from global {global_model_id}) is already up-to-date. Global: {global_last_updated}, Local DB: {local_db_last_updated}. Skipping update."
                        )
                        return ("up_to_date", local_model_id)  # Already up to date

                logger.debug(
                    f"Updating existing local model {local_model_id} from global model {global_model_id} (Global last_updated: {global_last_updated})."
                )
                try:
                    current_time = datetime.now()

                    # Do all updates in a single transaction to avoid foreign key constraint issues
                    with self._get_local_connection() as conn:
                        # First delete existing sources and fingerprints to avoid foreign key constraints
                        logger.debug(
                            "Deleting existing model sources and fingerprints..."
                        )
                        conn.execute(
                            "DELETE FROM model_sources WHERE model_id = ?",
                            (local_model_id,),
                        )
                        conn.execute(
                            "DELETE FROM fingerprints WHERE model_id = ?",
                            (local_model_id,),
                        )

                        logger.debug("Updating model properties...")
                        self._update_model_properties(
                            local_model_id, model_properties, current_time, conn
                        )

                        logger.debug("Updating model sources...")
                        self._update_model_sources(
                            local_model_id,
                            model_properties.get("sources", []),
                            current_time,
                            conn,
                        )

                        logger.debug("Updating model fingerprints...")
                        self._add_model_fingerprints(
                            local_model_id, global_model_id, current_time, conn
                        )

                    return ("updated", local_model_id)

                except Exception as e:
                    import traceback

                    print("TRACEBACK***\n\n", traceback.format_exc(), "\n\n***")
                    logger.error(
                        f"Failed to update local model {local_model_id} (from global {global_model_id}): {str(e)}"
                    )
                    return ("error", None)
            else:
                local_model_id = self._add_model_to_local_registry(
                    global_model_id, model_properties
                )
                return ("added", local_model_id) if local_model_id else ("error", None)

        except Exception as e:
            logger.error(
                f"Failed to copy/update model {global_model_id} from global registry: {str(e)}"
            )
            return ("error", None)

    def get_saved_hardware_info(self) -> HardwareInfo:
        """
        Get the current hardware information from the local registry.

        Returns:
            HardwareInfo object containing hardware information
        """
        hardware_id = 1  # Assuming a single hardware profile entry
        with self._get_local_connection() as conn:
            row = conn.execute(
                """
                SELECT cpu_info, memory_info, gpu_info, disk_info, system_info, last_updated
                FROM hardware_info
                WHERE id = ?
            """,
                (hardware_id,),
            ).fetchone()

            if row is None:
                logger.warning(
                    "No saved hardware info found in local DB. Returning current system hardware info."
                )
                # Fetch current hardware info, update the database, and then return it.
                # This ensures that the DB is populated on the first call if it somehow wasn't during init.
                LocalRegistryInterface.refresh_hardware_info(self.local_db_path)
                # Now try fetching again
                row = conn.execute(
                    """
                    SELECT cpu_info, memory_info, gpu_info, disk_info, system_info, last_updated
                    FROM hardware_info
                    WHERE id = ?
                """,
                    (hardware_id,),
                ).fetchone()
                if row is None:  # Should not happen if _update_hardware_info worked
                    logger.error(
                        "Failed to retrieve hardware info even after attempting an update."
                    )
                    # Fallback to returning live info directly without saving, though this indicates an issue.
                    return self._get_local_hardware_info()

            # DuckDB returns JSON type as string, so we need to parse it.
            return HardwareInfo(
                cpu=json.loads(row[0]),
                memory=json.loads(row[1]),
                gpu=json.loads(row[2]),
                disk=json.loads(row[3]),
                system=json.loads(row[4]),
                last_updated=row[5],
            )

    def get_model_id_from_source_id(self, source_id: str) -> str:
        """Retrieve the model_id associated with a given source_id."""
        try:
            with self._get_local_connection() as conn:
                result = conn.execute(
                    "SELECT model_id FROM model_sources WHERE id = ?",
                    (source_id,),
                ).fetchone()
                if result:
                    return str(result[0])
                else:
                    return None
        except Exception as e:
            logger.error(f"Error fetching model_id for source_id {source_id}: {e}")
            return None

    def find_model_by_canonical_id(self, canonical_id: str) -> Optional[Model]:
        """
        Find a model in the local registry by its canonical ID.

        Args:
            canonical_id: Canonical ID of the model to find (e.g., "microsoft/phi-3-mini_42")

        Returns:
            Model object if found, None otherwise
        """
        try:
            with self._get_local_connection() as conn:
                # Get model data using canonical_id
                cursor = conn.execute(
                    """
                    SELECT *
                    FROM models
                    WHERE canonical_id = ?
                """,
                    (canonical_id,),
                )
                model_data_tuple = cursor.fetchone()

                if not model_data_tuple:
                    return None

                # Convert tuple to Model object
                columns = [desc[0] for desc in cursor.description]
                model_data = dict(zip(columns, model_data_tuple))
                local_model_id = model_data["id"]

                # Get sources for this model
                sources_cursor = conn.execute(
                    """
                    SELECT source_type, source_identifier, requires_auth, created_at, last_updated
                    FROM model_sources
                    WHERE model_id = ?
                """,
                    (local_model_id,),
                )
                sources_data = sources_cursor.fetchall()
                sources = []
                for source_row in sources_data:
                    source_dict = {
                        "source_type": source_row[0],
                        "source_identifier": json.loads(source_row[1])
                        if source_row[1]
                        else {},
                        "requires_auth": source_row[2],
                        "created_at": source_row[3],
                        "last_updated": source_row[4],
                    }
                    sources.append(source_dict)

                # Build model_info dict
                model_info = {
                    "id": model_data["id"],
                    "canonical_id": model_data.get("canonical_id"),
                    "model_maker": model_data["model_maker"],
                    "model_name": model_data["model_name"],
                    "params_count": model_data["params_count"],
                    "context_length": model_data["context_length"],
                    "quantization": model_data["quantization"],
                    "license": model_data["license"],
                    "created_at": model_data["created_at"],
                    "last_updated": model_data["last_updated"],
                    "sources": sources,
                }

                return Model(
                    name=model_data["model_name"],
                    model_info=model_info,
                )

        except Exception as e:
            logger.error(f"Error finding model by canonical_id {canonical_id}: {e}")
            return None

    def find_model(self, model_id) -> Optional[Model]:
        """
        Find a model in the local registry by ID (supports both local numeric IDs and canonical IDs).

        Args:
            model_id: ID of the model to find (numeric local ID or canonical ID)

        Returns:
            Model object if found, None otherwise
        """
        # Convert to string for consistent handling
        model_id_str = str(model_id)

        try:
            with self._get_local_connection() as conn:
                # Single query that can handle both integer IDs and canonical IDs
                # Try to convert to int for numeric ID comparison, otherwise use as string
                try:
                    # Try to convert to int - handle floats that are whole numbers
                    if isinstance(model_id, float):
                        if model_id.is_integer():
                            numeric_id = int(model_id)
                        else:
                            numeric_id = None
                    else:
                        numeric_id = int(model_id_str)
                except ValueError:
                    numeric_id = None

                # Query using OR condition to check both id and canonical_id
                if numeric_id is not None:
                    cursor = conn.execute(
                        """
                        SELECT *
                        FROM models
                        WHERE id = ?
                    """,
                        (numeric_id,),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT *
                        FROM models
                        WHERE canonical_id = ?
                    """,
                        (model_id_str,),
                    )

                model_data_tuple = cursor.fetchone()

                if not model_data_tuple:
                    return None

                # Dynamically get column names from cursor description
                model_columns = [desc[0] for desc in cursor.description]
                model_data = dict(zip(model_columns, model_data_tuple))

                # Get sources
                sources_cursor = conn.execute(
                    """
                    SELECT *
                    FROM model_sources
                    WHERE model_id = ?
                """,
                    (model_data["id"],),
                )
                sources_tuples = sources_cursor.fetchall()
                source_columns = [desc[0] for desc in sources_cursor.description]
                sources_list = [
                    dict(zip(source_columns, s_tuple)) for s_tuple in sources_tuples
                ]

                # Create model info dictionary using string keys from model_data
                model_info = {
                    "id": model_data.get("id"),
                    "canonical_id": model_data.get("canonical_id"),
                    "model_maker": model_data.get("model_maker"),
                    "model_name": model_data.get("model_name"),
                    "params_count": model_data.get("params_count"),
                    "context_length": model_data.get("context_length"),
                    "quantization": model_data.get("quantization"),
                    "license": model_data.get("license"),
                    "created_at": model_data.get("created_at"),
                    "last_updated": model_data.get("last_updated"),
                    "sources": [
                        {
                            "source_id": str(s.get("id")),
                            "source_type": s.get("source_type"),
                            "source_identifier": json.loads(s.get("source_identifier"))
                            if isinstance(s.get("source_identifier"), str)
                            else s.get("source_identifier"),
                            "requires_auth": s.get("requires_auth"),
                            "created_at": s.get("created_at"),
                            "last_updated": s.get("last_updated"),
                        }
                        for s in sources_list
                    ],
                }

                # Create and return Model object
                return Model(name=model_data["model_name"], model_info=model_info)

        except Exception as e:
            logger.error(f"Error finding model {model_id}: {e}")
            return None

    def count_models(self) -> int:
        """
        Count the total number of models in the local registry.

        Returns:
            int: Total number of models
        """
        with self._get_local_connection() as conn:
            result = conn.execute("""
                SELECT COUNT(*)
                FROM models
            """).fetchone()
            return result[0] if result else 0

    def find_models(
        self,
        filters: Optional[ModelFilterCriteria] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Model]:
        """
        Find models in the local registry that match the given criteria.

        Args:
            filters: ModelFilterCriteria object with filter conditions.
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of Model objects with their sources and fingerprints
        """

        with self._get_local_connection() as conn:
            # Build the query
            query = """
                SELECT 
                    m.id as model_id,
                    m.canonical_id,
                    m.model_maker,
                    m.model_name,
                    m.params_count,
                    m.context_length,
                    m.quantization,
                    m.license,
                    m.created_at,
                    m.last_updated,
                    json_group_array(json_object(
                        'source_id', s.id,
                        'source_type', s.source_type,
                        'source_identifier', s.source_identifier,
                        'requires_auth', s.requires_auth,
                        'created_at', s.created_at,
                        'last_updated', s.last_updated
                    )) as sources
                FROM models m
                LEFT JOIN model_sources s ON m.id = s.model_id
                WHERE 1=1
            """
            params = []

            # Add filters if provided
            if filters and not filters.is_empty():
                filter_conditions, filter_params = filters.to_sql_filters(
                    table_alias="m", placeholder_style="?"
                )
                query += f" AND {filter_conditions}"
                params.extend(filter_params)

            query += " GROUP BY m.id, m.canonical_id, m.model_maker, m.model_name, m.params_count, m.context_length, m.quantization, m.license, m.created_at, m.last_updated"

            # Add pagination
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)

            # Execute query
            # Correctly get column names for mapping
            cursor = conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            # Convert results to Model objects
            models = []
            for row_tuple in rows:
                row = dict(zip(columns, row_tuple))
                model_dict = {
                    "id": row["model_id"],
                    "canonical_id": row["canonical_id"],
                    "model_maker": row["model_maker"],
                    "model_name": row["model_name"],
                    "params_count": row["params_count"],
                    "context_length": row["context_length"],
                    "quantization": row["quantization"],
                    "license": row["license"],
                    "created_at": row["created_at"],
                    "last_updated": row["last_updated"],
                    "sources": json.loads(row["sources"]) if row["sources"] else [],
                }

                # Create a Model object
                model_obj = Model(name=model_dict["model_name"], model_info=model_dict)
                models.append(model_obj)

            return models

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
        Add an observation for a model in the local registry.

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

        with self._get_local_connection() as conn:
            # Verify model exists
            result = conn.execute(
                "SELECT id FROM models WHERE id = ?", [int(model_id)]
            ).fetchone()

            if not result:
                raise ValueError(
                    f"Model with id {model_id} not found in local registry"
                )

            # Get next ID from sequence
            next_id = conn.execute(
                "SELECT nextval('model_observations_id_seq')"
            ).fetchone()[0]

            # Insert observation
            conn.execute(
                """
                INSERT INTO model_observations 
                (id, model_id, observation, created_by, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                [
                    next_id,
                    int(model_id),
                    observation,
                    created_by,
                    tags if tags else None,
                    json.dumps(metadata) if metadata else None,
                ],
            )

            # Update the parent model's last_updated timestamp
            conn.execute(
                """
                UPDATE models 
                SET last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                [int(model_id)],
            )

            logger.info(
                f"Added observation {next_id} for model {model_id} in local registry"
            )
            return str(next_id)

    def get_model_observations(
        self,
        model_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Get observations for a model from the local registry.

        Args:
            model_id: ID of the model to get observations for
            limit: Maximum number of observations to return
            offset: Number of observations to skip
            tags: Optional list of tags to filter by (returns observations with ANY of the tags)

        Returns:
            List of observation dictionaries
        """
        with self._get_local_connection() as conn:
            query = """
                SELECT 
                    id,
                    model_id,
                    observation,
                    created_at,
                    created_by,
                    tags,
                    metadata
                FROM model_observations
                WHERE model_id = ?
            """
            params = [int(model_id)]

            # Add tag filter if provided
            if tags:
                # DuckDB uses list_has_any for array overlap check
                query += " AND list_has_any(tags, ?)"
                params.append(tags)

            query += " ORDER BY created_at DESC"

            # Add pagination
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)

            cursor = conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description]

            observations = []
            for row in cursor.fetchall():
                obs_dict = dict(zip(columns, row))
                # Parse metadata JSON if present
                if obs_dict.get("metadata"):
                    obs_dict["metadata"] = json.loads(obs_dict["metadata"])
                observations.append(obs_dict)

            return observations

    # ============= Fingerprint Methods =============

    def get_fingerprint(self, model_id, fingerprint_type: str) -> Optional[Dict]:
        """
        Get a fingerprint vector for a model from the local registry.

        Args:
            model_id: ID of the model (can be integer local ID or canonical ID string).
            fingerprint_type: Type of the fingerprint to retrieve.

        Returns:
            A dictionary containing the fingerprint data if found, else None.
        """
        # First, resolve the model_id to a local integer ID
        local_model_id = self._resolve_model_id_to_local_id(model_id)
        if local_model_id is None:
            return None

        with self._get_local_connection() as conn:
            result = conn.execute(
                """
                SELECT fingerprint_vector
                FROM fingerprints
                WHERE model_id = ? AND fingerprint_type = ?
            """,
                (local_model_id, fingerprint_type),
            ).fetchone()

            if result and result[0] is not None:
                # Ensure it's a list of floats if not None
                return (
                    np.array(result[0])
                    if isinstance(result[0], (list, np.ndarray))
                    else None
                )
            return None

    def get_all_fingerprints_by_type(self, fingerprint_type: str) -> List[Dict]:
        """
        Get all fingerprints of a specific type across all models from the local registry.

        Args:
            fingerprint_type: Type of the fingerprints to retrieve.

        Returns:
            A list of dictionaries, each containing fingerprint data for a model.
        """
        with self._get_local_connection() as conn:
            results = conn.execute(
                """
                SELECT model_id, fingerprint_vector, fingerprint_config, created_at, last_updated
                FROM fingerprints
                WHERE fingerprint_type = ?
            """,
                (fingerprint_type,),
            ).fetchall()

            fingerprints = []
            for row in results:
                fingerprints.append(
                    {
                        "model_id": row[0],
                        "fingerprint_type": fingerprint_type,  # Add fingerprint_type to the output
                        "vector": list(row[1])
                        if row[1]
                        else None,  # Convert array to list
                        "config": json.loads(row[2]) if row[2] else {},
                        "created_at": row[3],
                        "last_updated": row[4],
                    }
                )
            return fingerprints

    # ============= Sync-Tracking Helper Methods =============

    def _get_sync_value(self, key: str) -> Optional[datetime]:
        """Return stored sync timestamp for the given key (None if not present)."""
        with self._get_local_connection() as conn:
            result = conn.execute(
                "SELECT value FROM sync_metadata WHERE key = ?", (key,)
            ).fetchone()
            return result[0] if result else None

    def _set_sync_value(self, key: str, value: datetime):
        """Upsert the sync timestamp for the given key."""
        with self._get_local_connection() as conn:
            conn.execute(
                """
                INSERT INTO sync_metadata (key, value)
                VALUES (?, ?)
                ON CONFLICT (key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def _resolve_model_id_to_local_id(self, model_id) -> Optional[int]:
        """
        Resolve a model_id (which could be a local integer ID or canonical ID string) to a local integer ID.

        Args:
            model_id: ID of the model (can be integer local ID or canonical ID string)

        Returns:
            Local integer model ID if found, None otherwise
        """
        # Convert to string for consistent handling
        model_id_str = str(model_id)

        try:
            with self._get_local_connection() as conn:
                # Try to convert to int for numeric ID comparison, otherwise use as string
                try:
                    # Try to convert to int - handle floats that are whole numbers
                    if isinstance(model_id, float):
                        if model_id.is_integer():
                            numeric_id = int(model_id)
                        else:
                            logger.error(
                                f"Invalid model_id format (float not a whole number): {model_id}"
                            )
                            return None
                    else:
                        numeric_id = int(model_id_str)
                except ValueError:
                    numeric_id = None

                # Query using OR condition to check both id and canonical_id
                if numeric_id is not None:
                    result = conn.execute(
                        "SELECT id FROM models WHERE id = ?",
                        (numeric_id,),
                    ).fetchone()
                else:
                    result = conn.execute(
                        "SELECT id FROM models WHERE canonical_id = ?",
                        (model_id_str,),
                    ).fetchone()

                if result:
                    return result[0]
                else:
                    logger.error(f"Model with ID {model_id} not found")
                    return None

        except Exception as e:
            logger.error(f"Error resolving model_id {model_id}: {e}")
            return None

    def get_model_similarities(
        self,
        model_ids: List,
        fingerprint_type: Optional[str] = None,
        threshold: Optional[float] = None,
        similarity_metric: str = "l1_similarity",
    ) -> List[Dict]:
        """
        Get similarity scores for specific model pairs from the fingerprint_similarities view.

        Args:
            model_ids: A list of two or more model IDs to compare (can be integer local IDs or canonical ID strings).
            fingerprint_type: The specific type of fingerprint to compare.
            threshold: An optional similarity score to filter results.
            similarity_metric: Which similarity metric to use for threshold filtering
                               ('l1_similarity', 'euclidean_similarity', 'dot_product', 'cosine_similarity')

        Returns:
            A list of dictionaries, each containing the similarity scores for a model pair.
        """
        if len(model_ids) < 2:
            raise ValueError(
                "At least two model IDs are required to find similarities."
            )

        # Resolve all model_ids to local integer IDs
        local_model_ids = []
        for model_id in model_ids:
            local_id = self._resolve_model_id_to_local_id(model_id)
            if local_id is not None:
                local_model_ids.append(local_id)
            else:
                logger.warning(f"Could not resolve model_id {model_id} to local ID")

        if len(local_model_ids) < 2:
            logger.warning("Not enough valid model IDs found after resolution")
            return []

        # Build the query to find pairs within the specified model IDs
        placeholders = ",".join("?" * len(local_model_ids))
        query = f"""
            SELECT * FROM fingerprint_similarities 
            WHERE (model_id_1 IN ({placeholders}) AND model_id_2 IN ({placeholders}))
        """
        params = local_model_ids + local_model_ids

        if fingerprint_type:
            query += " AND fingerprint_type = ?"
            params.append(fingerprint_type)

        if threshold is not None:
            # All metrics are now similarity metrics, higher is better
            query += f" AND {similarity_metric} >= ?"
            params.append(threshold)

        with self._get_local_connection() as conn:
            results = conn.execute(query, params).fetchall()
            columns = [desc[0] for desc in conn.description]

        return [dict(zip(columns, row)) for row in results]

    def find_similar_models(
        self,
        model_id,
        fingerprint_type: Optional[str] = None,
        threshold: float = 0.99,
        similarity_metric: str = "l1_similarity",
    ) -> List[Dict]:
        """
        Find all models with a similarity score above a given threshold to a specific model.

        Args:
            model_id: The ID of the model to find similar models for (can be integer local ID or canonical ID string).
            fingerprint_type: The specific type of fingerprint to compare.
            threshold: The similarity score threshold.
            similarity_metric: Which similarity metric to use for threshold filtering
                             ('l1_similarity', 'cosine_similarity', 'euclidean_similarity', 'dot_product')

        Returns:
            A list of dictionaries, each representing a similar model and the similarity score.
        """
        # First, resolve the model_id to a local integer ID
        local_model_id = self._resolve_model_id_to_local_id(model_id)
        if local_model_id is None:
            return []

        query = "SELECT * FROM fingerprint_similarities WHERE (model_id_1 = ? OR model_id_2 = ?)"
        params = [local_model_id, local_model_id]

        if fingerprint_type:
            query += " AND fingerprint_type = ?"
            params.append(fingerprint_type)

        # All metrics are now similarity metrics, higher is better
        query += f" AND {similarity_metric} >= ?"
        params.append(threshold)

        with self._get_local_connection() as conn:
            results = conn.execute(query, params).fetchall()
            columns = [desc[0] for desc in conn.description]

        return [dict(zip(columns, row)) for row in results]
