#!/usr/bin/env python
"""
Command-line interface for the VAIL Model Registry.
"""

import argparse
import getpass
import json
import logging
import os
import sys

from dotenv import load_dotenv

from vail.fingerprint.metrics import l1_similarity

# Add import for browse functionality
from vail.registry.browse import interactive_browse
from vail.registry.local_interface import LocalRegistryInterface
from vail.registry.models import ModelFilterCriteria
from vail.vail_mcp.server import get_registry, mcp_server

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


# Helper function to update .vail.env file
def update_vail_env_file(key: str, value: str):
    """Updates or adds a key-value pair to the .vail.env file."""
    env_file_path = ".vail.env"
    env_vars = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()

    env_vars[key] = value

    with open(env_file_path, "w") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\\n")
    log.info(f"Updated {key} in {env_file_path}")


# Helper function to prompt for and save Hugging Face token
def prompt_and_save_hf_token():
    """Prompts the user for their Hugging Face token and saves it if provided."""
    if not os.environ.get("HUGGINGFACE_TOKEN"):  # Only prompt if not already set
        try:
            token = getpass.getpass(
                "Enter your Hugging Face API Token (or press Enter to skip): "
            )
            if token:
                update_vail_env_file("HUGGINGFACE_TOKEN", token)
                os.environ["HUGGINGFACE_TOKEN"] = token  # Also set in current session
                print(
                    "Hugging Face token has been saved to .vail.env and set for the current session."
                )
            else:
                print("Skipped Hugging Face token setup.")
        except Exception as e:
            log.warning(f"Could not read or save Hugging Face token: {e}")


def mcp_server_main(args=None):
    """Run the MCP server with the given arguments."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Run the VAIL Model Registry MCP server."
    )
    parser.add_argument(
        "--registry-type",
        type=str,
        choices=["local", "global"],
        default="local",
        help="Type of registry to use ('local' or 'global'). Default is 'local'.",
    )
    parser.add_argument(
        "--local-db-path",
        type=str,
        default=os.environ.get("LOCAL_DB_PATH", "local_registry.duckdb"),
        help="Path to the local DuckDB database file. Used if --registry-type is 'local'. Default is 'local_registry.duckdb' or the LOCAL_DB_PATH env var.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("FASTMCP_PORT", "8080")),
        help="Port to run the MCP server on. Default is 8080 or the FASTMCP_PORT env var.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("FASTMCP_HOST", "127.0.0.1"),
        help="Host to run the MCP server on. Default is 127.0.0.1 or the FASTMCP_HOST env var.",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string for the global registry. Uses the DATABASE_URL env var if not specified.",
    )
    parser.add_argument(
        "--huggingface-token",
        type=str,
        default=os.environ.get("HUGGINGFACE_TOKEN"),
        help="Hugging Face API token for accessing restricted models. Uses the HUGGINGFACE_TOKEN env var if not specified.",
    )

    parsed_args = parser.parse_args(args)

    log.info(f"Using registry type: {parsed_args.registry_type}")
    if parsed_args.registry_type == "local":
        log.info(f"Local DB path: {parsed_args.local_db_path}")
        # Verify the database file exists or can be created
        db_dir = os.path.dirname(parsed_args.local_db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                log.info(f"Created directory for local database: {db_dir}")
            except Exception as e:
                log.error(f"Failed to create directory for local database: {e}")
                sys.exit(1)

    # Set environment variables from arguments if provided
    if parsed_args.database_url:
        os.environ["DATABASE_URL"] = parsed_args.database_url

    if parsed_args.huggingface_token:
        os.environ["HUGGINGFACE_TOKEN"] = parsed_args.huggingface_token

    try:
        # Initialize the registry before starting the server
        get_registry(
            registry_type=parsed_args.registry_type,
            local_db_path=parsed_args.local_db_path,
        )

        # Set host and port from arguments
        os.environ["FASTMCP_HOST"] = parsed_args.host
        os.environ["FASTMCP_PORT"] = str(parsed_args.port)

        log.info(f"MCP server will listen on {parsed_args.host}:{parsed_args.port}")

        # Let the FastMCP SDK handle the communication protocol
        mcp_server.run()
        log.info("MCP server run() finished.")
        return 0
    except KeyboardInterrupt:
        log.info("MCP server stopped by user.")
        return 0
    except Exception as e:
        log.exception(f"MCP server failed: {e}")
        return 1


def browse_registry_main(args=None):
    """Run the interactive registry browser with the given arguments."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Browse the VAIL Model Registry.")
    parser.add_argument(
        "--local-db-path",
        type=str,
        default=os.environ.get("LOCAL_DB_PATH", "local_registry.duckdb"),
        help="Path to the local DuckDB database file. Default is 'local_registry.duckdb' or the LOCAL_DB_PATH env var.",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string for the global registry. Uses the DATABASE_URL env var if not specified.",
    )

    parsed_args = parser.parse_args(args)

    # Set environment variables from arguments if provided
    if parsed_args.database_url:
        os.environ["DATABASE_URL"] = parsed_args.database_url

    try:
        interactive_browse(local_db_path=parsed_args.local_db_path)
        return 0
    except KeyboardInterrupt:
        log.info("Registry browser stopped by user.")
        return 0
    except Exception as e:
        log.exception(f"Registry browser failed: {e}")
        return 1


