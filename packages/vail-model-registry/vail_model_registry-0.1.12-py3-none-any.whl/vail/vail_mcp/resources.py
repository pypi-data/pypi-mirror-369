"""
Resources for the MCP Server

This module contains implementation details and resources used by the MCP server.
"""

import os
import tempfile
from typing import Dict, List

from vail.fingerprint.methods import (
    ArchitectureFingerprintingMethod,
    InputOutputFingerprintingMethod,
    WeightFingerprintingMethod,
)
from vail.fingerprint.visualization import create_family_fingerprint_visualization
from vail.registry import RegistryInterface
from vail.utils import setup_logging

# Initialize logging
Logger = setup_logging(log_file_name="mcp_resources.log")

# =============================================
# Fingerprinting Configurations
# =============================================

# Resolve paths relative to the project root
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))

DEFAULT_PROBE_TOKENS_PATH = os.path.join(
    _PROJECT_ROOT, "helper_data/io_tokens/probe_tokens.txt"
)
DEFAULT_TARGET_TOKENS_PATH = os.path.join(
    _PROJECT_ROOT, "helper_data/io_tokens/target_tokens.txt"
)
DEFAULT_N0 = 40
DEFAULT_WT_ARCH_FP_SIZE = 50  # Default size for weight/architecture methods


# Mapping from fingerprint type string to the corresponding method class
FINGERPRINT_METHOD_MAP = {
    "input_output": InputOutputFingerprintingMethod,
    "weight": WeightFingerprintingMethod,
    "architecture": ArchitectureFingerprintingMethod,
}

# Define constants for visualization
SIMILARITY_METHOD = "l1"  # Hardcoded similarity method
FAMILY1_COLOR = "#7080b0"
FAMILY2_COLOR = "#3366bb"


def get_fingerprint_vectors_impl(
    model_ids: List[str], fingerprint_type: str = "input_output", registry=None
) -> Dict:
    """
    Retrieve the fingerprint vector for a given fingerprint type for multiple model IDs.

    Args:
        model_ids: A list of model IDs.
        fingerprint_type: The type of the fingerprint to retrieve for all models. Defaults to "input_output".
        registry: Optional registry interface instance. If None, a new one will be created.

    Returns:
        Dictionary containing a list of results, one for each model ID.
        Each result indicates success or failure and includes the vector or an error message.
    """
    results = []
    Logger.info(
        f"Received request to get fingerprint vectors for model_ids: {model_ids}, type: {fingerprint_type}"
    )

    # Use provided registry or create a new one
    if registry is None:
        registry = RegistryInterface(os.getenv("DATABASE_URL"))

    for model_id in model_ids:
        try:
            Logger.debug(
                f"Attempting to retrieve fingerprint for model {model_id}, type {fingerprint_type}"
            )
            fingerprint_vector = registry.get_fingerprint(
                model_id=model_id, fingerprint_type=fingerprint_type
            )

            if fingerprint_vector is None:
                Logger.warning(
                    f"Fingerprint not found for model {model_id}, type {fingerprint_type}"
                )
                results.append(
                    {
                        "status": "error",
                        "model_id": model_id,
                        "fingerprint_type": fingerprint_type,
                        "detail": f"Fingerprint vector not found for model_id '{model_id}' and fingerprint_type '{fingerprint_type}'",
                    }
                )
            else:
                # Convert numpy array to list for JSON serialization
                fingerprint_list = fingerprint_vector.tolist()
                Logger.info(
                    f"Successfully retrieved fingerprint vector for model {model_id}, type {fingerprint_type}"
                )
                results.append(
                    {
                        "status": "success",
                        "model_id": model_id,
                        "fingerprint_type": fingerprint_type,
                        "fingerprint_vector": fingerprint_list,
                    }
                )

        except Exception as e:
            # Catch potential database errors or other exceptions during retrieval for a single ID
            Logger.error(
                f"Error getting fingerprint vector for model {model_id}, type {fingerprint_type}: {e}",
                exc_info=True,
            )
            results.append(
                {
                    "status": "error",
                    "model_id": model_id,
                    "fingerprint_type": fingerprint_type,
                    "detail": f"Internal server error while processing model_id '{model_id}': {str(e)}",
                }
            )

    return {"results": results}


# def get_model_id_from_source_id(source_id: str, registry) -> str:
#     """Retrieve the model_id associated with a given source_id."""
#     try:
#         with registry._get_connection() as conn:
#             with conn.cursor() as cur:
#                 cur.execute(
#                     f"SELECT model_id FROM {registry.schema}.model_sources WHERE id = %s",
#                     (source_id,),
#                 )
#                 result = cur.fetchone()
#                 if result:
#                     return str(result[0])
#                 else:
#                     return None
#     except Exception as e:
#         Logger.error(f"Error fetching model_id for source_id {source_id}: {e}")
#         return None


