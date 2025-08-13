"""
Tests for the RegistryInterface class.

This module provides comprehensive tests for the RegistryInterface class,
covering model management, fingerprint operations, and hardware information.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from vail.utils.env import load_env

# Mock transformers before importing RegistryInterface
mock_auto_tokenizer = MagicMock()
with patch.dict(
    "sys.modules", {"transformers": MagicMock(AutoTokenizer=mock_auto_tokenizer)}
):
    from vail.registry import RegistryInterface
    from vail.registry.models import ModelFilterCriteria


# Load test environment variables
load_env("test")


@pytest.fixture
def registry():
    """Create a RegistryInterface instance for testing."""
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string:
        pytest.skip("DATABASE_URL environment variable not set in .env.test")
    if "test" not in connection_string:
        raise ValueError(
            "DATABASE_URL must include 'test' to prevent accidental modifications to production database"
        )

    # Ensure the test database schema is set up
    RegistryInterface.setup_global_registry(connection_string)

    return RegistryInterface(connection_string)


@pytest.fixture(autouse=True)
def cleanup_database(registry):
    """Clean up the database after each test."""
    yield  # Run the test
    # After test completes, clean up
    with registry._get_connection() as conn:
        with conn.cursor() as cur:
            # Delete in correct order to respect foreign key constraints
            cur.execute("DELETE FROM fingerprints")
            cur.execute("DELETE FROM model_sources")
            cur.execute("DELETE FROM models")
            cur.execute("DELETE FROM hardware_info")
            conn.commit()


@pytest.fixture
def sample_model_info():
    """Create sample model information for testing."""
    return [
        {
            "model_name": "microsoft/phi-4",
            "model_maker": "Microsoft",
            "quantization": "bfloat16",
            "context_length": 16384,
            "params_count": 14000000000,
            "license": "MIT",
        },
        {
            "model_name": "microsoft/Phi-3-mini-4k-instruct",
            "model_maker": "Microsoft",
            "quantization": "bfloat16",
            "context_length": 4096,
            "params_count": 3800000000,
            "license": "MIT",
        },
        {
            "model_name": "t5_v1_1-small_conditional_generation",
            "model_maker": "google",
            "quantization": "",
            "context_length": 1024,
            "params_count": 60000000,
            "license": "Apache 2.0",
        },
        {
            "model_name": "jondurbin/airoboros-70b-3.3",
            "model_maker": "jondurbin",
            "quantization": "bfloat16",
            "license": "Llama 3",
            "params_count": 70000000000,
        },
    ]


@pytest.fixture
def sample_source_info():
    """Create sample source information for testing."""
    return [
        {
            "source_type": "huggingface_api",
            "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"microsoft/phi-4"}',
            "license": "MIT",
            "link": "https://huggingface.co/microsoft/phi-4",
            "human_verified": "X",
            "requires_auth": False,
            "comment": "",
        },
        {
            "source_type": "huggingface_api",
            "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"microsoft/Phi-3-mini-4k-instruct"}',
            "license": "MIT",
            "link": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct",
            "human_verified": "X",
            "comment": "",
        },
        {
            "source_type": "huggingface_api",
            "source_identifier": '{"loader_class":"T5ForConditionalGeneration","checkpoint":"google/t5-v1_1-small"}',
            "license": "Apache 2.0",
            "link": "https://huggingface.co/google/t5-v1_1-small",
            "human_verified": "X",
            "requires_auth": False,
            "comment": "",
        },
        {
            "source_type": "huggingface_api",
            "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"jondurbin/airoboros-70b-3.3"}',
            "license": "Llama 3",
            "link": "https://huggingface.co/jondurbin/airoboros-70b-3.3",
            "human_verified": "X",
            "requires_auth": False,
            "comment": "",
        },
    ]


def test_add_and_get_model(registry, sample_model_info, sample_source_info):
    """Test adding a model and retrieving its information."""
    # Add model
    model_id = registry.add_model(sample_model_info[3])
    assert model_id is not None

    # Add source
    source_id = registry.add_model_source(
        model_id, "huggingface_api", sample_source_info[0]
    )
    assert source_id is not None

    # Get model info
    model_info = registry.get_model_loader_info(model_id)

    assert model_info["id"] == model_id
    assert model_info["model_maker"] == sample_model_info[3]["model_maker"]
    assert model_info["model_name"] == sample_model_info[3]["model_name"]
    assert len(model_info["sources"]) == 1
    assert model_info["sources"][0]["source_type"] == "huggingface_api"


def test_remove_model(registry, sample_model_info, sample_source_info):
    """Test removing a model and its associated data."""
    # Add model and source
    model_id = registry.add_model(sample_model_info[0])
    registry.add_model_source(model_id, "huggingface_api", sample_source_info[0])

    # Remove model
    registry.remove_model(model_id)

    # Verify model is removed
    assert registry.find_model(model_id) is None


# TODO: Add tests for finding similar models using fingerprints

# TODO: Add tests for getting fingerprints

# TODO: Add tests for adding fingerprints


def test_find_models(registry, sample_model_info, sample_source_info):
    """Test finding models by criteria."""
    # Add test models
    for idx, model_data in enumerate(sample_model_info):
        model_id = registry.add_model(model_data)
        registry.add_model_source(
            model_id, sample_source_info[idx]["source_type"], sample_source_info[idx]
        )

    # Test fetching all models (no filters)
    models = registry.find_models()
    assert len(models) >= len(sample_model_info)

    # Test filtering by an exact params_count (since to_sql_filters uses '=')
    exact_params_filter = ModelFilterCriteria(params_count_eq=3800000000)
    exact_param_models = registry.find_models(filters=exact_params_filter)
    assert len(exact_param_models) == 1
    assert (
        exact_param_models[0].model_info["model_name"]
        == "microsoft/Phi-3-mini-4k-instruct"
    )
    assert exact_param_models[0].model_info["params_count"] == 3800000000

    # Test filtering by maker
    maker_filter = ModelFilterCriteria(maker="Microsoft")
    microsoft_models = registry.find_models(filters=maker_filter)
    assert len(microsoft_models) == 2
    for model in microsoft_models:
        assert model.model_info["model_maker"] == "Microsoft"

    # Test filtering by quantization
    quant_filter = ModelFilterCriteria(quantization="bfloat16")
    bfloat16_models = registry.find_models(filters=quant_filter)
    assert len(bfloat16_models) == 3
    for model in bfloat16_models:
        assert model.model_info["quantization"] == "bfloat16"

    # Test combined filters
    combined_filter = ModelFilterCriteria(maker="Microsoft", quantization="bfloat16")
    combined_models = registry.find_models(filters=combined_filter)
    assert len(combined_models) == 2
    for model in combined_models:
        assert model.model_info["model_maker"] == "Microsoft"
        assert model.model_info["quantization"] == "bfloat16"
