import asyncio
import json
import os

from huggingface_hub import hf_hub_download, login
from huggingface_hub import model_info as hf_model_info_api
from huggingface_hub.utils import HfHubHTTPError
from mcp import ClientSession

# If you want to override, export HF_MCP_REMOTE=…
REMOTE_MCP_URL = os.getenv("HF_MCP_REMOTE", "https://hf.co/mcp")

# Shared constants for field name variations across different sources
POSSIBLE_PARAM_COUNT_KEYS = [
    "params_count",
    "parameters",
    "num_parameters",
    "parameter_count",
    "total",  # Used in safetensors API
]

POSSIBLE_CONTEXT_LENGTH_KEYS = [
    "context_length",
    "max_position_embeddings",
    "sequence_length",
    "max_sequence_length",
    "n_positions",
    "model_max_length",
    "seq_length",
    "max_seq_len",
    "n_ctx",
]

POSSIBLE_LICENSE_KEYS = [
    "license",
    "license_name",
]

POSSIBLE_QUANTIZATION_KEYS = [
    "quantization",
    "quantization_type",
    "dtype",
    "precision",
]

POSSIBLE_AUTH_KEYS = [
    "requires_auth",
    "gated",
    "private",
]

# Quantization formats and precision types found in model parameters
QUANTIZATION_FORMATS_AND_PRECISION = [
    "gguf",
    "gptq",
    "awq",
    "ggml",
    "fp16",
    "bf16",
    "int8",
    "int4",
    "float16",
    "bfloat16",
    "fp32",
    "f32",
]

raw_token = os.getenv("HUGGINGFACE_TOKEN")
login(token=raw_token)


async def get_raw_hf_mcp_info(model_id: str) -> str:
    """async helper that queries Hugging Face MCP for a model's metadata.
    Returns
    -------
    str
        The markdown text from the ``model_details`` tool.
    """
    from mcp.client.streamable_http import streamablehttp_client

    token = os.getenv("HUGGINGFACE_TOKEN", "")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with streamablehttp_client(REMOTE_MCP_URL, headers=headers) as (
        read,
        write,
        _,
    ):
        async with ClientSession(read, write) as sess:
            await sess.initialize()
            rsp = await sess.call_tool("model_details", {"model_id": model_id})
            # Extract text from the response content
            if rsp.content and len(rsp.content) > 0:
                return rsp.content[0].text
            else:
                return str(rsp.content)


def parse_hf_model_info_mcp(hf_info_mcp) -> dict:
    """
    Parse the MCP markdown response from huggingface-mcp-server to extract relevant model info.

    Args:
        hf_info_mcp: The markdown text response from the MCP model_details tool

    Returns:
        Dict with keys: params_count, context_length, license, quantization, requires_auth
    """
    result = {
        "params_count": None,
        "context_length": None,
        "license": None,
        "quantization": None,
        "requires_auth": False,
    }

    try:
        # Handle both string (markdown) and dict formats for backwards compatibility
        if isinstance(hf_info_mcp, str):
            text = hf_info_mcp
        elif isinstance(hf_info_mcp, dict):
            # Fallback to original dict parsing logic using POSSIBLE_ constants
            for param_key in POSSIBLE_PARAM_COUNT_KEYS:
                if param_key in hf_info_mcp:
                    result["params_count"] = hf_info_mcp[param_key]
                    break
            for ctx_key in POSSIBLE_CONTEXT_LENGTH_KEYS:
                if ctx_key in hf_info_mcp:
                    result["context_length"] = hf_info_mcp[ctx_key]
                    break
            for license_key in POSSIBLE_LICENSE_KEYS:
                if license_key in hf_info_mcp:
                    result["license"] = hf_info_mcp[license_key]
                    break
            for quant_key in POSSIBLE_QUANTIZATION_KEYS:
                if quant_key in hf_info_mcp:
                    result["quantization"] = hf_info_mcp[quant_key]
                    break
            for auth_key in POSSIBLE_AUTH_KEYS:
                if auth_key in hf_info_mcp:
                    result["requires_auth"] = bool(hf_info_mcp[auth_key])
                    break
            return result
        else:
            text = str(hf_info_mcp)

        # Parse markdown text for model information
        import re

        # Parse parameters count (e.g., "**Parameters:** 8030.3M")
        param_match = re.search(
            r"\*\*Parameters:\*\*\s*(\d+(?:\.\d+)?)\s*([KMGT]?)", text, re.IGNORECASE
        )
        if param_match:
            value = float(param_match.group(1))
            unit = param_match.group(2).upper()
            # Convert to actual number
            multipliers = {"K": 1000, "M": 1000000, "B": 1000000000, "T": 1000000000000}
            if unit in multipliers:
                value *= multipliers[unit]
            result["params_count"] = int(value)

        # Parse license from tags (e.g., `license:mit` or `license:llama3.1`)
        license_match = re.search(r"`license:([^`]+)`", text, re.IGNORECASE)
        if license_match:
            result["license"] = license_match.group(1)

        # Parse context length using various possible field names from POSSIBLE_CONTEXT_LENGTH_KEYS
        for ctx_field in POSSIBLE_CONTEXT_LENGTH_KEYS:
            # Create regex pattern for this field name
            ctx_pattern = (
                rf"\*\*{re.escape(ctx_field.replace('_', ' ').title())}:\*\*\s*(\d+)"
            )
            ctx_match = re.search(ctx_pattern, text, re.IGNORECASE)
            if ctx_match:
                result["context_length"] = int(ctx_match.group(1))
                break

        # Parse quantization info from tags using QUANTIZATION_FORMATS_AND_PRECISION
        for quant in QUANTIZATION_FORMATS_AND_PRECISION:
            if f"`{quant}`" in text.lower():
                result["quantization"] = quant
                break

        # Check for auth requirements (look for "gated", "private", etc.)
        if re.search(r"(🔒\s*gated|gated|private|requires.*auth)", text, re.IGNORECASE):
            result["requires_auth"] = True

    except Exception as e:
        print(f"Warning: Error parsing MCP markdown response: {e}")

    return result


