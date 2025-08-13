"""
Test model observations functionality
"""

import logging
import os
from datetime import datetime

import pytest

from vail.registry.interface import RegistryInterface
from vail.registry.local_interface import LocalRegistryInterface
from vail.utils.env import load_env

logger = logging.getLogger(__name__)


@pytest.fixture
def registry():
    """Create a registry interface for testing."""
    load_env("test")
    db_url = os.getenv("DATABASE_URL")
    if db_url and "test" in db_url:
        return RegistryInterface(db_url, use_production=False)
    else:
        logger.warning(
            "DATABASE_URL not configured for test setup or does not contain 'test'. Skipping global registry setup for test_db_utils.py."
        )


@pytest.fixture
def local_registry(tmp_path):
    """Create a local registry interface for testing."""
    load_env()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL not set")

    local_db_path = str(tmp_path / "test_local.duckdb")
    return LocalRegistryInterface(connection_string=db_url, local_db_path=local_db_path)


@pytest.fixture
def sample_model(registry):
    """Create a sample model for testing."""
    model_info = {
        "model_name": f"test_model_observations_{datetime.now().timestamp()}",
        "model_maker": "test_maker",
        "params_count": 1000000,
        "quantization": "fp32",
    }
    model_id = registry.add_model(model_info)

    # Add a source
    source_info = {
        "source_identifier": {"checkpoint": "test/model"},
        "source_type": "huggingface_api",
    }
    registry.add_model_source(model_id, "huggingface_api", source_info)

    return model_id


def test_add_observation_basic(registry, sample_model):
    """Test adding a basic observation."""
    observation_id = registry.add_model_observation(
        model_id=sample_model,
        observation="This model shows good performance on text generation tasks",
    )

    assert observation_id is not None
    assert observation_id.isdigit()

    # Verify the observation was actually stored
    observations = registry.get_model_observations(sample_model)
    assert len(observations) == 1
    assert observations[0]["id"] == int(observation_id)
    assert (
        observations[0]["observation"]
        == "This model shows good performance on text generation tasks"
    )


def test_add_observation_with_metadata(registry, sample_model):
    """Test adding an observation with all optional fields."""
    test_metadata = {"batch_size": 32, "peak_memory_gb": 24.5, "gpu_model": "A100"}
    test_tags = ["performance", "memory", "issue"]

    observation_id = registry.add_model_observation(
        model_id=sample_model,
        observation="Model exhibits high memory usage during batch inference",
        created_by="test_user@example.com",
        tags=test_tags,
        metadata=test_metadata,
    )

    assert observation_id is not None

    # Verify all fields were stored correctly
    observations = registry.get_model_observations(sample_model)
    assert len(observations) == 1
    obs = observations[0]
    assert obs["id"] == int(observation_id)
    assert (
        obs["observation"] == "Model exhibits high memory usage during batch inference"
    )
    assert obs["created_by"] == "test_user@example.com"
    assert set(obs["tags"]) == set(test_tags)
    assert obs["metadata"] == test_metadata


def test_get_observations(registry, sample_model):
    """Test retrieving observations for a model."""
    # Add multiple observations and track their IDs
    observations_data = []
    for i in range(3):
        obs_id = registry.add_model_observation(
            model_id=sample_model,
            observation=f"Test observation {i}",
            tags=[f"tag{i}", "common"],
        )
        observations_data.append(
            {
                "id": int(obs_id),
                "observation": f"Test observation {i}",
                "tags": [f"tag{i}", "common"],
            }
        )

    # Get all observations
    observations = registry.get_model_observations(sample_model)

    assert len(observations) == 3

    # Verify all expected fields are present
    for obs in observations:
        assert "id" in obs
        assert "observation" in obs
        assert "created_at" in obs
        assert "tags" in obs

    # Check order (should be most recent first)
    assert observations[0]["observation"] == "Test observation 2"
    assert observations[2]["observation"] == "Test observation 0"

    # Verify all observation IDs are present
    returned_ids = {obs["id"] for obs in observations}
    expected_ids = {data["id"] for data in observations_data}
    assert returned_ids == expected_ids


def test_get_observations_with_pagination(registry, sample_model):
    """Test pagination when retrieving observations."""
    # Add 5 observations
    for i in range(5):
        registry.add_model_observation(
            model_id=sample_model, observation=f"Observation {i}"
        )

    # Get first 2
    page1 = registry.get_model_observations(sample_model, limit=2)
    assert len(page1) == 2

    # Get next 2
    page2 = registry.get_model_observations(sample_model, limit=2, offset=2)
    assert len(page2) == 2

    # Ensure no overlap
    page1_ids = {obs["id"] for obs in page1}
    page2_ids = {obs["id"] for obs in page2}
    assert len(page1_ids.intersection(page2_ids)) == 0


