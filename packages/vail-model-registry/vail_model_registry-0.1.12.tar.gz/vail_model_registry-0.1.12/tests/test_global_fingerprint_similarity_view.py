"""
Test suite for Phase 2 Global Registry Similarity Cache functionality.

Tests the materialized view creation, refresh logic, and query methods
for the PostgreSQL-based global registry similarity cache.
"""

import os

import numpy as np
import pytest

from vail.registry.interface import RegistryInterface


def get_connection_string():
    """Get the database connection string for testing."""
    try:
        from vail.utils.env import load_env

        load_env("test")
        return os.getenv("DATABASE_URL")
    except Exception:
        return None


@pytest.fixture
def global_registry():
    """Create a RegistryInterface instance for testing."""
    connection_string = get_connection_string()
    if not connection_string:
        pytest.skip("DATABASE_URL environment variable not set in .env.test")
    if "test" not in connection_string:
        raise ValueError(
            "DATABASE_URL must include 'test' to prevent accidental modifications to production database"
        )

    # Ensure the test database schema is set up
    RegistryInterface.setup_global_registry(connection_string)

    return RegistryInterface(connection_string)


@pytest.fixture
def test_models_and_fingerprints(global_registry):
    """Set up test models and fingerprints for similarity testing."""
    # Clean up any existing test data
    with global_registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {global_registry.schema}.fingerprints WHERE 1=1")
            cur.execute(f"DELETE FROM {global_registry.schema}.model_sources WHERE 1=1")
            cur.execute(f"DELETE FROM {global_registry.schema}.models WHERE 1=1")
            conn.commit()

    # Create test models
    models_data = [
        {
            "model_maker": "test_org",
            "model_name": "test_model_1",
            "params_count": 1000000,
            "quantization": "fp16",
        },
        {
            "model_maker": "test_org",
            "model_name": "test_model_2",
            "params_count": 2000000,
            "quantization": "fp32",
        },
        {
            "model_maker": "test_org",
            "model_name": "test_model_3",
            "params_count": 3000000,
            "quantization": "int8",
        },
    ]

    model_ids = []
    for model_data in models_data:
        model_id = global_registry.add_model(model_data, override_checks=True)
        model_ids.append(int(model_id))

    # Create test fingerprints with known similarity relationships
    fingerprints_data = [
        # Model 1 - fingerprints for different types
        (model_ids[0], "io", np.array([1.0, 2.0, 3.0, 4.0, 5.0]), {"test": "config1"}),
        (
            model_ids[0],
            "weights",
            np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            {"test": "config1"},
        ),
        # Model 2 - similar to model 1 for 'io' type
        (model_ids[1], "io", np.array([1.1, 2.1, 3.1, 4.1, 5.1]), {"test": "config2"}),
        (
            model_ids[1],
            "weights",
            np.array([0.5, 0.6, 0.7, 0.8, 0.9]),
            {"test": "config2"},
        ),
        # Model 3 - different from models 1&2
        (
            model_ids[2],
            "io",
            np.array([10.0, 20.0, 30.0, 40.0, 50.0]),
            {"test": "config3"},
        ),
        (
            model_ids[2],
            "weights",
            np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
            {"test": "config3"},
        ),
    ]

    for model_id, fp_type, fp_vector, fp_config in fingerprints_data:
        global_registry.register_fingerprint(
            model_id=str(model_id),
            fingerprint_type=fp_type,
            fingerprint_vector=fp_vector,
            fingerprint_config=fp_config,
            override_checks=True,
        )

    return {"model_ids": model_ids, "fingerprint_types": ["io", "weights"]}


def test_materialized_view_creation(global_registry):
    """Test that the materialized view is created successfully during setup."""
    with global_registry._get_connection() as conn:
        with conn.cursor() as cur:
            # Check that the materialized view exists
            cur.execute(f"""
                SELECT 1 FROM pg_matviews 
                WHERE schemaname = '{global_registry.schema}' 
                AND matviewname = 'fingerprint_similarities_cache'
            """)
            result = cur.fetchone()
            assert result is not None, (
                f"Materialized view fingerprint_similarities_cache not found in {global_registry.schema} schema"
            )

            # Check that the required indexes exist
            cur.execute(f"""
                SELECT indexname FROM pg_indexes 
                WHERE schemaname = '{global_registry.schema}' 
                AND tablename = 'fingerprint_similarities_cache'
            """)
            indexes = [row[0] for row in cur.fetchall()]

            expected_indexes = [
                f"idx_{global_registry.schema}_fingerprint_similarities_cache_model_ids",
                f"idx_{global_registry.schema}_fingerprint_similarities_cache_fingerprint_type",
                f"idx_{global_registry.schema}_fingerprint_similarities_cache_l1_similarity",
            ]

            for expected_index in expected_indexes:
                assert expected_index in indexes, (
                    f"Expected index {expected_index} not found"
                )


def test_similarity_cache_refresh(global_registry, test_models_and_fingerprints):
    """Test the similarity cache refresh functionality."""
    # Test initial refresh (full refresh)
    result = global_registry.refresh_similarity_cache(incremental=False)

    assert result["status"] == "success"
    assert result["schema"] == global_registry.schema
    assert result["incremental"] is False
    assert result["cache_count"] == 6
    assert "refreshed_at" in result
    assert "duration_seconds" in result

    # Test incremental refresh
    result_incremental = global_registry.refresh_similarity_cache(incremental=True)

    assert result_incremental["status"] == "success"
    assert result_incremental["incremental"] is True