def get_json_hf_mcp_info(model_checkpoint: str):
    """
    Attempt to get HuggingFace model info using MCP tools.
    Returns None if MCP tools are not available or fail.
    """
    try:
        # Get info via MCP, with a timeout to prevent long hangs
        mcp_response = asyncio.run(
            asyncio.wait_for(get_raw_hf_mcp_info(model_checkpoint), timeout=30.0)
        )
        parsed_info = parse_hf_model_info_mcp(mcp_response)

        # Return as JSON string to match existing interface
        return json.dumps(parsed_info, indent=2)

    except ImportError:
        # MCP tools not available
        return None
    except asyncio.TimeoutError:
        print(
            "Warning: MCP model info fetch timed out after 30 seconds for "
            f"{model_checkpoint}. Falling back to extract methods."
        )
        return None
    except Exception as e:
        print(f"Warning: MCP model info fetch failed for {model_checkpoint}: {e}")
        return None


def extract_license_from_api_info(info):
    if hasattr(info, "cardData") and info.cardData:
        for license_key in POSSIBLE_LICENSE_KEYS:
            license_val = info.cardData.get(license_key)
            if license_val:
                # Handle case where license is a list of strings
                if isinstance(license_val, list):
                    license_val = license_val[0] if license_val else None

                if isinstance(license_val, str) and license_val.lower() not in (
                    "other",
                    "none",
                    "unknown",
                ):
                    return license_val
    # Fallback for older model info formats
    if hasattr(info, "license"):
        return info.license

    return None


def extract_quantization_from_api_info(info):
    if hasattr(info, "safetensors") and info.safetensors:
        safetensors_info = info.safetensors
        param_info = safetensors_info.get("parameters")
        if param_info:
            param_keys = [x.lower() for x in list(param_info.keys())]
            set_intersect = set(QUANTIZATION_FORMATS_AND_PRECISION) & set(param_keys)
            if len(set_intersect) == 1:
                return set_intersect.pop()
    return None


def extract_params_count_from_api_info(info):
    if hasattr(info, "safetensors") and info.safetensors:
        safetensors_info = info.safetensors
        # Try different possible keys for parameter count
        for param_key in POSSIBLE_PARAM_COUNT_KEYS:
            param_count = safetensors_info.get(param_key)
            if param_count:
                return param_count

    return None


