"""
Interactive registry browser for the VAIL Model Registry.
"""

import json
import logging
import math
import os
from typing import List

import numpy as np  # noqa: F401
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.prompt import Confirm, Prompt
from rich.table import Table

from vail.constants import FP_SIM_THRESHOLD_L1
from vail.fingerprint.metrics import l1_similarity
from vail.registry.interface import RegistryInterface
from vail.registry.local_interface import LocalRegistryInterface
from vail.registry.models import Model
from vail.utils import HardwareInfo

# Set up logging
log = logging.getLogger(__name__)

# Set up rich console for better formatting
console = Console()


def display_model_table(
    models: List[dict], total_models: int, registry_type: str = "Local"
) -> None:
    """Display a table of models."""
    table = Table(title=f"Models in {registry_type} Registry (Total: {total_models})")
    table.add_column(f"ID ({registry_type.lower()})", style="cyan")
    # Add canonical ID column for local registry
    if registry_type == "Local":
        table.add_column("Canonical ID", style="bright_cyan")
    table.add_column("Name", style="green")
    table.add_column("Maker", style="yellow")
    table.add_column("Params", style="blue")
    table.add_column("Context Length", style="magenta")
    table.add_column("Quantization", style="red")
    table.add_column("License", style="purple")
    table.add_column("Created At", style="grey50")
    table.add_column("Last Updated", style="grey50")

    for model in models:
        created_at_str = (
            model["created_at"].strftime("%B %-d, %Y") if model["created_at"] else "N/A"
        )
        last_updated_str = (
            model["last_updated"].strftime("%B %-d, %Y")
            if model.get("last_updated")
            else "N/A"
        )

        row_data = [str(model["id"])]

        # Add canonical ID if this is local registry
        if registry_type == "Local":
            canonical_id = model.get("canonical_id", "N/A")
            row_data.append(canonical_id)

        row_data.extend(
            [
                model["model_name"],
                model["model_maker"],
                str(model["params_count"]),
                str(model["context_length"]),
                model["quantization"],
                model["license"],
                created_at_str,
                last_updated_str,
            ]
        )

        table.add_row(*row_data)

    console.print(table)


def display_model_details(model: dict) -> None:
    """Display detailed information about a model."""
    console.print("\n[bold cyan]Model Details[/bold cyan]")
    console.print(f"Local ID: {model['id']}")
    # Show canonical ID if available
    if model.get("canonical_id"):
        console.print(f"Canonical ID: {model['canonical_id']}")
    console.print(f"Name: {model['model_name']}")
    console.print(f"Maker: {model['model_maker']}")
    console.print(f"Parameters: {model['params_count']}")
    console.print(f"Context Length: {model['context_length']}")
    console.print(f"Quantization: {model['quantization']}")
    console.print(f"License: {model['license']}")
    console.print(f"Created At: {model['created_at']}")

    if model["sources"]:
        console.print("\n[bold cyan]Sources[/bold cyan]")
        for source in model["sources"]:
            console.print(f"Type: {source['source_type']}")
            console.print(
                f"Identifier: {json.dumps(source['source_identifier'], indent=2)}"
            )
            console.print(f"Requires Auth: {source['requires_auth']}")


def get_models(local_registry: LocalRegistryInterface) -> List[dict]:
    """Get a list of models from the local registry."""
    models = local_registry.find_models(limit=None, offset=0)  # Fetch all models

    result = []

    for model in models:
        model_dict = model.to_dict()
        result.append(
            {
                "id": model_dict["id"],
                "model_maker": model_dict["model_maker"],
                "model_name": model_dict["model_name"],
                "canonical_id": model_dict.get("canonical_id"),  # Include canonical ID
                "params_count": model_dict["params_count"],
                "context_length": model_dict.get("context_length"),
                "quantization": model_dict["quantization"],
                "license": model_dict["license"],
                "created_at": model_dict["created_at"],
                "sources": model_dict.get("sources", []),
                "last_updated": model_dict.get("last_updated"),
            }
        )

    # Sort the models by ID before returning
    result.sort(key=lambda x: x["canonical_id"])
    return result