def sync_registry_main(args=None):
    """Sync models from the global registry to the local registry with optional filters."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Sync models from the global registry to the local registry."
    )
    parser.add_argument(
        "--local-db-path",
        type=str,
        default=os.environ.get("LOCAL_DB_PATH", "local_registry.duckdb"),
        help="Path to the local DuckDB database file. Default is 'local_registry.duckdb' or the LOCAL_DB_PATH env var.",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string for the global registry. Uses the DATABASE_URL env var if not specified.",
    )
    # Add filter options
    parser.add_argument(
        "--maker",
        type=str,
        help="Filter by model maker (e.g., 'anthropic', 'meta', 'mistral')",
    )
    parser.add_argument(
        "--max-params",
        type=int,
        help="Filter by models with less than or equal to this many parameters",
        dest="params_count",
    )
    parser.add_argument(
        "--quantization",
        type=str,
        help="Filter by quantization type (e.g., 'none', 'int8', 'int4')",
    )
    parser.add_argument(
        "--license",
        type=str,
        help="Filter by model license (e.g., 'mit', 'apache-2.0')",
    )
    parser.add_argument(
        "--ignore-last-sync",
        action="store_true",
        help="Ignore the last sync timestamp and sync all models that match the filters",
    )

    parsed_args = parser.parse_args(args)

    # Set environment variables from arguments if provided
    if parsed_args.database_url:
        os.environ["DATABASE_URL"] = parsed_args.database_url

    database_url = parsed_args.database_url
    if not database_url:
        log.error(
            "No database URL provided. Please specify the --database-url parameter or set the DATABASE_URL environment variable."
        )
        return 1

    # Check if any filters are specified
    has_filters = any(
        [
            parsed_args.maker,
            parsed_args.params_count,
            parsed_args.quantization,
            parsed_args.license,
        ]
    )

    try:
        log.info(
            f"Initializing connection to local registry at {parsed_args.local_db_path}"
        )
        local_registry = LocalRegistryInterface(
            connection_string=database_url,
            local_db_path=parsed_args.local_db_path,
        )

        # Create filter criteria from command line arguments
        filter_criteria = ModelFilterCriteria(
            maker=parsed_args.maker,
            params_count_lte=parsed_args.params_count,  # Using lte since --max-params means "less than or equal to"
            quantization=parsed_args.quantization,
            license=parsed_args.license,
        )

        print("Syncing models from global registry to local registry")
        if has_filters:
            log.info(f"Using filters: {filter_criteria.to_filter_string()}")

        result = local_registry.sync_models_from_global(
            filters=filter_criteria, use_last_sync_time=not parsed_args.ignore_last_sync
        )

        if result:
            success_count, processed_count = result
            log.info(
                f"Sync completed successfully. Processed {processed_count} models, successfully synced {success_count}."
            )
            return 0
        else:
            log.error("Sync failed.")
            return 1
    except KeyboardInterrupt:
        log.info("Registry sync stopped by user.")
        return 0
    except Exception as e:
        log.exception(f"Registry sync failed: {e}")
        return 1


def init_registry_main(args=None):
    """Initialize a new VAIL Model Registry with the given arguments."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Initialize a new VAIL Model Registry."
    )
    parser.add_argument(
        "--local-db-path",
        type=str,
        default=os.environ.get("LOCAL_DB_PATH", "local_registry.duckdb"),
        help="Path to the local DuckDB database file. Default is 'local_registry.duckdb' or the LOCAL_DB_PATH env var.",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string for the global registry. Uses the DATABASE_URL env var if not specified.",
    )
    parser.add_argument(
        "--no-env-file",
        action="store_true",
        help="Do not create a .vail.env.default file",
    )
    parser.add_argument(
        "--sync-models",
        action="store_true",
        default=True,
        help="Sync lightweight model metadata (under 3B parameters) after initialization. Default: True",
    )
    parser.add_argument(
        "--no-sync-models",
        action="store_false",
        dest="sync_models",
        help="Do not sync any model metadata after initialization",
    )
    parser.add_argument(
        "--sync-all-models",
        action="store_true",
        help="Sync all models' metadata regardless of size (can be slow)",
    )
    parser.add_argument(
        "--huggingface-token",
        type=str,
        default=os.environ.get("HUGGINGFACE_TOKEN"),
        help="Hugging Face API token. If not provided and not in .vail.env, you may be prompted. Uses HUGGINGFACE_TOKEN env var.",
    )

    parsed_args = parser.parse_args(args)

    print("Initializing VAIL Model Registry...")
    print(f"Local DB path: {parsed_args.local_db_path}")

    # If a DATABASE_URL is provided, use it
    database_url = parsed_args.database_url
    if database_url:
        print(f"Using provided database URL for global registry: {database_url}")
    else:
        print(
            "No database URL provided, using default global registry URL. You can set up your own database URL in .vail.env"
        )

    # Prompt for Hugging Face token if not set by arg or existing env var
    if not parsed_args.huggingface_token:
        prompt_and_save_hf_token()
    elif (
        parsed_args.huggingface_token
        and parsed_args.huggingface_token != os.environ.get("HUGGINGFACE_TOKEN")
    ):
        # If token is provided as an argument and is different from env, update .vail.env
        update_vail_env_file("HUGGINGFACE_TOKEN", parsed_args.huggingface_token)
        os.environ["HUGGINGFACE_TOKEN"] = parsed_args.huggingface_token
        print(
            "Hugging Face token updated from command line argument and saved to .vail.env."
        )

    try:
        # Initialize the registry
        success = LocalRegistryInterface.setup_local_registry(
            local_db_path=parsed_args.local_db_path, database_url=database_url
        )

        if not success:
            log.error("Failed to initialize the VAIL Model Registry.")
            return 1

        log.info("VAIL Model Registry initialized successfully!")
        if not parsed_args.no_env_file:
            env_file_path = ".vail.env"
            env_content = [
                "# VAIL Model Registry Environment Variables",
                "",
                "# Required: PostgreSQL Database for global registry",
            ]
            if database_url:
                env_content.append(f"DATABASE_URL={database_url}")
            else:
                database_url = "postgresql://registry_user:VAIL_2025_READ_ONLY@ep-cold-leaf-a643eoax-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"
                env_content.append(
                    "# Default Global Registry URL (Read Only Access to Models in VAIL)"
                )
                env_content.append(f"DATABASE_URL={database_url}")
            env_content.extend(
                [
                    "",
                    "# Optional: Path to local DuckDB database",
                    f"LOCAL_DB_PATH={parsed_args.local_db_path}",
                    "",
                    "# Optional: Hugging Face Token for accessing restricted models",
                    "HUGGINGFACE_TOKEN=your_huggingface_token",
                    "",
                    "# Optional: MCP server settings",
                    "FASTMCP_HOST=127.0.0.1",
                    "FASTMCP_PORT=8080",
                ]
            )
            with open(env_file_path, "w") as f:
                f.write("\n".join(env_content))
            print(
                f"Created environment file at {env_file_path}. Edit this file to customize your registry."
            )

        # Sync models if requested and database_url is provided
        if parsed_args.sync_models and database_url:
            if parsed_args.sync_all_models:
                print(
                    "Initializing local registry with all models from the global registry..."
                )
                local_registry = LocalRegistryInterface(
                    connection_string=database_url,
                    local_db_path=parsed_args.local_db_path,
                )
                result = local_registry.sync_models_from_global(
                    use_last_sync_time=False
                )
            else:
                # Default: Sync only models with less than 3B parameters
                print(
                    "Initializing local registry with lightweight models (under 3B parameters) from the global registry..."
                )
                local_registry = LocalRegistryInterface(
                    connection_string=database_url,
                    local_db_path=parsed_args.local_db_path,
                )

                filter_criteria = ModelFilterCriteria(params_count_lte=3_000_000_000)
                result = local_registry.sync_models_from_global(
                    filters=filter_criteria, use_last_sync_time=False
                )

            if result:
                success_count, processed_count = result
                print(
                    f"Model sync completed. Synced {success_count} out of {processed_count} processed models."
                )
            else:
                log.warning(
                    "Model sync failed or was incomplete. You can run 'vail registry sync' later to retry."
                )
        elif parsed_args.sync_models and not database_url:
            log.warning(
                "Cannot sync models: No database URL provided. Run 'vail registry sync' after setting up your database connection."
            )

        print("\nNext steps:")
        if not database_url:
            print(
                "1. Set up your environment variables (copy .vail.env.default to .env and edit)"
            )
            print("2. Browse the registry: vail registry browse")
            print("3. Start the MCP server: vail mcp run")
        else:
            print("1. Browse the registry: vail registry browse")
            print("2. Start the MCP server: vail mcp run")
            if not parsed_args.sync_models:
                print("3. Sync models to your local registry: vail registry sync")

        return 0
    except Exception as e:
        log.exception(f"Registry initialization failed: {e}")
        return 1