def test_get_observations_by_tag(registry, sample_model):
    """Test filtering observations by tags."""
    # Add observations with different tags
    registry.add_model_observation(
        model_id=sample_model,
        observation="Performance issue",
        tags=["performance", "issue"],
    )

    registry.add_model_observation(
        model_id=sample_model,
        observation="Security concern",
        tags=["security", "issue"],
    )

    registry.add_model_observation(
        model_id=sample_model,
        observation="Good accuracy",
        tags=["performance", "positive"],
    )

    # Filter by single tag
    perf_obs = registry.get_model_observations(sample_model, tags=["performance"])
    assert len(perf_obs) == 2

    # Filter by multiple tags (should return observations with ANY of the tags)
    issue_obs = registry.get_model_observations(
        sample_model, tags=["issue", "positive"]
    )
    assert len(issue_obs) == 3


def test_observation_nonexistent_model(registry):
    """Test adding observation to non-existent model."""
    with pytest.raises(ValueError, match="Model with id 999999 not found"):
        registry.add_model_observation(
            model_id="999999", observation="This should fail"
        )


def test_local_registry_observations(local_registry):
    """Test observations in local registry."""
    # First add model to global registry
    global_registry = local_registry.global_registry

    # Create unique model name to avoid conflicts
    from datetime import datetime

    unique_suffix = datetime.now().timestamp()

    model_info = {
        "model_name": f"local_test_model_{unique_suffix}",
        "model_maker": "test",
        "params_count": 1000,
        "quantization": "fp32",
    }

    # Add model to global registry
    global_model_id = global_registry.add_model(model_info)

    # Add a source to global model
    source_info = {
        "source_identifier": '{"loader_class": "AutoModelForCausalLM", "checkpoint": "test/local_model"}',
        "source_type": "huggingface_api",
        "requires_auth": False,
    }
    global_registry.add_model_source(global_model_id, "huggingface_api", source_info)

    # Register a fingerprint so similarity checks can work
    import numpy as np

    fingerprint_vec = np.array([0.1, 0.2, 0.3])
    global_registry.register_fingerprint(
        model_id=str(global_model_id),
        fingerprint_type="input_output",
        fingerprint_vector=fingerprint_vec,
        fingerprint_config={},
    )

    # Copy model from global to local registry
    status, local_model_id = local_registry.copy_model_from_global(global_model_id)
    assert status in ["added", "updated", "up_to_date"]
    assert local_model_id is not None

    # Add observation using the local model ID
    obs_id = local_registry.add_model_observation(
        model_id=str(local_model_id),
        observation="Local observation test",
        created_by="local_user",
        tags=["local", "test"],
    )

    assert obs_id is not None

    # Retrieve observation
    observations = local_registry.get_model_observations(str(local_model_id))
    assert len(observations) == 1
    assert observations[0]["observation"] == "Local observation test"
    assert observations[0]["created_by"] == "local_user"
    assert "local" in observations[0]["tags"]