def sync_models_from_main(local_registry: LocalRegistryInterface) -> None:
    """Sync all models from the main registry to the local DuckDB registry."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        # Get all model IDs from main registry
        progress.add_task("[cyan]Syncing models from global registry...", total=None)
        success = local_registry.sync_models_from_global()
        if success:
            console.print("[green]Sync completed successfully![/green]")
        else:
            console.print("[red]Sync failed! Check logs for details.[/red]")


def get_global_models(global_registry: RegistryInterface) -> List[dict]:
    """Get a list of models from the global registry."""
    models = global_registry.find_models()

    result = []
    for model in models:  # Iterate over all models
        model_dict = model.to_dict()
        result.append(
            {
                "id": model_dict["id"],
                "model_maker": model_dict["model_maker"],
                "model_name": model_dict["model_name"],
                "params_count": model_dict["params_count"],
                "context_length": model_dict.get("context_length"),
                "quantization": model_dict["quantization"],
                "license": model_dict["license"],
                "created_at": model_dict["created_at"],
                "sources": model_dict["sources"],
                "last_updated": model_dict.get("last_updated"),
            }
        )

    # Sort the models by ID before returning
    result.sort(key=lambda x: int(x["id"]))
    return result


def compare_local_and_global_models(
    local_registry: LocalRegistryInterface, global_registry: RegistryInterface
) -> tuple[List[dict], List[dict]]:
    """Compare local and global registries using Model.get_hash() and return differences as lists of dicts."""
    local_models = local_registry.find_models(limit=None, offset=0)
    global_models = global_registry.find_models()

    # Create lists of tuples instead of dictionaries
    local_fingerprint_pairs = []
    for model in local_models:
        fingerprint = local_registry.get_fingerprint(
            model.model_info["id"], "input_output"
        )
        if fingerprint is not None:  # Make sure to handle None values
            local_fingerprint_pairs.append((model, fingerprint))

    global_fingerprint_pairs = []
    for model in global_models:
        fingerprint = global_registry.get_fingerprint(
            model.model_info["id"], "input_output"
        )
        if fingerprint is not None:
            global_fingerprint_pairs.append((model, fingerprint))

    # Find models in local but not in global using similarity comparison
    local_only_model_objects = []
    for local_model, local_fp in local_fingerprint_pairs:
        found_match = False
        for global_model, global_fp in global_fingerprint_pairs:
            # Using cosine similarity
            if l1_similarity(local_fp, global_fp) >= FP_SIM_THRESHOLD_L1:
                found_match = True
                break
        if not found_match:
            local_only_model_objects.append(local_model)

    # Find models in global but not in local using similarity comparison
    global_only_model_objects = []
    for global_model, global_fp in global_fingerprint_pairs:
        found_match = False
        for local_model, local_fp in local_fingerprint_pairs:
            if l1_similarity(local_fp, global_fp) >= FP_SIM_THRESHOLD_L1:
                found_match = True
                break
        if not found_match:
            global_only_model_objects.append(global_model)

    def _prepare_for_display(model_obj: Model) -> dict:
        m_dict = model_obj.to_dict()
        return {
            "id": m_dict.get("id"),
            "model_name": m_dict.get("model_name"),
            "model_maker": m_dict.get("model_maker"),
            "canonical_id": m_dict.get("canonical_id"),  # Include canonical ID
            "params_count": m_dict.get("params_count"),
            "context_length": m_dict.get("context_length"),
            "quantization": m_dict.get("quantization"),
            "license": m_dict.get("license"),
            "created_at": m_dict.get("created_at"),
            "last_updated": m_dict.get("last_updated"),
        }

    final_local_only = [_prepare_for_display(m) for m in local_only_model_objects]
    final_global_only = [_prepare_for_display(m) for m in global_only_model_objects]

    # Sort the lists by ID
    final_local_only.sort(key=lambda x: x["canonical_id"])
    final_global_only.sort(key=lambda x: int(x["id"]))

    return final_local_only, final_global_only


def display_compared_models(
    local_only_models: List[dict], global_only_models: List[dict]
) -> None:
    """Display tables of models unique to local and global registries."""
    if local_only_models:
        table_local = Table(
            title=f"Models in Local Registry Only (Total: {len(local_only_models)})"
        )
        table_local.add_column("Local ID", style="cyan")
        table_local.add_column("Canonical ID", style="bright_cyan")
        table_local.add_column("Name", style="green")
        table_local.add_column("Maker", style="yellow")
        table_local.add_column("Params", style="blue")
        table_local.add_column("Context Length", style="magenta")
        table_local.add_column("Quantization", style="red")
        table_local.add_column("License", style="purple")
        table_local.add_column("Created At", style="grey50")
        table_local.add_column("Last Updated", style="grey50")

        for model in local_only_models:
            created_at_str = (
                model["created_at"].strftime("%B %-d, %Y")
                if model.get("created_at")
                else "N/A"
            )
            last_updated_str = (
                model["last_updated"].strftime("%B %-d, %Y")
                if model.get("last_updated")
                else "N/A"
            )

            table_local.add_row(
                str(model.get("id")),
                model.get("canonical_id", "N/A"),
                model.get("model_name"),
                model.get("model_maker"),
                str(model.get("params_count")),
                str(model.get("context_length")),
                model.get("quantization"),
                model.get("license"),
                created_at_str,
                last_updated_str,
            )
        console.print(table_local)
    else:
        console.print("\n[green]No models found only in the local registry.[/green]")

    if global_only_models:
        table_global = Table(
            title=f"Models in Global Registry Only (Total: {len(global_only_models)})"
        )
        table_global.add_column("Global ID", style="cyan")
        table_global.add_column("Name", style="green")
        table_global.add_column("Maker", style="yellow")
        table_global.add_column("Params", style="blue")
        table_global.add_column("Context Length", style="magenta")
        table_global.add_column("Quantization", style="red")
        table_global.add_column("License", style="purple")
        table_global.add_column("Created At", style="grey50")
        table_global.add_column("Last Updated", style="grey50")

        for model in global_only_models:
            created_at_str = (
                model["created_at"].strftime("%B %-d, %Y")
                if model.get("created_at")
                else "N/A"
            )
            last_updated_str = (
                model["last_updated"].strftime("%B %-d, %Y")
                if model.get("last_updated")
                else "N/A"
            )

            table_global.add_row(
                str(model.get("id")),
                model.get("model_name"),
                model.get("model_maker"),
                str(model.get("params_count")),
                str(model.get("context_length")),
                model.get("quantization"),
                model.get("license"),
                created_at_str,
                last_updated_str,
            )
        console.print(table_global)
    else:
        console.print("\n[green]No models found only in the global registry.[/green]")


def sync_single_model_from_main(
    local_registry: LocalRegistryInterface, model_id: str
) -> None:
    """Sync a single model from the main registry to the local DuckDB registry."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        progress.add_task(
            f"[cyan]Syncing model {model_id} from global registry...", total=None
        )
        # Expect a tuple: (status, local_model_id_or_none)
        status, local_model_id = local_registry.copy_model_from_global(model_id)

    if status == "added":
        console.print(
            f"[green]Model {model_id} was successfully added to local registry with ID {local_model_id}![/green]"
        )
    elif status == "updated":
        console.print(
            f"[green]Model {model_id} was successfully updated in local registry (local ID: {local_model_id})![/green]"
        )
    elif status == "up_to_date":
        console.print(
            f"[blue]Model {model_id} is already up-to-date in local registry (local ID: {local_model_id}).[/blue]"
        )
    elif status == "not_found":
        console.print(f"[red]Model {model_id} not found in global registry.[/red]")
    else:  # Includes "failed" or any other unexpected status
        console.print(
            f"[red]Sync failed for model {model_id} with status '{status}'. Check logs for details.[/red]"
        )


