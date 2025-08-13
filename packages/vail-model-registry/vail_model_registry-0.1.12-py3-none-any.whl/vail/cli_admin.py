#!/usr/bin/env python
"""
Admin command-line interface for the VAIL Model Registry.
This module provides admin-only functionality for adding models and managing fingerprints.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional

from vail.utils.data_utils import get_combined_hf_model_info
from vail.utils.env import load_env
from vail.vail_mcp.server import get_registry
from vail.vail_mcp.validation import validate_model_info, validate_source_info

# Set up logging
log = logging.getLogger(__name__)


# Simple console output functions (replacing Rich)
def print_success(message):
    print(f"✓ {message}")


def print_error(message):
    print(f"✗ {message}")


def print_warning(message):
    print(f"⚠ {message}")


def print_info(message):
    print(f"ℹ {message}")


def print_table(title, data):
    """Simple table printing to replace Rich table."""
    print(f"\n{title}")
    print("=" * len(title))
    for key, value in data.items():
        print(f"{key:<20}: {value}")
    print()


def _edit_data_in_editor(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Opens the user's default editor to edit the given data in a temporary JSON file.

    Args:
        data: The dictionary of data to be edited.

    Returns:
        The updated dictionary, or None if the edit was aborted or failed.
    """
    editor = os.environ.get("VISUAL", os.environ.get("EDITOR", "vim"))

    try:
        with tempfile.NamedTemporaryFile(
            "w+", delete=False, suffix=".json", encoding="utf-8"
        ) as fp:
            temp_file_path = fp.name
            json.dump(data, fp, indent=4)
            fp.flush()

        print(f"\nOpening temporary file for editing with '{editor}': {temp_file_path}")
        print(
            "Save and close the editor when you are done. Close without saving to abort."
        )

        stat_before = os.stat(temp_file_path)
        subprocess.run([editor, temp_file_path], check=True)
        stat_after = os.stat(temp_file_path)

        if stat_before.st_mtime == stat_after.st_mtime:
            print("No changes detected. Aborting edit.")
            os.unlink(temp_file_path)
            return None

        with open(temp_file_path, "r", encoding="utf-8") as fp:
            updated_data = json.load(fp)

        os.unlink(temp_file_path)
        print_success("Successfully loaded updated data.")
        return updated_data

    except FileNotFoundError:
        print_error(
            f"Editor '{editor}' not found. Please check your VISUAL/EDITOR environment variables."
        )
        return None
    except json.JSONDecodeError:
        print_error(
            "Invalid JSON in the temporary file. The changes could not be loaded."
        )
        print(f"The invalid file was left at: {temp_file_path}")
        return None
    except Exception as e:
        print_error(f"An unexpected error occurred during the edit process: {e}")
        if "temp_file_path" in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return None


def extract_model_maker_from_checkpoint(checkpoint: str) -> str:
    """Extract the model maker from a HuggingFace checkpoint string."""
    parts = checkpoint.split("/")
    if len(parts) >= 2:
        return parts[0]
    else:
        # If no organization in checkpoint, try to guess from model name
        return "unknown"


def build_model_info_from_hf(
    checkpoint: str,
    source_type: str,
    quantization: Optional[str] = None,
    use_hf_mcp: bool = False,
) -> dict:
    """
    Build model_info dictionary from HuggingFace model information.

    Args:
        checkpoint: HuggingFace model checkpoint (e.g., "mistralai/Magistral-Small-2506")
        source_type: Either "safetensor" or "gguf"
        quantization: Quantization type for gguf models (e.g., "Q6_K")

    Returns:
        Dictionary with model information ready for registry
    """
    print(f"Fetching model information from HuggingFace for {checkpoint}...")

    try:
        hf_info_json = get_combined_hf_model_info(checkpoint, use_hf_mcp=use_hf_mcp)

        # Parse the JSON string returned by get_combined_hf_model_info
        hf_info = json.loads(hf_info_json)

        # Extract model maker from checkpoint and use full checkpoint as model name
        model_maker = extract_model_maker_from_checkpoint(checkpoint)
        model_name = checkpoint  # Use full HF checkpoint as model name

        # Build model_info dictionary
        model_info = {
            "model_maker": model_maker,
            "model_name": model_name,
            "params_count": hf_info.get("params_count"),
            "context_length": hf_info.get("context_length"),
            "license": hf_info.get("license", "unknown"),
            "requires_auth": hf_info.get("requires_auth"),
        }

        # Set quantization based on source type
        if source_type == "gguf" and quantization:
            model_info["quantization"] = quantization
        elif source_type == "safetensor":
            # For safetensor, use quantization from HF API or default to fp16
            model_info["quantization"] = hf_info.get("quantization")

        # Remove None values
        model_info = {k: v for k, v in model_info.items() if v is not None}

        print_success("Successfully extracted model information from HuggingFace")
        return model_info

    except Exception as e:
        print_error(f"Error fetching model information: {e}")
        raise