def _check_existing_fingerprint(registry, model_id, fingerprint_type):
    """Check if a fingerprint already exists."""
    Logger.debug(
        f"Checking for existing {fingerprint_type} fingerprint for model {model_id}"
    )
    return registry.get_fingerprint(model_id, fingerprint_type)


def _load_model_object(registry, model_id):
    """Load the Model object from the registry."""
    Logger.debug(f"Loading model object for model_id {model_id}")
    model_obj = registry.find_model(model_id)
    if not model_obj:
        Logger.error(f"Model object not found for model_id {model_id}")
        raise ValueError(f"Model with id '{model_id}' not found in registry.")
    Logger.info(f"Successfully loaded model: {model_obj.name}")
    return model_obj


def _instantiate_fingerprint_method(fingerprint_type):
    """Instantiate the fingerprinting method class with default configurations."""
    Logger.debug(f"Instantiating fingerprint method for type: {fingerprint_type}")
    if fingerprint_type not in FINGERPRINT_METHOD_MAP:
        valid_types = list(FINGERPRINT_METHOD_MAP.keys())
        Logger.error(
            f"Unsupported fingerprint type: {fingerprint_type}. Valid: {valid_types}"
        )
        raise ValueError(
            f"Unsupported fingerprint type: '{fingerprint_type}'. Valid types are: {valid_types}"
        )

    try:
        MethodClass = FINGERPRINT_METHOD_MAP[fingerprint_type]

        if MethodClass == InputOutputFingerprintingMethod:
            if not os.path.exists(DEFAULT_PROBE_TOKENS_PATH):
                Logger.error(f"Probe tokens file not found for {fingerprint_type}")
                raise FileNotFoundError(
                    f"Default probe tokens file not found: {DEFAULT_PROBE_TOKENS_PATH}"
                )
            if not os.path.exists(DEFAULT_TARGET_TOKENS_PATH):
                Logger.error(f"Target tokens file not found for {fingerprint_type}")
                raise FileNotFoundError(
                    f"Default target tokens file not found: {DEFAULT_TARGET_TOKENS_PATH}"
                )
            method_instance = MethodClass(
                n0=DEFAULT_N0,
                probe_tokens_path=DEFAULT_PROBE_TOKENS_PATH,
                target_tokens_path=DEFAULT_TARGET_TOKENS_PATH,
            )
        elif MethodClass in [
            WeightFingerprintingMethod,
            ArchitectureFingerprintingMethod,
        ]:
            method_instance = MethodClass(size=DEFAULT_WT_ARCH_FP_SIZE)
        else:
            # Default instantiation if no specific config needed
            method_instance = MethodClass()

        Logger.info(
            f"Successfully instantiated {MethodClass.__name__} for {fingerprint_type}"
        )
        return method_instance

    except Exception as e:
        Logger.error(
            f"Error instantiating fingerprint method {fingerprint_type}: {e}",
            exc_info=True,
        )
        raise ValueError(
            f"Error preparing fingerprint function for type '{fingerprint_type}': {e}"
        )


def _execute_fingerprint_generation(method_instance, model_obj):
    """Execute the fingerprint generation locally."""
    fingerprint_func = method_instance.generate_fingerprint
    func_name = f"{method_instance.__class__.__name__}.generate_fingerprint"
    Logger.info(f"Executing {func_name} for model {model_obj.name} ...")

    try:
        fingerprint_data = fingerprint_func(model_obj)

        Logger.info("Fingerprint generation completed successfully.")
        Logger.debug(
            f"Generated fingerprint data shape/type: {getattr(fingerprint_data, 'shape', type(fingerprint_data))}"
        )
        return fingerprint_data
    except Exception as e:
        Logger.error(f"Fingerprint generation failed: {e}", exc_info=True)
        raise ValueError(f"Fingerprint generation failed: {str(e)}")


def _register_fingerprint(
    registry, model_id, fingerprint_type, fingerprint_vector, fingerprint_config
):
    """Register the generated fingerprint data and configuration."""
    Logger.info(f"Registering {fingerprint_type} fingerprint for model {model_id}")
    try:
        fingerprint_id = registry.register_fingerprint(
            model_id=model_id,
            fingerprint_type=fingerprint_type,
            fingerprint_vector=fingerprint_vector,  # Pass the list
            fingerprint_config=fingerprint_config,
            override_checks=False,  # Internal override logic is handled earlier
        )
        Logger.info(f"Successfully registered fingerprint. ID: {fingerprint_id}")
        return fingerprint_id
    except Exception as e:
        Logger.error(
            f"Failed to register fingerprint for model {model_id}: {e}", exc_info=True
        )
        raise ValueError(f"Database error during fingerprint registration: {str(e)}")


