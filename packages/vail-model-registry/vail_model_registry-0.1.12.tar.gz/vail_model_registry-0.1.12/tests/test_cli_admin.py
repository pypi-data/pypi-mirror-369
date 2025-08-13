"""
Tests for the CLI admin tool functionality.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from vail.cli_admin import (
    build_model_info_from_hf,
    build_source_info,
    extract_model_maker_from_checkpoint,
    handle_add_model,
)
from vail.registry import RegistryInterface
from vail.utils.env import load_env

# Load test environment variables to ensure we use the test database
load_env("test")


@pytest.fixture
def global_registry():
    """
    Provides a connection to a real, temporary global test database.
    Ensures the database is set up and cleaned up for each test.
    """
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string or "test" not in connection_string:
        pytest.fail(
            "DATABASE_URL for test database is not configured or is missing 'test'. "
            "Set it in your .env.test file."
        )

    # Ensure the test database schema is set up
    RegistryInterface.setup_global_registry(connection_string)
    registry = RegistryInterface(connection_string)

    yield registry

    # Teardown: Clean up the database after the test
    with registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM fingerprints")
            cur.execute("DELETE FROM model_sources")
            cur.execute("DELETE FROM models")
            conn.commit()


@patch("vail.cli_admin.get_registry")
@patch("vail.cli_admin.input")
@patch("vail.cli_admin.build_model_info_from_hf")
@patch("vail.cli_admin.build_source_info")
def test_add_model_logic(
    mock_build_source, mock_build_model, mock_input, mock_get_registry
):
    """
    Test the main 'handle_add_model' function to ensure it calls the registry correctly.
    This test is mocked to isolate the CLI logic from external services.
    """
    # 1. Setup Mocks
    mock_input.return_value = "P"  # Simulate user pressing "Proceed"

    mock_model_data = {
        "model_maker": "Google",
        "model_name": "test-maker/test-model",
        "params_count": 1000,
        "license": "mit",
        "quantization": "fp32",
    }
    mock_source_data = {
        "source_type": "huggingface_api",
        "source_identifier": {
            "checkpoint": "test-maker/test-model",
            "loader_class": "AutoModelForCausalLM",
        },
        "requires_auth": False,
    }
    mock_build_model.return_value = mock_model_data
    mock_build_source.return_value = mock_source_data

    mock_registry = MagicMock()
    mock_registry.add_model.return_value = 123  # Mock model_id
    mock_registry.add_model_source.return_value = 456  # Mock source_id
    mock_get_registry.return_value = mock_registry

    # 2. Setup mock CLI arguments
    mock_args = MagicMock()
    mock_args.checkpoint = "test-maker/test-model"
    mock_args.source_type = "safetensor"
    mock_args.quantization = None
    mock_args.requires_auth = False
    mock_args.use_hf_mcp = False
    mock_args.env = None
    mock_args.fingerprint = False

    # 3. Call the function to be tested
    handle_add_model(mock_args)

    # 4. Assert that the core functionality was executed
    mock_build_model.assert_called_once()
    mock_build_source.assert_called_once()
    mock_registry.add_model.assert_called_once_with(mock_model_data)
    mock_registry.add_model_source.assert_called_once_with(
        123,  # Expected model_id
        mock_source_data["source_type"],
        {
            "source_identifier": mock_source_data["source_identifier"],
            "requires_auth": False,
        },
    )
    print("✓ Add-model-to-registry logic test passed")


def test_error_handling_and_edge_cases():
    """Test error handling and edge cases across functions."""
    # Test invalid source type
    with pytest.raises(ValueError, match="Unsupported source type"):
        build_source_info("test/model", "invalid_type")

    # Test edge cases in model maker extraction
    test_cases = [
        ("org/model", "org"),
        ("single_name", "unknown"),
        ("nested/path/model", "nested"),
        ("", "unknown"),
    ]
    for checkpoint, expected_maker in test_cases:
        assert extract_model_maker_from_checkpoint(checkpoint) == expected_maker

    print("✓ Error handling and edge cases test passed")


@patch("vail.cli_admin.input", return_value="P")
@patch("vail.cli_admin.build_model_info_from_hf")
def test_add_model_to_real_database(mock_build_model, mock_input, global_registry):
    """
    Integration test: ensures handle_add_model successfully adds a model
    to a real test database.
    """
    # 1. Define test data. The checkpoint is the key identifier.
    model_maker = "Google"
    model_base_name = "real-db-test-model"
    checkpoint = f"{model_maker}/{model_base_name}"

    # 2. Setup Mocks to be consistent with cli_admin's logic.
    mock_model_data = {
        "model_maker": model_maker,
        "model_name": checkpoint,
        "params_count": 1000,
        "license": "mit",
        "quantization": "fp32",
    }
    mock_build_model.return_value = mock_model_data

    # 3. Setup mock CLI arguments
    mock_args = MagicMock()
    mock_args.checkpoint = checkpoint
    mock_args.source_type = "safetensor"
    mock_args.quantization = None
    mock_args.requires_auth = False
    mock_args.use_hf_mcp = False
    mock_args.env = "test"  # Ensure it uses the test environment
    mock_args.fingerprint = False

    # 4. Run the function that interacts with the database
    with patch("vail.cli_admin.get_registry", return_value=global_registry):
        handle_add_model(mock_args)

    # 5. Verify the result by querying for the checkpoint in the model_name column
    with global_registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT model_name, model_maker FROM models WHERE model_name = %s",
                (checkpoint,),  # Verify using the full checkpoint
            )
            result = cur.fetchone()

    assert result is not None, "Model was not found in the database"
    assert result[0] == checkpoint  # This now correctly checks for the full checkpoint
    assert result[1] == model_maker
    print(
        "✓ Integration test passed: Model successfully added to the real test database"
    )


def test_build_source_info_gguf_quantization():
    """Test that GGUF source_info is built correctly with quantization logic"""
    checkpoint = "bartowski/Llama-3.2-3B-Instruct-GGUF"

    # Test GGUF source_info structure
    source_info = build_source_info(checkpoint, "gguf", requires_auth=False)

    assert source_info["source_type"] == "gguf_file"
    source_data = json.loads(source_info["source_identifier"])

    # Critical: quantization should NOT be in source_identifier
    assert "quantization" not in source_data
    assert source_data["checkpoint"] == checkpoint
    assert "loader_kwargs" in source_data

    print("✓ GGUF source_info building test passed")


@patch("vail.cli_admin.print_error")
def test_gguf_quantization_validation_in_cli(mock_error):
    """Test that CLI properly validates quantization requirement for GGUF"""
    mock_args = MagicMock()
    mock_args.checkpoint = "test/gguf-model"
    mock_args.source_type = "gguf"
    mock_args.quantization = None  # Missing quantization
    mock_args.env = None

    # Should return error code 1 when quantization is missing
    result = handle_add_model(mock_args)
    assert result == 1
    mock_error.assert_called_with("Quantization type is required for gguf models")

    print("✓ GGUF quantization validation test passed")


def test_model_info_building_with_real_hf_api():
    """
    Test the complete data building workflow using a real HuggingFace API call.
    This verifies that HF integration works and that data is shaped correctly.
    """
    # Use a small, real model with an organization prefix
    checkpoint = "meta-llama/Llama-3.1-8B-Instruct"

    try:
        # 1. Test model maker extraction
        model_maker = extract_model_maker_from_checkpoint(checkpoint)
        assert model_maker == "meta-llama"

        # 2. Test building model info with a real HF call
        model_info = build_model_info_from_hf(checkpoint, "safetensor", use_hf_mcp=True)
        assert model_info["model_name"] == checkpoint  # Verify the main fix
        assert model_info["model_maker"] == "meta-llama"
        assert "params_count" in model_info  # Check that some data was returned

        # 3. Test building source info
        source_info = build_source_info(checkpoint, "safetensor", requires_auth=False)
        assert source_info["source_type"] == "huggingface_api"
        source_data = json.loads(source_info["source_identifier"])
        assert source_data["checkpoint"] == checkpoint

        print("✓ Real HuggingFace API workflow test passed")

    except Exception as e:
        pytest.fail(f"HuggingFace API call failed with an exception: {e}")