def test_local_registry_observations_by_tag(local_registry):
    """Test filtering observations by tags in local registry (DuckDB list_has_any)."""
    # First add model to global registry
    global_registry = local_registry.global_registry

    # Create unique model name to avoid conflicts
    from datetime import datetime

    import numpy as np

    unique_suffix = datetime.now().timestamp()

    model_info = {
        "model_name": f"local_tag_test_model_{unique_suffix}",
        "model_maker": "test",
        "params_count": 1000,
        "quantization": "fp32",
    }

    # Add model to global registry
    global_model_id = global_registry.add_model(model_info)

    # Add a source to global model
    source_info = {
        "source_identifier": '{"loader_class": "AutoModelForCausalLM", "checkpoint": "test/local_tag_model"}',
        "source_type": "huggingface_api",
        "requires_auth": False,
    }
    global_registry.add_model_source(global_model_id, "huggingface_api", source_info)

    # Register a fingerprint so similarity checks can work
    fingerprint_vec = np.array([0.4, 0.5, 0.6])
    global_registry.register_fingerprint(
        model_id=str(global_model_id),
        fingerprint_type="input_output",
        fingerprint_vector=fingerprint_vec,
        fingerprint_config={},
    )

    # Copy model from global to local registry
    status, local_model_id = local_registry.copy_model_from_global(global_model_id)
    assert status in ["added", "updated", "up_to_date"]
    assert local_model_id is not None

    # Add observations with different tags
    local_registry.add_model_observation(
        model_id=str(local_model_id),
        observation="Performance issue",
        tags=["performance", "issue"],
    )

    local_registry.add_model_observation(
        model_id=str(local_model_id),
        observation="Security concern",
        tags=["security", "issue"],
    )

    local_registry.add_model_observation(
        model_id=str(local_model_id),
        observation="Good accuracy",
        tags=["performance", "positive"],
    )

    # Test filtering by single tag
    perf_obs = local_registry.get_model_observations(
        str(local_model_id), tags=["performance"]
    )
    assert len(perf_obs) == 2
    perf_observations = [obs["observation"] for obs in perf_obs]
    assert "Performance issue" in perf_observations
    assert "Good accuracy" in perf_observations

    # Test filtering by multiple tags (should use list_has_any for ANY match)
    issue_positive_obs = local_registry.get_model_observations(
        str(local_model_id), tags=["issue", "positive"]
    )
    assert len(issue_positive_obs) == 3  # All observations match at least one tag

    # Test filtering by tag that only matches some observations
    security_obs = local_registry.get_model_observations(
        str(local_model_id), tags=["security"]
    )
    assert len(security_obs) == 1
    assert security_obs[0]["observation"] == "Security concern"

    # Test filtering with non-existent tag
    no_match_obs = local_registry.get_model_observations(
        str(local_model_id), tags=["non_existent_tag"]
    )
    assert len(no_match_obs) == 0

    # Test filtering with empty tags list (should return all)
    all_obs = local_registry.get_model_observations(str(local_model_id), tags=[])
    assert len(all_obs) == 3  # Should not filter when tags list is empty

    # Verify order is preserved (most recent first)
    assert all_obs[0]["observation"] == "Good accuracy"
    assert all_obs[1]["observation"] == "Security concern"
    assert all_obs[2]["observation"] == "Performance issue"


def test_observation_edge_cases(registry, sample_model):
    """Test edge cases for model observations."""
    # Test empty observation (should fail)
    with pytest.raises(ValueError, match="Observation cannot be empty"):
        registry.add_model_observation(
            model_id=sample_model,
            observation="",
        )

    # Test whitespace-only observation (should also fail)
    with pytest.raises(ValueError, match="Observation cannot be empty"):
        registry.add_model_observation(
            model_id=sample_model,
            observation="   \n\t  ",
        )

    # Test very long observation (should work)
    long_observation = "x" * 10000  # 10k characters
    obs_id = registry.add_model_observation(
        model_id=sample_model,
        observation=long_observation,
    )
    assert obs_id is not None

    # Verify only the long observation was stored
    observations = registry.get_model_observations(sample_model)
    assert len(observations) == 1
    assert observations[0]["observation"] == long_observation

    # Test with empty tags list
    obs_id = registry.add_model_observation(
        model_id=sample_model,
        observation="Test with empty tags",
        tags=[],
    )
    assert obs_id is not None

    # Test with None metadata (should work)
    obs_id = registry.add_model_observation(
        model_id=sample_model,
        observation="Test with None metadata",
        metadata=None,
    )
    assert obs_id is not None

    # Test filtering with non-existent tag
    filtered_obs = registry.get_model_observations(
        sample_model, tags=["non_existent_tag"]
    )
    assert len(filtered_obs) == 0

    # Test large offset
    obs_with_large_offset = registry.get_model_observations(sample_model, offset=1000)
    assert len(obs_with_large_offset) == 0


def test_metadata_json_handling(registry, sample_model):
    """Test that metadata is properly stored and retrieved as JSON."""
    test_timestamp = datetime.now().isoformat()
    complex_metadata = {
        "metrics": {"accuracy": 0.95, "f1_score": 0.92},
        "test_conditions": ["zero_shot", "few_shot"],
        "timestamp": test_timestamp,
        "nested_data": {"level1": {"level2": ["value1", "value2"], "number": 42}},
    }

    obs_id = registry.add_model_observation(
        model_id=sample_model,
        observation="Complex metadata test",
        metadata=complex_metadata,
    )

    observations = registry.get_model_observations(sample_model)
    assert len(observations) == 1
    assert observations[0]["id"] == int(obs_id)

    # Verify complex metadata structure is preserved
    retrieved_metadata = observations[0]["metadata"]
    assert retrieved_metadata["metrics"]["accuracy"] == 0.95
    assert retrieved_metadata["metrics"]["f1_score"] == 0.92
    assert "zero_shot" in retrieved_metadata["test_conditions"]
    assert "few_shot" in retrieved_metadata["test_conditions"]
    assert retrieved_metadata["timestamp"] == test_timestamp

    # Test nested data structure
    assert retrieved_metadata["nested_data"]["level1"]["level2"] == ["value1", "value2"]
    assert retrieved_metadata["nested_data"]["level1"]["number"] == 42