def generate_fingerprint_impl(
    registry: RegistryInterface,
    source_id: str,
    fingerprint_type: str,
    override: bool = False,
) -> Dict:
    """Core implementation logic for generating a fingerprint."""

    # 1. Get model_id from source_id
    model_id = registry.get_model_id_from_source_id(source_id)
    if not model_id:
        raise ValueError(f"Invalid source_id: {source_id}")
    Logger.debug(f"Found model_id: {model_id} for source_id: {source_id}")

    # 2. Check for existing fingerprint if override is False
    if not override:
        existing_fingerprint = _check_existing_fingerprint(
            registry, model_id, fingerprint_type
        )
        if existing_fingerprint is not None:
            message = f"Fingerprint of type '{fingerprint_type}' already exists for model_id '{model_id}'. Use override=True to regenerate."
            Logger.info(message)
            # Return a specific structure recognizable by the wrapper
            return {
                "status": "skipped",
                "message": message,
                "model_id": model_id,
                "fingerprint_type": fingerprint_type,
            }

    # 3. Load Model object
    model_obj = _load_model_object(registry, model_id)

    # 4. Instantiate Fingerprinting Method
    method_instance = _instantiate_fingerprint_method(fingerprint_type)
    fingerprint_config = method_instance.get_config()

    # 5. Execute Fingerprint Generation
    fingerprint_vector = _execute_fingerprint_generation(method_instance, model_obj)

    # 6. Register Fingerprint only if registry is not local
    fingerprint_id = None
    message = f"Successfully generated fingerprint type '{fingerprint_type}' for model_id '{model_id}'."

    if registry.registry_type != "local":
        fingerprint_id = _register_fingerprint(
            registry, model_id, fingerprint_type, fingerprint_vector, fingerprint_config
        )
        message = f"Successfully generated and registered fingerprint type '{fingerprint_type}' for model_id '{model_id}'. Fingerprint ID: {fingerprint_id}"

    # 7. Prepare Success Response
    Logger.info(message)
    return {
        "status": "success",
        "message": message,
        "fingerprint_id": fingerprint_id,
        "model_id": model_id,
        "fingerprint_type": fingerprint_type,
        "fingerprint_config": fingerprint_config,
        "fingerprint_data": fingerprint_vector.tolist(),  # Convert numpy array to list for JSON serialization
    }


def compare_fp_pairs_impl(
    vector_ref1: List[float],
    vector_var1: List[float],
    vector_ref2: List[float],
    vector_var2: List[float],
    family1_name: str,
    family2_name: str,
    model_name_ref1: str,
    model_name_var1: str,
    model_name_ref2: str,
    model_name_var2: str,
) -> Dict:
    """Core implementation logic for generating fingerprint comparison visualization."""
    Logger.info(
        f"Generating fingerprint pair comparison (Similarity: {SIMILARITY_METHOD}) for families '{family1_name}' and '{family2_name}'"
    )

    try:
        # 1. Prepare arguments for visualization
        vectors = [vector_ref1, vector_var1, vector_ref2, vector_var2]
        model_names = [
            model_name_ref1,
            model_name_var1,
            model_name_ref2,
            model_name_var2,
        ]
        families = [family1_name, family1_name, family2_name, family2_name]
        family_colors = {
            family1_name: FAMILY1_COLOR,
            family2_name: FAMILY2_COLOR,
        }
        reference_indices = {
            family1_name: 0,  # Assumes ref1 is the reference for family 1
            family2_name: 2,  # Assumes ref2 is the reference for family 2
        }

        # 2. Generate temporary file path
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            save_path = tmp_file.name
        Logger.debug(f"Using temporary file path for visualization: {save_path}")

        # 3. Create visualization
        # Note: The original code had a hardcoded save_path in the function call.
        # Using the dynamically generated temp path instead.
        generated_path = create_family_fingerprint_visualization(
            vectors=vectors,
            model_names=model_names,
            families=families,
            reference_indices=reference_indices,
            family_colors=family_colors,
            similarity_method=SIMILARITY_METHOD,
            save_path=save_path,  # Use the generated temp path
            show_ipv6=False,
            show_similarity=True,
        )

        if save_path and generated_path and os.path.exists(generated_path):
            Logger.info(f"Visualization saved successfully to {generated_path}")
            # Ensure the returned path matches the generated path
            return {"status": "success", "visualization_path": generated_path}
        else:
            Logger.error(
                f"Visualization generation failed. Expected path: {save_path}, Generated path: {generated_path}"
            )
            raise ValueError(
                "Visualization generation failed internally. Generated path might be missing or incorrect."
            )

    except Exception as e:
        # Catch errors during visualization generation or file handling
        Logger.error(
            f"Error during fingerprint comparison visualization: {e}", exc_info=True
        )
        # Raise as ValueError as it likely indicates an issue with input data or the visualization function itself
        raise ValueError(f"Error generating fingerprint comparison: {str(e)}")