def format_bytes(size_bytes):
    """Format bytes to human-readable format."""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.log(size_bytes, 1024))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 1)
    return f"{s} {size_name[i]}"


def display_hardware_info(hardware_info: HardwareInfo) -> None:
    """Display hardware information in a readable format."""
    console.print("\n[bold magenta]Hardware Profile (Local)[/bold magenta]")
    if hardware_info:
        console.print(f"[bold]Last Updated:[/bold] {hardware_info.last_updated}")

        console.print("\n[bold cyan]CPU Info:[/bold cyan]")
        for key, value in hardware_info.cpu.items():
            console.print(f"  {key.replace('_', ' ').title()}: {value}")

        console.print("\n[bold cyan]Memory Info:[/bold cyan]")
        for key, value in hardware_info.memory.items():
            if key.lower() == "percent":
                formatted_value = f"{value}%"
                console.print(f"  Percent Used: {formatted_value}")
            else:
                if isinstance(value, (int, float)):
                    formatted_value = format_bytes(value)
                else:
                    formatted_value = value
                console.print(f"  {key.replace('_', ' ').title()}: {formatted_value}")

        console.print("\n[bold cyan]GPU Info:[/bold cyan]")
        if hardware_info.gpu:
            for i, gpu in enumerate(hardware_info.gpu):
                console.print(f"  [bold]GPU {i}:[/bold]")
                for key, value in gpu.items():
                    console.print(f"    {key.replace('_', ' ').title()}: {value}")
        else:
            console.print("  No GPU information available.")

        console.print("\n[bold cyan]Disk Info:[/bold cyan]")
        for key, value in hardware_info.disk.items():
            if key.lower() == "percent":
                formatted_value = f"{value}%"
                console.print(f"  Percent Used: {formatted_value}")
            else:
                if isinstance(value, (int, float)):
                    formatted_value = format_bytes(value)
                else:
                    formatted_value = value
                console.print(f"  {key.replace('_', ' ').title()}: {formatted_value}")

        console.print("\n[bold cyan]System Info:[/bold cyan]")
        for key, value in hardware_info.system.items():
            console.print(f"  {key.replace('_', ' ').title()}: {value}")
    else:
        console.print(
            "[yellow]No hardware information available in the local registry.[/yellow]"
        )


