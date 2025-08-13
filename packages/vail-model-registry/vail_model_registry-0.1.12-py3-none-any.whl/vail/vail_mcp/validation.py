"""
Validation logic for MCP Server tools.

This module contains validation functions and constants used primarily by the
'add_model' and 'get_model_template' tools.
"""

import json
from typing import Dict

from vail.constants import (
    VALID_LICENSES,
    VALID_LOADER_CLASSES,
    VALID_MODEL_MAKERS,
    VALID_QUANTIZATION,
)
from vail.utils import setup_logging

Logger = setup_logging(log_file_name="mcp_validation.log")  # Use a separate log file


# =============================================
# Validation Helper Functions
# =============================================


def validate_model_info(model_info: Dict) -> None:
    """
    Validate the model information dictionary.

    Args:
        model_info: Dictionary containing model information

    Raises:
        ValueError: If any validation fails
    """
    # Validate required model fields
    required_fields = [
        "model_maker",
        "model_name",
        "params_count",
        "license",
        "quantization",
    ]
    missing_fields = [field for field in required_fields if not model_info.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required model fields: {', '.join(missing_fields)}")

    # Validate params_count is a valid number
    if not isinstance(model_info["params_count"], int):
        raise TypeError("params_count must be an integer")

    # Validate context_length is a valid number if provided
    if "context_length" in model_info and not isinstance(
        model_info["context_length"], int
    ):
        raise TypeError("context_length must be an integer")

    # Validate model_maker is a valid value
    if model_info["model_maker"] not in VALID_MODEL_MAKERS:
        raise ValueError(
            f"Invalid model_maker. Must be one of: {', '.join(sorted(VALID_MODEL_MAKERS))}"
        )

    # Validate license is a valid value
    if model_info["license"] not in VALID_LICENSES:
        raise ValueError(
            f"Invalid license. Must be one of: {', '.join(sorted(VALID_LICENSES))}"
        )

    # Validate quantization is a valid value
    if model_info["quantization"].lower() not in {
        q.lower() for q in VALID_QUANTIZATION
    }:
        raise ValueError(
            f"Invalid quantization format. Must be one of: {', '.join(sorted(VALID_QUANTIZATION))}"
        )


def _validate_onnx_source(source_identifier_dict: Dict) -> None:
    """
    Validate ONNX source specific fields.

    Args:
        source_identifier_dict: Dictionary containing source identifier information

    Raises:
        ValueError: If ONNX source validation fails
    """
    if (
        "url" not in source_identifier_dict
        and "file_path" not in source_identifier_dict
    ):
        raise ValueError(
            "onnx source_identifier must include either 'url' or 'file_path' field"
        )


def _validate_gguf_source(source_identifier_dict: Dict) -> None:
    """
    Validate GGUF source specific fields.

    Args:
        source_identifier_dict: Dictionary containing source identifier information

    Raises:
        ValueError: If GGUF source validation fails
    """
    if (
        "url" not in source_identifier_dict
        and "file_path" not in source_identifier_dict
    ):
        raise ValueError(
            "gguf source_identifier must include either 'url' or 'file_path' field"
        )


def _validate_huggingface_source(source_identifier_dict: Dict) -> None:
    """
    Validate HuggingFace source specific fields.

    Args:
        source_identifier_dict: Dictionary containing source identifier information

    Raises:
        ValueError: If HuggingFace source validation fails
    """
    if "loader_class" not in source_identifier_dict:
        raise ValueError(
            "huggingface_api source_identifier must include 'loader_class' field"
        )
    if "checkpoint" not in source_identifier_dict:
        raise ValueError(
            "huggingface_api source_identifier must include 'checkpoint' field"
        )

    if source_identifier_dict["loader_class"] not in VALID_LOADER_CLASSES:
        raise ValueError(
            f"Invalid loader_class. Must be one of: {', '.join(sorted(VALID_LOADER_CLASSES))}"
        )


def validate_source_info(source_info: Dict) -> Dict:
    """
    Validate the source information dictionary.

    Args:
        source_info: Dictionary containing source information

    Returns:
        Dict: Parsed source identifier dictionary

    Raises:
        ValueError: If any validation fails
    """
    # Validate required source fields
    required_source_fields = ["source_type", "source_identifier"]
    missing_fields = [
        field for field in required_source_fields if not source_info.get(field)
    ]
    if missing_fields:
        raise ValueError(f"Missing required source fields: {', '.join(missing_fields)}")

    # Validate source_type is one of the allowed values
    valid_source_types = ["huggingface_api", "onnx_file", "gguf_file"]
    if source_info["source_type"] not in valid_source_types:
        raise ValueError(f"source_type must be one of: {', '.join(valid_source_types)}")

    # Parse and validate source_identifier
    try:
        if isinstance(source_info["source_identifier"], str):
            source_identifier_dict = json.loads(source_info["source_identifier"])
        else:
            source_identifier_dict = source_info["source_identifier"]

        # Call appropriate validation function based on source type
        if source_info["source_type"] == "huggingface_api":
            _validate_huggingface_source(source_identifier_dict)
        elif source_info["source_type"] == "onnx":
            _validate_onnx_source(source_identifier_dict)
        elif source_info["source_type"] == "gguf":
            _validate_gguf_source(source_identifier_dict)

        return source_identifier_dict

    except json.JSONDecodeError:
        raise ValueError("source_identifier must be a valid JSON string")