def build_source_info(
    checkpoint: str,
    source_type: str,
    requires_auth: bool = False,
) -> dict:
    """
    Build source_info dictionary for the registry.

    Args:
        checkpoint: HuggingFace model checkpoint
        source_type: Either "safetensor" or "gguf"
        requires_auth: Whether the model requires authentication

    Returns:
        Dictionary with source information ready for registry
    """
    if source_type == "safetensor":
        # Map safetensor to huggingface_api source type
        source_info = {
            "source_type": "huggingface_api",
            "source_identifier": json.dumps(
                {"loader_class": "AutoModelForCausalLM", "checkpoint": checkpoint}
            ),
            "requires_auth": requires_auth,
        }
    elif source_type == "gguf":
        # Map gguf to gguf_file source type
        # Use checkpoint and quantization for pattern-based file discovery
        source_info = {
            "source_type": "gguf_file",
            "source_identifier": json.dumps(
                {
                    "checkpoint": checkpoint,
                    "loader_kwargs": {
                        "n_ctx": 2048,
                    },
                }
            ),
            "requires_auth": requires_auth,
        }
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

    return source_info


def handle_add_model(parsed_args):
    """
    Add a model to the global registry and optionally generate a fingerprint.

    This command fetches model information from HuggingFace, adds it to the registry,
    and optionally generates a fingerprint for the model.
    """

    if parsed_args.env:
        try:
            print(f"Loading environment settings for '{parsed_args.env}'...")
            load_env(parsed_args.env)
        except AssertionError as e:
            print_error(f"Invalid environment specified: {e}")
            return 1

    print("VAIL Model Registry - Adding Model")
    print(f"Checkpoint: {parsed_args.checkpoint}")
    print(f"Source Type: {parsed_args.source_type}")

    # Validate arguments
    if parsed_args.source_type == "gguf" and not parsed_args.quantization:
        print_error("Quantization type is required for gguf models")
        return 1

    # Build initial model and source info
    try:
        model_info = build_model_info_from_hf(
            parsed_args.checkpoint,
            parsed_args.source_type,
            parsed_args.quantization,
            parsed_args.use_hf_mcp,
        )
        # Determine requires_auth based on CLI flag or HF metadata
        requires_auth = parsed_args.requires_auth or bool(
            model_info.get("requires_auth")
        )
        source_info = build_source_info(
            parsed_args.checkpoint,
            parsed_args.source_type,
            requires_auth,
        )
    except Exception as e:
        print_error(f"Failed to build initial model data: {e}")
        return 1

    combined_data = {"model_info": model_info, "source_info": source_info}

    # Loop for pre-add confirmation and editing
    while True:
        print("\nThe following data will be added to the registry:")
        print_table("Model Info", combined_data["model_info"])
        print_table("Source Info", combined_data["source_info"])

        try:
            action = (
                input(
                    "\nChoose an action: [P]roceed, [E]dit, [C]ancel (default: P): "
                ).upper()
                or "P"
            )
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")
            return 1

        if action == "P":
            break
        elif action == "E":
            updated_data = _edit_data_in_editor(combined_data)
            if (
                updated_data
                and "model_info" in updated_data
                and "source_info" in updated_data
            ):
                combined_data = updated_data
            else:
                print_error("Edit was aborted or the edited file was invalid.")
            continue
        elif action == "C":
            print("Operation cancelled.")
            return 1
        else:
            print_error("Invalid option. Please choose P, E, or C.")

    # Loop for adding the model to the registry, with retry on failure
    while True:
        try:
            print("\nAdding model to registry...")

            # Validate model and source info
            validate_model_info(combined_data["model_info"])
            validate_source_info(combined_data["source_info"])

            # Get registry and add model
            registry = get_registry()
            if registry.registry_type == "local":
                print_error("Local registry does not support manual model addition")
                return 1

            # Add model to registry
            model_id = registry.add_model(combined_data["model_info"])

            # Add source to registry
            source_id = registry.add_model_source(
                model_id,
                combined_data["source_info"]["source_type"],
                {
                    "source_identifier": combined_data["source_info"][
                        "source_identifier"
                    ],
                    "requires_auth": combined_data["source_info"].get(
                        "requires_auth", False
                    ),
                },
            )

            print_success("Successfully added model to registry")
            print(f"  Model ID: {model_id}")
            print(f"  Source ID: {source_id}")

            # If successful, break the loop
            break

        except Exception as e:
            print_error("Failed to add model to registry")
            print_error(f"Error details: {str(e)}")

            try:
                edit_action = (
                    input(
                        "\nChoose an action: [E]dit data and retry, or [A]bort (default: A): "
                    ).upper()
                    or "A"
                )
            except (EOFError, KeyboardInterrupt):
                print("\nOperation aborted.")
                return 1

            if edit_action == "E":
                updated_data = _edit_data_in_editor(combined_data)
                if (
                    updated_data
                    and "model_info" in updated_data
                    and "source_info" in updated_data
                ):
                    combined_data = updated_data
                else:
                    print_error("Edit was aborted or invalid. Aborting operation.")
                    return 1
            else:
                print("Operation aborted.")
                return 1

    print("\nModel addition process completed!")
    return 0