def model_tools_main(args=None):
    """Handle model-related commands like viewing model information."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Model-related commands for the registry."
    )
    subparsers = parser.add_subparsers(
        dest="model_subcommand", help="Model subcommand to run"
    )

    # View subcommand
    view_parser = subparsers.add_parser(
        "view", help="View information about a specific model"
    )
    view_parser.add_argument(
        "model_id",
        type=str,
        help="ID of the model to view metadata information for (can be local ID like '1' or canonical ID like 'microsoft/phi-3-mini_42')",
    )
    view_parser.add_argument(
        "--format",
        type=str,
        choices=["json", "pretty"],
        default="pretty",
        help="Output format: 'json' for machine-readable, 'pretty' for human-readable. Default: pretty",
    )
    view_parser.add_argument(
        "--local-db-path",
        type=str,
        default=os.environ.get("LOCAL_DB_PATH", "local_registry.duckdb"),
        help="Path to the local DuckDB database file. Default is 'local_registry.duckdb' or the LOCAL_DB_PATH env var.",
    )
    view_parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string for the global registry. Uses the DATABASE_URL env var if not specified.",
    )

    # Compare subcommand
    compare_parser = subparsers.add_parser(
        "compare", help="Compare fingerprints between two models"
    )
    compare_parser.add_argument(
        "model_id1",
        type=str,
        help="ID of the first model to compare (can be local ID like '1' or canonical ID like 'microsoft/phi-3-mini_42')",
    )
    compare_parser.add_argument(
        "model_id2",
        type=str,
        help="ID of the second model to compare (can be local ID like '1' or canonical ID like 'microsoft/phi-3-mini_42')",
    )
    compare_parser.add_argument(
        "--fingerprint-type",
        type=str,
        default="input_output",
        help="Type of fingerprint to compare. Default: input_output",
    )
    compare_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information about the models being compared",
    )
    compare_parser.add_argument(
        "--local-db-path",
        type=str,
        default=os.environ.get("LOCAL_DB_PATH", "local_registry.duckdb"),
        help="Path to the local DuckDB database file. Default is 'local_registry.duckdb' or the LOCAL_DB_PATH env var.",
    )
    compare_parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string for the global registry. Uses the DATABASE_URL env var if not specified.",
    )

    # Similarities subcommand
    similarities_parser = subparsers.add_parser(
        "similarities",
        help="Show L1 similarity matrix for models with color-coded visualization",
    )
    similarities_parser.add_argument(
        "--model-ids",
        type=str,
        help="Comma-separated list of model IDs to compare (can be local IDs like '1,2,3' or canonical IDs like 'microsoft/phi-3-mini_42,google/t5-small_27'). If not provided, all models will be compared.",
    )
    similarities_parser.add_argument(
        "--fingerprint-type",
        type=str,
        default="input_output",
        help="Type of fingerprint to compare. Default: input_output",
    )
    similarities_parser.add_argument(
        "--threshold",
        type=float,
        help="Minimum similarity threshold to filter results",
    )
    similarities_parser.add_argument(
        "--metric",
        type=str,
        choices=[
            "cosine_similarity",
            "euclidean_similarity",
            "dot_product",
            "l1_similarity",
        ],
        default="l1_similarity",
        help="Similarity metric to use for filtering and sorting. Default: l1_similarity",
    )
    similarities_parser.add_argument(
        "--format",
        type=str,
        choices=["json", "matrix", "csv"],
        default="matrix",
        help="Output format. Default: matrix",
    )
    similarities_parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of results to show",
    )
    similarities_parser.add_argument(
        "--compact",
        action="store_true",
        help="Use ultra-compact matrix format with single-character abbreviations",
    )
    similarities_parser.add_argument(
        "--local-db-path",
        type=str,
        default=os.environ.get("LOCAL_DB_PATH", "local_registry.duckdb"),
        help="Path to the local DuckDB database file. Default is 'local_registry.duckdb' or the LOCAL_DB_PATH env var.",
    )
    similarities_parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string for the global registry. Uses the DATABASE_URL env var if not specified.",
    )

    # Find-similar subcommand
    find_similar_parser = subparsers.add_parser(
        "find-similar", help="Find models similar to a specific model"
    )
    find_similar_parser.add_argument(
        "model_id",
        type=str,
        help="ID of the reference model to find similar models for (can be local ID like '1' or canonical ID like 'microsoft/phi-3-mini_42')",
    )
    find_similar_parser.add_argument(
        "--fingerprint-type",
        type=str,
        default="input_output",
        help="Type of fingerprint to compare. Default: input_output",
    )
    find_similar_parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="Minimum similarity threshold. Default: 0.95",
    )
    find_similar_parser.add_argument(
        "--metric",
        type=str,
        choices=[
            "cosine_similarity",
            "euclidean_similarity",
            "dot_product",
            "l1_similarity",
        ],
        default="l1_similarity",
        help="Similarity metric to use. Default: l1_similarity",
    )
    find_similar_parser.add_argument(
        "--format",
        type=str,
        choices=["json", "table", "csv"],
        default="table",
        help="Output format. Default: table",
    )
    find_similar_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of results to show. Default: all models",
    )
    find_similar_parser.add_argument(
        "--local-db-path",
        type=str,
        default=os.environ.get("LOCAL_DB_PATH", "local_registry.duckdb"),
        help="Path to the local DuckDB database file. Default is 'local_registry.duckdb' or the LOCAL_DB_PATH env var.",
    )
    find_similar_parser.add_argument(
        "--database-url",
        type=str,
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection string for the global registry. Uses the DATABASE_URL env var if not specified.",
    )

    parsed_args = parser.parse_args(args)

    if not parsed_args.model_subcommand:
        parser.print_help()
        return 1

    # Check if database URL is provided
    database_url = parsed_args.database_url
    if not database_url:
        log.error(
            "No database URL provided. Please specify the --database-url parameter or set the DATABASE_URL environment variable."
        )
        return 1

    try:
        # Initialize the local registry interface with database_url
        registry = LocalRegistryInterface(
            connection_string=database_url, local_db_path=parsed_args.local_db_path
        )

        # Handle view subcommand
        if parsed_args.model_subcommand == "view":
            # Get the model information using find_model
            model = registry.find_model(parsed_args.model_id)

            if not model:
                log.error(
                    f"Model with ID '{parsed_args.model_id}' not found in the local registry."
                )
                return 1

            # Get model sources from the model_info
            sources = model.model_info.get("sources", [])

            # Combine model info with sources
            model_info = {"model": model.model_info, "sources": sources}

            # Display the information
            if parsed_args.format == "json":
                print(json.dumps(model_info, indent=2))
            else:
                print(f"\nModel Information for ID: {parsed_args.model_id}")
                print("=" * 80)
                print(f"Name: {model.model_info.get('model_name', 'N/A')}")
                print(f"Maker: {model.model_info.get('model_maker', 'N/A')}")
                print(f"Local ID: {model.model_info.get('id', 'N/A')}")
                # Show canonical ID if available
                canonical_id = model.model_info.get("canonical_id")
                if canonical_id:
                    print(f"Canonical ID: {canonical_id}")
                print(f"Parameters: {model.model_info.get('params_count', 'N/A'):,}")
                print(
                    f"Context Length: {model.model_info.get('context_length', 'N/A')}"
                )
                print(f"License: {model.model_info.get('license', 'N/A')}")
                print(f"Description: {model.model_info.get('description', 'N/A')}")
                print(f"Created: {model.model_info.get('created_at', 'N/A')}")
                # Show sources
                print("\nSources:")
                print("-" * 80)
                if not sources:
                    print("No sources available")
                else:
                    for i, source in enumerate(sources, 1):
                        print(f"Source #{i}: {source.get('source_type', 'N/A')}")
                        print(f"  ID: {source.get('source_id', 'N/A')}")
                        print(f"  Location: {source.get('source_identifier', {})}")
                        print()

            return 0
        elif parsed_args.model_subcommand == "compare":
            # Get model information if verbose output is requested
            if parsed_args.verbose:
                model1 = registry.find_model(parsed_args.model_id1)
                model2 = registry.find_model(parsed_args.model_id2)

                if not model1:
                    log.error(
                        f"Model with ID '{parsed_args.model_id1}' not found in the local registry."
                    )
                    return 1
                if not model2:
                    log.error(
                        f"Model with ID '{parsed_args.model_id2}' not found in the local registry."
                    )
                    return 1

                print("\nComparing models:")

                # Display model 1 info with canonical ID if available
                model1_name = model1.model_info.get("model_name", parsed_args.model_id1)
                model1_canonical = model1.model_info.get("canonical_id")
                model1_display = (
                    f"Model 1: {model1_name} (Input: {parsed_args.model_id1}"
                )
                if model1_canonical:
                    model1_display += f", Canonical: {model1_canonical}"
                model1_display += ")"
                print(model1_display)

                # Display model 2 info with canonical ID if available
                model2_name = model2.model_info.get("model_name", parsed_args.model_id2)
                model2_canonical = model2.model_info.get("canonical_id")
                model2_display = (
                    f"Model 2: {model2_name} (Input: {parsed_args.model_id2}"
                )
                if model2_canonical:
                    model2_display += f", Canonical: {model2_canonical}"
                model2_display += ")"
                print(model2_display)

                print(f"Fingerprint type: {parsed_args.fingerprint_type}")
                print("-" * 80)

            # Get fingerprint vectors for both models
            fingerprint1 = registry.get_fingerprint(
                parsed_args.model_id1, parsed_args.fingerprint_type
            )
            fingerprint2 = registry.get_fingerprint(
                parsed_args.model_id2, parsed_args.fingerprint_type
            )

            if fingerprint1 is None:
                log.error(
                    f"No '{parsed_args.fingerprint_type}' fingerprint found for model '{parsed_args.model_id1}'."
                )
                return 1
            if fingerprint2 is None:
                log.error(
                    f"No '{parsed_args.fingerprint_type}' fingerprint found for model '{parsed_args.model_id2}'."
                )
                return 1

            # The get_fingerprint method directly returns numpy arrays
            vector1 = fingerprint1
            vector2 = fingerprint2

            if len(vector1) == 0 or len(vector2) == 0:
                log.error("Fingerprint vectors are empty.")
                return 1

            if len(vector1) != len(vector2):
                log.error(
                    f"Fingerprint vectors have different lengths: {len(vector1)} vs {len(vector2)}."
                )
                return 1

            # Compute similarity
            similarity_score = l1_similarity(vector1, vector2)

            # Output results
            print(f"Similarity score: {similarity_score:.6f} (L1 distance)")
            print(
                "Higher scores (closer to 1.0) indicate higher similarity between models."
            )

            return 0
        elif parsed_args.model_subcommand == "similarities":
            # Get list of model IDs to compare
            if parsed_args.model_ids:
                raw_model_ids = [id.strip() for id in parsed_args.model_ids.split(",")]

                # Convert to local integer IDs for the similarity computation
                model_ids = []
                for raw_id in raw_model_ids:
                    model = registry.find_model(raw_id)
                    if not model:
                        log.error(
                            f"Model with ID '{raw_id}' not found in the local registry."
                        )
                        return 1
                    # Use the local integer ID for similarity computation
                    local_id = model.model_info.get("id")
                    if local_id:
                        model_ids.append(int(local_id))
                    else:
                        log.error(f"Could not get local ID for model '{raw_id}'")
                        return 1
            else:
                # Get all models with fingerprints of the specified type
                fingerprints = registry.get_all_fingerprints_by_type(
                    parsed_args.fingerprint_type
                )
                if not fingerprints:
                    log.error(
                        f"No models found with '{parsed_args.fingerprint_type}' fingerprints."
                    )
                    return 1
                model_ids = [fp["model_id"] for fp in fingerprints]
                if len(model_ids) < 2:
                    log.error(
                        "At least two models are required to compute similarities."
                    )
                    return 1

            # Get similarities using the Phase 1 method
            try:
                similarities = registry.get_model_similarities(
                    model_ids=model_ids,
                    fingerprint_type=parsed_args.fingerprint_type,
                    threshold=parsed_args.threshold,
                    similarity_metric=parsed_args.metric,
                )
            except Exception as e:
                log.error(f"Error computing similarities: {e}")
                return 1

            if not similarities:
                if parsed_args.threshold:
                    print(
                        f"No model pairs found with {parsed_args.metric} >= {parsed_args.threshold}"
                    )
                else:
                    print("No similarities found for the specified models.")
                return 0

            # Sort by the selected metric
            similarities.sort(key=lambda x: x[parsed_args.metric], reverse=True)

            # Apply limit if specified
            if parsed_args.limit:
                similarities = similarities[: parsed_args.limit]

            # Format and display results
            if parsed_args.format == "json":
                print(json.dumps(similarities, indent=2, default=str))
            elif parsed_args.format == "csv":
                if similarities:
                    import csv
                    import sys

                    writer = csv.DictWriter(
                        sys.stdout, fieldnames=similarities[0].keys()
                    )
                    writer.writeheader()
                    writer.writerows(similarities)
            else:  # matrix format

                def get_color_code(value, metric):
                    """Get ANSI color code based on similarity value."""
                    # For similarity metrics, higher is better
                    if value <= 0.5:
                        return "\033[91m"  # Red (low similarity)
                    elif value <= 0.8:
                        return "\033[93m"  # Yellow (medium similarity)
                    else:
                        return "\033[92m"  # Green (high similarity)

                def reset_color():
                    """Reset ANSI color to default."""
                    return "\033[0m"

                def create_smart_abbreviation(name, max_len=6):
                    """Create intelligent abbreviations for model names."""
                    if len(name) <= max_len:
                        return name

                    # Apply pattern replacements from constants
                    from vail.constants import (
                        MODEL_NAME_REPLACEMENT_ORDER,
                        MODEL_NAME_REPLACEMENTS,
                    )

                    abbreviated = name

                    # Apply replacements in the specified order to handle overlapping patterns
                    for pattern in MODEL_NAME_REPLACEMENT_ORDER:
                        if pattern in MODEL_NAME_REPLACEMENTS:
                            replacement = MODEL_NAME_REPLACEMENTS[pattern]
                            abbreviated = abbreviated.replace(pattern, replacement)

                    # Take first chars and last chars if still too long
                    if len(abbreviated) > max_len:
                        if max_len >= 4:
                            abbreviated = abbreviated[: max_len - 2] + abbreviated[-2:]
                        else:
                            abbreviated = abbreviated[:max_len]

                    return abbreviated[:max_len]

                if similarities:
                    # Get all unique models and their names
                    models_info = {}
                    for sim in similarities:
                        models_info[sim["model_id_1"]] = sim["model_name_1"]
                        models_info[sim["model_id_2"]] = sim["model_name_2"]

                    # Sort model IDs for consistent ordering
                    sorted_model_ids = sorted(models_info.keys())

                    # Create a matrix dictionary to store similarities using the selected metric
                    matrix = {}
                    for sim in similarities:
                        id1, id2 = sim["model_id_1"], sim["model_id_2"]
                        metric_value = sim[parsed_args.metric]
                        matrix[(id1, id2)] = metric_value
                        matrix[(id2, id1)] = metric_value

                    # Set diagonal values (perfect similarity with self)
                    diagonal_value = 1.0
                    for model_id in sorted_model_ids:
                        matrix[(model_id, model_id)] = diagonal_value

                    # Create abbreviations and ID mappings
                    abbrev_map = {}

                    if parsed_args.compact:
                        # Ultra-compact mode: use single letters
                        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        for i, model_id in enumerate(sorted_model_ids):
                            if i < len(alphabet):
                                abbrev_map[model_id] = alphabet[i]
                            else:
                                abbrev_map[model_id] = (
                                    f"{alphabet[i % len(alphabet)]}{i // len(alphabet)}"
                                )
                    else:
                        # Standard mode: intelligent abbreviations
                        for model_id in sorted_model_ids:
                            abbrev = create_smart_abbreviation(models_info[model_id], 6)
                            abbrev_map[model_id] = abbrev

                    # Format metric name for display
                    metric_display = parsed_args.metric.replace("_", " ").title()
                    print(
                        f"\n🎯 {metric_display} Matrix ({parsed_args.fingerprint_type} fingerprints)"
                    )

                    if parsed_args.compact:
                        # Ultra-compact format
                        col_width = 4
                        print("=" * (6 + len(sorted_model_ids) * col_width))

                        # Header with single letters
                        header = f"{'':>5} "
                        for model_id in sorted_model_ids:
                            header += f"{abbrev_map[model_id]:>3} "
                        print(header)
                        print("-" * (6 + len(sorted_model_ids) * col_width))

                        # Matrix rows
                        for row_id in sorted_model_ids:
                            row = f"{abbrev_map[row_id]:>4} "

                            for col_id in sorted_model_ids:
                                if (row_id, col_id) in matrix:
                                    value = matrix[(row_id, col_id)]
                                    if row_id == col_id:
                                        row += f"{'—':>3} "
                                    else:
                                        color = get_color_code(
                                            value, parsed_args.metric
                                        )
                                        row += f"{color}{value:>3.1f}{reset_color()} "
                                else:
                                    row += f"{'—':>3} "
                            print(row)

                        print("-" * (6 + len(sorted_model_ids) * col_width))
                    else:
                        # Standard format
                        print("=" * (12 + len(sorted_model_ids) * 7))

                        # Print header with IDs for compactness
                        header = f"{'Model':<10}"
                        for model_id in sorted_model_ids:
                            header += f"[{model_id:>2}]  "
                        print(header)
                        print("-" * (12 + len(sorted_model_ids) * 7))

                        # Print matrix rows
                        for row_id in sorted_model_ids:
                            row = f"[{row_id:>2}] {abbrev_map[row_id][:4]:<4}"

                            for col_id in sorted_model_ids:
                                if (row_id, col_id) in matrix:
                                    value = matrix[(row_id, col_id)]
                                    if row_id == col_id:
                                        # Diagonal - no color, just show dash
                                        row += f"{'—':>5}  "
                                    else:
                                        color = get_color_code(
                                            value, parsed_args.metric
                                        )
                                        # Use 2 decimal places for better readability
                                        row += f"{color}{value:>5.2f}{reset_color()}  "
                                else:
                                    row += f"{'—':>5}  "

                            print(row)

                        print("-" * (12 + len(sorted_model_ids) * 7))

                    # Color legend (metric-specific)
                    legend = f"🎨 {get_color_code(0.3, parsed_args.metric)}●{reset_color()}≤0.50  {get_color_code(0.65, parsed_args.metric)}●{reset_color()}0.50-0.80  {get_color_code(0.9, parsed_args.metric)}●{reset_color()}>0.80"

                    print(
                        f"{legend}   📊 {len(sorted_model_ids)} models, {len(similarities)} pairs"
                    )

                    # Model legend (compact, 3 columns)
                    print("\n📋 Model Legend:")
                    models_list = [
                        (model_id, models_info[model_id])
                        for model_id in sorted_model_ids
                    ]

                    if parsed_args.compact:
                        # Ultra-compact legend showing letter mappings
                        for i in range(0, len(models_list), 2):
                            line = ""
                            for j in range(2):
                                if i + j < len(models_list):
                                    model_id, name = models_list[i + j]
                                    letter = abbrev_map[model_id]
                                    line += (
                                        f"{letter}=[{model_id:>2}] {name[:32]:<32}  "
                                    )
                            print(line)
                    else:
                        # Standard legend
                        for i in range(0, len(models_list), 3):
                            line = ""
                            for j in range(3):
                                if i + j < len(models_list):
                                    model_id, name = models_list[i + j]
                                    line += f"[{model_id:>2}] {name[:24]:<24}  "
                            print(line)
                else:
                    print("No similarities to display in matrix format.")

            return 0
        elif parsed_args.model_subcommand == "find-similar":
            # Validate that the reference model exists
            model = registry.find_model(parsed_args.model_id)
            if not model:
                log.error(
                    f"Model with ID '{parsed_args.model_id}' not found in the local registry."
                )
                return 1

            # Get all models with fingerprints of the specified type
            fingerprints = registry.get_all_fingerprints_by_type(
                parsed_args.fingerprint_type
            )
            if not fingerprints:
                log.error(
                    f"No models found with '{parsed_args.fingerprint_type}' fingerprints."
                )
                return 1

            all_model_ids = [fp["model_id"] for fp in fingerprints]

            # Get the local integer ID for the reference model
            reference_local_id = int(model.model_info.get("id"))

            # Ensure the reference model has a fingerprint
            if reference_local_id not in all_model_ids:
                log.error(
                    f"Model with ID '{parsed_args.model_id}' does not have a '{parsed_args.fingerprint_type}' fingerprint."
                )
                return 1

            # Get all similarities involving the reference model
            try:
                all_similarities = registry.get_model_similarities(
                    model_ids=all_model_ids,
                    fingerprint_type=parsed_args.fingerprint_type,
                    threshold=parsed_args.threshold,  # Use the user-specified threshold
                    similarity_metric=parsed_args.metric,
                )
            except Exception as e:
                log.error(f"Error computing similarities: {e}")
                return 1

            # Filter to only include pairs with the reference model
            similar_models = []
            for sim in all_similarities:
                if (
                    sim["model_id_1"] == reference_local_id
                    or sim["model_id_2"] == reference_local_id
                ):
                    # Skip self-comparison
                    if sim["model_id_1"] != sim["model_id_2"]:
                        similar_models.append(sim)

            if not similar_models:
                print(
                    f"No models found with {parsed_args.metric} >= {parsed_args.threshold} for model {parsed_args.model_id}"
                )
                return 0

            # Sort by the selected metric (descending for similarities, ascending for distances)
            similar_models.sort(key=lambda x: x[parsed_args.metric], reverse=True)

            # Apply limit if specified
            if parsed_args.limit is not None:
                similar_models = similar_models[: parsed_args.limit]

            # Format and display results
            if parsed_args.format == "json":
                print(json.dumps(similar_models, indent=2, default=str))
            elif parsed_args.format == "csv":
                if similar_models:
                    import csv
                    import sys

                    writer = csv.DictWriter(
                        sys.stdout, fieldnames=similar_models[0].keys()
                    )
                    writer.writeheader()
                    writer.writerows(similar_models)
            else:  # table format

                def get_color_code(value, metric):
                    """Get ANSI color code based on similarity/distance value."""
                    # For similarity metrics, higher is better
                    if value <= 0.5:
                        return "\033[91m"  # Red (low similarity)
                    elif value <= 0.8:
                        return "\033[93m"  # Yellow (medium similarity)
                    else:
                        return "\033[92m"  # Green (high similarity)

                def reset_color():
                    """Reset ANSI color to default."""
                    return "\033[0m"

                def truncate_model_name(name, max_length=28):
                    """Intelligently truncate model names for better table display."""
                    if len(name) <= max_length:
                        return name

                    # Try to preserve important parts of the model name
                    # Split by '/' to separate organization from model name
                    if "/" in name:
                        org, model_name = name.split("/", 1)

                        # If model name alone fits, just use it
                        if len(model_name) <= max_length:
                            return model_name

                        # If organization is short, keep it with truncated model name
                        if len(org) <= 8:
                            remaining = max_length - len(org) - 1  # -1 for the '/'
                            if remaining > 8:
                                return f"{org}/{model_name[: remaining - 3]}..."

                        # Fallback: truncate model name part only
                        return f"{model_name[: max_length - 3]}..."

                    # No '/' found, just truncate
                    return f"{name[: max_length - 3]}..."

                # Calculate total table width for better formatting
                total_width = 90  # Increased slightly to accommodate ID column
                model_col_width = 24  # Reduced to make room for ID column
                id_col_width = 4

                # Display reference model info with canonical ID if available
                reference_name = model.model_info.get(
                    "model_name", parsed_args.model_id
                )
                reference_canonical = model.model_info.get("canonical_id")
                reference_display = f"\nModels compared to: {reference_name} (Input: {parsed_args.model_id}"
                if reference_canonical:
                    reference_display += f", Canonical: {reference_canonical}"
                reference_display += ")"
                print(reference_display)

                print(f"Fingerprint type: {parsed_args.fingerprint_type}")
                if parsed_args.threshold is not None:
                    print(
                        f"Similarity metric: {parsed_args.metric} >= {parsed_args.threshold}"
                    )
                else:
                    print(f"Sorted by: {parsed_args.metric} (showing all models)")
                print("=" * total_width)
                print(
                    f"{'ID':<{id_col_width}} {'Model':<{model_col_width}} {'L1 Sim':<8} {'Cosine':<8} {'Euclidean':<8} {'Dot Prod':<8}"
                )
                print("-" * total_width)

                for sim in similar_models:
                    # Determine which model is the similar one (not the reference)
                    if sim["model_id_1"] == reference_local_id:
                        similar_id = sim["model_id_2"]
                        similar_name = sim["model_name_2"]
                    else:
                        similar_id = sim["model_id_1"]
                        similar_name = sim["model_name_1"]

                    # Truncate model name for better display
                    truncated_name = truncate_model_name(similar_name, model_col_width)

                    # Get color for the selected metric
                    metric_value = sim[parsed_args.metric]
                    color = get_color_code(metric_value, parsed_args.metric)

                    print(
                        f"{similar_id:<{id_col_width}} "
                        f"{truncated_name:<{model_col_width}} "
                        f"{color}{sim['l1_similarity']:<8.4f}{reset_color()} "
                        f"{sim['cosine_similarity']:<8.4f} "
                        f"{sim['euclidean_similarity']:<8.4f} "
                        f"{sim['dot_product']:<8.4f}"
                    )
                print("-" * total_width)

                # Color legend (metric-specific)
                legend = f"🎨 {get_color_code(0.3, parsed_args.metric)}●{reset_color()}≤0.50  {get_color_code(0.65, parsed_args.metric)}●{reset_color()}0.50-0.80  {get_color_code(0.9, parsed_args.metric)}●{reset_color()}>0.80"

                print(legend)

                threshold_text = f">= {parsed_args.threshold}"
                print(
                    f"Found {len(similar_models)} models with {parsed_args.metric} {threshold_text}"
                )

            return 0
        else:
            log.error(f"Unknown model subcommand: {parsed_args.model_subcommand}")
            return 1
    except KeyboardInterrupt:
        log.info("Operation stopped by user.")
        return 0
    except Exception as e:
        log.exception(f"Failed to execute model command: {e}")
        return 1


def admin_main(args=None):
    """Run admin commands by delegating to the admin CLI module."""
    try:
        from vail.cli_admin import admin_main as admin_cli_main

        # Pass the remaining arguments to the admin CLI
        return admin_cli_main(args)
    except KeyboardInterrupt:
        log.info("Admin operation stopped by user.")
        return 0


def main():
    """Main entry point for the VAIL CLI."""
    parser = argparse.ArgumentParser(
        description="VAIL Model Registry command-line interface."
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Add subcommand parsers without duplicating argument definitions
    subparsers.add_parser("init", help="Initialize a new VAIL Model Registry")

    # MCP subcommand
    mcp_parser = subparsers.add_parser("mcp", help="MCP server commands")
    mcp_subparsers = mcp_parser.add_subparsers(
        dest="mcp_command", help="MCP command to run"
    )
    mcp_subparsers.add_parser("run", help="Run the MCP server")

    # Registry commands
    registry_parser = subparsers.add_parser("registry", help="Registry commands")
    registry_subparsers = registry_parser.add_subparsers(
        dest="registry_command", help="Registry command to run"
    )
    registry_subparsers.add_parser("browse", help="Browse the registry interactively")
    registry_subparsers.add_parser(
        "sync", help="Sync model metadata from the global registry to local"
    )

    # Model commands
    model_parser = subparsers.add_parser("model", help="Model-specific commands")
    model_subparsers = model_parser.add_subparsers(
        dest="model_command", help="Model command to run"
    )
    model_subparsers.add_parser("view", help="View information about a specific model")
    model_subparsers.add_parser(
        "compare", help="Compare fingerprints between two models"
    )
    model_subparsers.add_parser(
        "similarities",
        help="Show L1 similarity matrix for models with color-coded visualization",
    )
    model_subparsers.add_parser(
        "find-similar", help="Find models similar to a specific model"
    )

    # Admin commands
    subparsers.add_parser("admin", help="Admin-only commands")

    # Special handling for admin command - pass everything through without parsing
    if len(sys.argv) > 1 and sys.argv[1] == "admin":
        # Pass all arguments after "admin" to the admin CLI
        admin_args = sys.argv[2:] if len(sys.argv) > 2 else []
        sys.exit(admin_main(admin_args))

    # Parse top-level arguments only for non-admin commands
    args, remaining_args = parser.parse_known_args()

    # Load environment variables from .vail.env if it exists
    env_path = ".vail.env"
    if os.path.exists(env_path):
        load_dotenv(env_path)

    # Check if a command was given
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle commands
    if args.command == "init":
        sys.exit(init_registry_main(remaining_args))
    elif args.command == "mcp":
        if not args.mcp_command:
            mcp_parser.print_help()
            sys.exit(1)
        elif args.mcp_command == "run":
            sys.exit(mcp_server_main(remaining_args))
        else:
            mcp_parser.print_help()
            sys.exit(1)
    elif args.command == "registry":
        if not args.registry_command:
            registry_parser.print_help()
            sys.exit(1)
        elif args.registry_command == "browse":
            sys.exit(browse_registry_main(remaining_args))
        elif args.registry_command == "sync":
            sys.exit(sync_registry_main(remaining_args))
        else:
            registry_parser.print_help()
            sys.exit(1)
    elif args.command == "model":
        if not args.model_command:
            model_parser.print_help()
            sys.exit(1)
        else:
            # Add the model_command as the first element of remaining_args
            model_args = [args.model_command] + remaining_args
            sys.exit(model_tools_main(model_args))


if __name__ == "__main__":
    main()