def interactive_browse(local_db_path: str = "local_registry.duckdb") -> None:
    """Interactive browsing of the local registry."""
    # Check for required environment variables
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        console.print("[red]Error: DATABASE_URL environment variable is not set.[/red]")
        console.print(
            "Please set the DATABASE_URL environment variable before running this command."
        )
        console.print(
            "Example: export DATABASE_URL='postgresql://user:password@localhost:5432/dbname'"
        )
        return

    # Create local registry interface
    try:
        local_registry = LocalRegistryInterface(
            connection_string=database_url,
            local_db_path=local_db_path,
        )
        global_registry = local_registry.global_registry
    except Exception as e:
        console.print(f"[red]Error creating local registry interface: {e}[/red]")
        console.print("Please check your database connection settings and try again.")
        return

    # Suppress INFO messages by increasing log level to WARNING for vail_model_registry
    logging.getLogger("vail_model_registry").setLevel(logging.WARNING)

    while True:
        console.clear()
        console.print("[bold cyan]Model Registry Browser[/bold cyan]")
        console.print("\nOptions:")
        console.print("1. List local models")
        console.print("2. List global models")
        console.print("3. Compare Local and Global Registries")
        console.print("4. View local model details")
        console.print("5. Sync all models from main registry")
        console.print("6. Sync single model from main registry")
        console.print("7. View local hardware profile")
        console.print("8. Exit")

        choice = Prompt.ask(
            "\nEnter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8"]
        )

        if choice == "1":
            models = get_models(local_registry)
            display_model_table(models, len(models))
            input("\nPress Enter to continue...")

        elif choice == "2":
            models = get_global_models(global_registry)
            display_model_table(models, len(models), registry_type="Global")
            input("\nPress Enter to continue...")

        elif choice == "3":
            local_only, global_only = compare_local_and_global_models(
                local_registry, global_registry
            )
            display_compared_models(local_only, global_only)
            input("\nPress Enter to continue...")

        elif choice == "4":
            model_id = Prompt.ask("Enter model ID")
            all_local_models = get_models(local_registry)
            model = next(
                (m for m in all_local_models if str(m["id"]) == model_id), None
            )
            if model:
                display_model_details(model)
            else:
                console.print("[red]Model not found[/red]")
            input("\nPress Enter to continue...")

        elif choice == "5":
            if Confirm.ask(
                "This will sync all models from the main registry. Continue?"
            ):
                sync_models_from_main(local_registry)
            input("\nPress Enter to continue...")

        elif choice == "6":
            model_id = Prompt.ask("Enter model ID to sync")
            if Confirm.ask(
                f"This will sync model {model_id} from the main registry. Continue?"
            ):
                sync_single_model_from_main(local_registry, model_id)
            input("\nPress Enter to continue...")

        elif choice == "7":
            hardware_info = local_registry.get_saved_hardware_info()
            display_hardware_info(hardware_info)
            input("\nPress Enter to continue...")

        elif choice == "8":
            break
