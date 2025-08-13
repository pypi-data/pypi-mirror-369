"""
Test suite for automatic cache refresh functionality.

Tests application-level auto-refresh, database triggers, and scheduled refresh mechanisms.
"""

import os

import numpy as np
import pytest

import vail.fingerprint.metrics as metrics
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

    # Create registry (auto-refresh is now always enabled)
    registry = RegistryInterface(connection_string)

    # Clean up any existing test data
    with registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {registry.schema}.fingerprints")
            cur.execute(f"DELETE FROM {registry.schema}.model_sources")
            cur.execute(f"DELETE FROM {registry.schema}.models")
            conn.commit()

    # Initial cache refresh to start with empty cache
    registry.refresh_similarity_cache(incremental=False)

    return registry


def test_application_level_auto_refresh(global_registry):
    """Test that the application automatically refreshes cache when fingerprints are added."""
    # Check initial cache state
    initial_stats = global_registry.get_similarity_cache_stats()
    assert initial_stats["total_similarities"] == 0

    # Add a model
    model_data = {
        "model_maker": "test_org",
        "model_name": "auto_refresh_test_model_1",
        "params_count": 1000000,
        "quantization": "fp16",
    }
    model_id = global_registry.add_model(model_data, override_checks=True)

    # Add a fingerprint - this should trigger auto-refresh
    fingerprint_vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    fingerprint_config = {"test": "auto_refresh"}

    global_registry.register_fingerprint(
        model_id=model_id,
        fingerprint_type="io",
        fingerprint_vector=fingerprint_vector,
        fingerprint_config=fingerprint_config,
        override_checks=True,
    )

    # Add a second model and fingerprint
    model_data_2 = {
        "model_maker": "test_org",
        "model_name": "auto_refresh_test_model_2",
        "params_count": 2000000,
        "quantization": "fp32",
    }
    model_id_2 = global_registry.add_model(model_data_2, override_checks=True)

    fingerprint_vector_2 = np.array([1.1, 2.1, 3.1, 4.1, 5.1])

    global_registry.register_fingerprint(
        model_id=model_id_2,
        fingerprint_type="io",
        fingerprint_vector=fingerprint_vector_2,
        fingerprint_config=fingerprint_config,
        override_checks=True,
    )

    # Check that cache was automatically refreshed and now contains similarities
    updated_stats = global_registry.get_similarity_cache_stats()
    assert updated_stats["total_similarities"] > 0

    # Verify we can retrieve the similarity
    similarities = global_registry.get_model_similarities(
        model_ids=[int(model_id), int(model_id_2)], fingerprint_type="io"
    )
    assert len(similarities) == 1  # One similarity pair between the two models


def test_cache_refresh_with_single_model(global_registry):
    """Test that cache refresh works correctly with a single model."""
    # Clear the cache
    global_registry.refresh_similarity_cache(incremental=False)
    initial_stats = global_registry.get_similarity_cache_stats()

    # Add model and fingerprint
    model_data = {
        "model_maker": "test_org",
        "model_name": "single_model_test",
        "params_count": 1000000,
        "quantization": "fp16",
    }
    model_id = global_registry.add_model(model_data, override_checks=True)

    fingerprint_vector = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    fingerprint_config = {"test": "single_model"}

    # Register fingerprint - cache will be refreshed automatically
    global_registry.register_fingerprint(
        model_id=model_id,
        fingerprint_type="io",
        fingerprint_vector=fingerprint_vector,
        fingerprint_config=fingerprint_config,
        override_checks=True,
    )

    # Check final stats - should be same since we only have one model (no pairs to compare)
    final_stats = global_registry.get_similarity_cache_stats()
    # With only one model, no new similarities should be created
    assert final_stats["total_similarities"] == initial_stats["total_similarities"]


def test_cache_refresh_basic_functionality(global_registry):
    """Test that cache refresh basic functionality works."""
    # Simple test to verify the registry works without status checking
    assert global_registry.schema in ["dev", "prod"]

    # Test that manual refresh works
    result = global_registry.refresh_similarity_cache(incremental=True)
    assert result["status"] == "success"
    assert "duration_seconds" in result
    assert "cache_count" in result


def test_cache_refresh_error_handling(global_registry):
    """Test error handling in refresh scenarios."""
    # Test with an invalid schema to trigger errors
    old_schema = global_registry.schema
    global_registry.schema = "nonexistent_schema"

    try:
        # This should raise an exception due to invalid schema
        with pytest.raises(Exception):
            global_registry.refresh_similarity_cache(incremental=True)
    finally:
        # Restore original schema
        global_registry.schema = old_schema


def test_automatic_refresh_consistency(global_registry):
    """Test that automatic refresh produces consistent results."""
    # Clear cache to start fresh
    global_registry.refresh_similarity_cache(incremental=False)

    # Add test data
    model_data_1 = {
        "model_maker": "test_org",
        "model_name": "consistency_test_model_1",
        "params_count": 1000000,
        "quantization": "fp16",
    }
    model_id_1 = global_registry.add_model(model_data_1, override_checks=True)

    model_data_2 = {
        "model_maker": "test_org",
        "model_name": "consistency_test_model_2",
        "params_count": 2000000,
        "quantization": "fp32",
    }
    model_id_2 = global_registry.add_model(model_data_2, override_checks=True)

    # Add fingerprints - cache will be automatically refreshed after each registration
    fp_vector_1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    fp_vector_2 = np.array([1.5, 2.5, 3.5, 4.5, 5.5])

    calculated_l1_similarity = metrics.l1_similarity(fp_vector_1, fp_vector_2)

    global_registry.register_fingerprint(
        model_id=model_id_1,
        fingerprint_type="io",
        fingerprint_vector=fp_vector_1,
        fingerprint_config={"test": "consistency"},
        override_checks=True,
    )

    global_registry.register_fingerprint(
        model_id=model_id_2,
        fingerprint_type="io",
        fingerprint_vector=fp_vector_2,
        fingerprint_config={"test": "consistency"},
        override_checks=True,
    )

    # After second fingerprint, should have similarities between the two models
    auto_similarities = global_registry.get_model_similarities(
        model_ids=[int(model_id_1), int(model_id_2)], fingerprint_type="io"
    )

    # Should have exactly one similarity pair
    assert len(auto_similarities) == 1

    # Verify the similarity values are reasonable
    similarity = auto_similarities[0]
    assert similarity["l1_similarity"] == calculated_l1_similarity