def test_get_cached_similarities(global_registry, test_models_and_fingerprints):
    """Test retrieving similarities from the cache."""
    # Refresh the cache first
    global_registry.refresh_similarity_cache(incremental=False)

    model_ids = test_models_and_fingerprints["model_ids"]

    # Test getting all similarities
    all_similarities = global_registry.get_model_similarities()
    assert len(all_similarities) == 6

    # Verify structure of similarity records
    similarity = all_similarities[0]
    required_fields = [
        "model_id_1",
        "model_id_2",
        "model_name_1",
        "model_name_2",
        "fingerprint_type",
        "l1_similarity",
        "euclidean_similarity",
        "dot_product",
        "cosine_similarity",
        "computed_at",
    ]
    for field in required_fields:
        assert field in similarity, (
            f"Required field {field} missing from similarity record"
        )

    # Test filtering by model IDs
    filtered_similarities = global_registry.get_model_similarities(
        model_ids=[model_ids[0], model_ids[1]]
    )
    assert len(filtered_similarities) > 0
    for sim in filtered_similarities:
        assert sim["model_id_1"] in [model_ids[0], model_ids[1]] or sim[
            "model_id_2"
        ] in [model_ids[0], model_ids[1]]

    # Test filtering by fingerprint type
    io_similarities = global_registry.get_model_similarities(fingerprint_type="io")
    assert len(io_similarities) > 0
    for sim in io_similarities:
        assert sim["fingerprint_type"] == "io"

    # Test threshold filtering
    high_similarities = global_registry.get_model_similarities(
        threshold=0.8, similarity_metric="l1_similarity"
    )
    assert len(high_similarities) == 1
    for sim in high_similarities:
        assert sim["l1_similarity"] >= 0.8

    # Test limit
    limited_similarities = global_registry.get_model_similarities(limit=2)
    assert len(limited_similarities) <= 2


def test_find_similar_models(global_registry, test_models_and_fingerprints):
    """Test finding similar models using the cached similarities."""
    # Refresh the cache first
    global_registry.refresh_similarity_cache(incremental=False)

    model_ids = test_models_and_fingerprints["model_ids"]

    # Test finding similar models for the first model
    similar_models = global_registry.find_similar_models(
        model_id=model_ids[0],
        threshold=0.5,  # Use a lower threshold to ensure we get results
        similarity_metric="l1_similarity",
    )

    assert len(similar_models) == 2

    for sim in similar_models:
        # Verify the structure includes helper fields
        assert "similar_model_id" in sim
        assert "similar_model_name" in sim
        assert sim["similar_model_id"] != model_ids[0]  # Should not return self
        assert sim["l1_similarity"] >= 0.5

    # Test filtering by fingerprint type
    io_similar_models = global_registry.find_similar_models(
        model_id=model_ids[0],
        fingerprint_type="io",
        threshold=0.1,  # Very low threshold to get results
    )

    for sim in io_similar_models:
        assert sim["fingerprint_type"] == "io"

    # Test with limit
    limited_similar = global_registry.find_similar_models(
        model_id=model_ids[0], threshold=0.1, limit=1
    )
    assert len(limited_similar) <= 1


def test_similarity_cache_stats(global_registry, test_models_and_fingerprints):
    """Test the similarity cache statistics functionality."""
    # Refresh the cache first
    global_registry.refresh_similarity_cache(incremental=False)

    stats = global_registry.get_similarity_cache_stats()

    # Verify required fields in stats
    required_fields = [
        "schema",
        "total_similarities",
        "unique_models",
        "unique_fingerprint_types",
        "cache_age_seconds",
        "last_computed_at",
    ]
    for field in required_fields:
        assert field in stats, f"Required field {field} missing from stats"

    # Verify data makes sense
    assert stats["schema"] == global_registry.schema
    assert stats["total_similarities"] >= 0
    assert stats["unique_models"] >= 0
    assert stats["unique_fingerprint_types"] >= 0
    assert stats["cache_age_seconds"] is not None
    assert stats["last_computed_at"] is not None

    # Test average similarity scores
    if stats["total_similarities"] > 0:
        assert "average_l1_similarity" in stats
        assert "average_euclidean_similarity" in stats
        assert "average_dot_product" in stats
        assert "average_cosine_similarity" in stats


def test_similarity_metrics_consistency(global_registry, test_models_and_fingerprints):
    """Test that different similarity metrics work consistently."""
    # Refresh the cache first
    global_registry.refresh_similarity_cache(incremental=False)

    model_ids = test_models_and_fingerprints["model_ids"]

    # Test each similarity metric
    metrics = [
        "l1_similarity",
        "euclidean_similarity",
        "dot_product",
        "cosine_similarity",
    ]

    for metric in metrics:
        similarities = global_registry.get_model_similarities(
            model_ids=model_ids[:2], similarity_metric=metric, limit=5
        )

        # Verify results are properly ordered
        if len(similarities) > 1:
            for i in range(len(similarities) - 1):
                assert similarities[i][metric] >= similarities[i + 1][metric]


def test_cache_refresh_error_handling(global_registry):
    """Test error handling in cache refresh operations."""
    # Test with an invalid schema (this should cause an error)
    old_schema = global_registry.schema
    global_registry.schema = "nonexistent_schema"

    try:
        with pytest.raises(Exception):
            global_registry.refresh_similarity_cache()
    finally:
        # Restore original schema
        global_registry.schema = old_schema