def extract_context_length_from_webpage(
    model_checkpoint: str, token: str | None = None
):
    """Fetches and parses config.json by directly downloading it."""
    config_path = None  # Initialize config_path
    try:
        config_path = hf_hub_download(
            repo_id=model_checkpoint,
            filename="config.json",
            token=token,
            resume_download=False,
            local_files_only=False,  # Set to False to allow download
            force_download=False,
        )
        with open(config_path, "r", encoding="utf-8") as f:
            config_json = json.load(f)

        # Use shared constants for context length keys
        for key in POSSIBLE_CONTEXT_LENGTH_KEYS:
            if key in config_json and isinstance(config_json.get(key), int):
                return config_json[key]

        print(
            f"DEBUG (extract_context_length_from_webpage): None of the expected keys found or value not int in parsed config.json from {model_checkpoint}. Keys: {list(config_json.keys())}"
        )
        return None
    except HfHubHTTPError as e:
        if e.response.status_code == 401:
            print(
                f"ERROR (extract_context_length_from_webpage): Authentication failed for {model_checkpoint}. Check token and model permissions. Status: {e.response.status_code}"
            )
        elif e.response.status_code == 404:
            print(
                f"ERROR (extract_context_length_from_webpage): config.json not found for {model_checkpoint}. Status: {e.response.status_code}"
            )
        else:
            print(
                f"ERROR (extract_context_length_from_webpage): HTTP error for {model_checkpoint}: {e}. Status: {e.response.status_code}"
            )
        return None
    except json.JSONDecodeError as e:
        print(
            f"ERROR (extract_context_length_from_webpage): Failed to decode JSON for {model_checkpoint}: {e}."
        )
        return None
    except Exception as e:  # pylint: disable=broad-except
        print(
            f"ERROR (extract_context_length_from_webpage): An unexpected error occurred for {model_checkpoint}: {e}"
        )
        return None
    finally:
        if config_path and os.path.exists(config_path):
            try:
                os.remove(config_path)
                print(
                    f"DEBUG (extract_context_length_from_webpage): Successfully deleted {config_path}"
                )
            except OSError as e:
                print(
                    f"ERROR (extract_context_length_from_webpage): Error deleting file {config_path}: {e}"
                )


def get_hf_model_info_via_extract_methods(model_checkpoint: str) -> dict:
    """
    Get HuggingFace model info using the traditional extract methods.

    Args:
        model_checkpoint: HuggingFace model checkpoint

    Returns:
        Dict with keys: params_count, quantization, context_length, license, requires_auth
    """
    try:
        info = hf_model_info_api(model_checkpoint)
    except Exception as e:
        print(
            f"Warning: An unexpected error occurred during hf_model_info_api for {model_checkpoint}: {e}"
        )
        info = None  # Ensure info is defined even if API call fails

    lic = extract_license_from_api_info(info)
    quant = extract_quantization_from_api_info(info)
    params = extract_params_count_from_api_info(info)
    ctx_len = extract_context_length_from_webpage(model_checkpoint, token=raw_token)

    auth_req = False
    if hasattr(info, "gated"):
        gated_status = getattr(info, "gated")
        if isinstance(gated_status, str) and gated_status.lower() in [
            "auto",
            "manual",
            "true",
        ]:
            auth_req = True
        elif isinstance(gated_status, bool):
            auth_req = gated_status

    result = {
        "params_count": params,
        "quantization": quant,
        "context_length": ctx_len,
        "license": lic,
        "requires_auth": auth_req,
    }

    return result


def get_combined_hf_model_info(model_checkpoint: str, use_hf_mcp: bool = True):
    """
    Get HuggingFace model info using a hybrid approach:
    1. First try MCP
    2. Fill in any missing values using extract methods

    Returns:
        JSON string with model information
    """
    # Initialize result dict with required keys
    result = {
        "params_count": None,
        "quantization": None,
        "context_length": None,
        "license": None,
        "requires_auth": None,
    }

    # First try to get model info using HuggingFace MCP tools
    if use_hf_mcp:
        mcp_result_json = get_json_hf_mcp_info(model_checkpoint)
        if mcp_result_json is not None:
            try:
                mcp_result = json.loads(mcp_result_json)
                result.update(mcp_result)
                print(f"Retrieved model info for {model_checkpoint} via MCP")
            except json.JSONDecodeError:
                print(f"Warning: Failed to parse MCP result for {model_checkpoint}")

    # Check which fields are missing (None or empty)
    missing_fields = [
        key for key, value in result.items() if value is None or value == ""
    ]

    if missing_fields:
        print(
            f"Missing fields from MCP: {missing_fields}. Using extract methods to fill gaps."
        )

        # Get info via extract methods to fill missing values
        extract_result = get_hf_model_info_via_extract_methods(model_checkpoint)

        # Fill in only the missing fields
        for field in missing_fields:
            if field in extract_result and extract_result[field] is not None:
                result[field] = extract_result[field]
                print(f"Filled {field} via extract methods")
    else:
        print(f"All required fields obtained via MCP for {model_checkpoint}")

    return json.dumps(result, indent=2)