def admin_main(args=None):
    """Entry point for the admin CLI."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="VAIL Model Registry Admin CLI - Admin-only functionality"
    )
    subparsers = parser.add_subparsers(
        dest="admin_subcommand", help="Admin subcommand to run"
    )

    # Add model subcommand
    add_model_parser = subparsers.add_parser(
        "add-model",
        help="Add a model to the registry and optionally generate fingerprint",
    )

    # Add arguments to the add-model subcommand
    add_model_parser.add_argument(
        "--checkpoint",
        "-c",
        type=str,
        required=True,
        help="HuggingFace model checkpoint (e.g., 'mistralai/Magistral-Small-2506')",
    )
    add_model_parser.add_argument(
        "--source-type",
        "-s",
        type=str,
        required=True,
        choices=["gguf", "safetensor"],
        help="Type of model source: 'gguf' or 'safetensor'",
    )

    add_model_parser.add_argument(
        "--quantization",
        "-q",
        type=str,
        help="Quantization type for gguf models (e.g., 'Q6_K')",
    )

    add_model_parser.add_argument(
        "--requires-auth",
        action="store_true",
        help="Whether the model requires authentication",
    )

    add_model_parser.add_argument(
        "--env",
        type=str,
        help="Specify environment ('local' or 'test'). Loads settings from corresponding .env file.",
    )

    add_model_parser.add_argument(
        "--use-hf-mcp",
        action="store_true",
        help="Use HuggingFace MCP for fetching model information (default: False, uses traditional extraction methods)",
    )

    parsed_args = parser.parse_args(args)

    if not parsed_args.admin_subcommand:
        parser.print_help()
        return 1

    try:
        if parsed_args.admin_subcommand == "add-model":
            return handle_add_model(parsed_args)
        else:
            print_error(f"Unknown admin subcommand: {parsed_args.admin_subcommand}")
            return 1
    except KeyboardInterrupt:
        log.info("Admin operation stopped by user.")
        return 0
    except Exception as e:
        log.exception(f"Admin operation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(admin_main())
