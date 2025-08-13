# Model Control Protocol (MCP) Server Interface

## Overview
The Model Control Protocol (MCP) server provides a simple interface for LLMs to interact with the model registry. It enables LLMs to list available models and check the hardware profile of the machine where the registry is running. The registry runs locally and connects to a PostgreSQL database.

The MCP server implements the JSON-RPC 2.0 specification using the FastMCP library, making it easy for AI clients like Claude Desktop or Cursor to communicate with the model registry.

## Architecture

### FastMCP Implementation
The MCP server is implemented using the FastMCP library, which provides:
- JSON-RPC 2.0 compliant communication
- Tool definition and registration
- Context management for logging and debugging
- Structured error handling

The server consists of two main Python files:
1. **vail/mcp/server.py** - Contains the core server implementation with tool definitions
2. **scripts/run_mcp_server.py** - Entry point script that handles environment configuration and server startup

### Component Interaction
- **scripts/run_mcp_server.py** sets up the environment, loads configuration from the appropriate `.env` file, and initializes the server
- **vail/mcp/server.py** defines the available tools, connects to the registry database, and handles requests

## Registry Resources

### 1. Model Information
A comprehensive view of each model in the registry, combining:
- **Model Details**
  - ID, name, and maker
  - Parameter count
  - Quantization format
  - Creation timestamp
- **Access Information**
  - Source type (huggingface_api, openai, anthropic, ollama, etc.)
  - Source identifier (checkpoint, repo_id, etc.)
  - Authentication requirements
  - Loader configuration (e.g., quantization settings)

### 2. Hardware Profile
- **CPU Details**
  - Count (logical and physical)
  - Model and frequency
  - Current usage

- **Memory Information**
  - Total and available memory
  - Current usage percentage

- **GPU Information** (if available)
  - Device name and count
  - Memory capacity
  - Current memory usage
  - CUDA version

- **System Information**
  - OS and version
  - Python version
  - PyTorch version
  - Disk usage

## Available Tools

The server exposes the following tools to AI assistants:

- `list_models`: List all models in the registry with optional filtering
- `get_hardware_profile`: Get the hardware profile of the local machine
- `get_model_template`: Get a template for adding a new model to the registry
- `add_model`: Add a new model to the registry *(Admin only currently, in development)*
- `get_fingerprint_vectors`: Get fingerprint vectors for models
- `generate_fingerprint`: Generate a fingerprint for a model
- `compare_fp_pairs`: Compare fingerprint pairs and generate visualizations
- `compute_fingerprint_similarity`: Compute similarity between two fingerprint vectors

### List Models
```python
@mcp.tool("list_models")
def list_models(maker: Optional[str] = None, 
                limit: int = 10, 
                offset: int = 0,
                ctx: Context = None) -> Dict:
```

Returns a list of all models available in the registry, including their complete information and access details.

**Parameters:**
- `maker` (optional): Filter by model maker
- `limit` (optional): Maximum number of models to return (default: 10)
- `offset` (optional): Number of models to skip (default: 0)

**Response:**
```json
{
  "models": [
    {
      "model_id": "123",
      "model_maker": "organization",
      "model_name": "model-name",
      "params_count": 1000000000,
      "quantization": "fp32",
      "created_at": "2024-03-20T10:00:00Z",
      "sources": [
        {
          "source_id": "456",
          "source_type": "huggingface_api",
          "source_identifier": {
            "loader_class": "AutoModelForCausalLM",
            "checkpoint": "organization/model-name"
          },
          "requires_auth": false,
          "created_at": "2024-03-20T10:00:00Z"
        }
      ]
    }
  ],
  "total": 100,
  "offset": 0,
  "limit": 10
}
```

### Get Hardware Profile
```python
@mcp.tool("get_hardware_profile")
def get_hardware_profile(ctx: Context = None) -> Dict:
```

Returns the current hardware profile of the machine.

**Response:**
```json
{
  "cpu": {
    "count": 8,
    "physical_count": 4,
    "model": "Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz",
    "frequency": {
      "current": 2600.0,
      "min": 800.0,
      "max": 4500.0
    }
  },
  "memory": {
    "total": 16777216000,
    "available": 8388608000,
    "percent": 50.0
  },
  "gpu": [
    {
      "name": "NVIDIA GeForce RTX 3080",
      "memory_total": 10737418240,
      "memory_allocated": 2147483648,
      "memory_cached": 4294967296
    }
  ],
  "disk": {
    "total": 500000000000,
    "free": 250000000000,
    "percent": 50.0
  },
  "system": {
    "os": "Darwin",
    "os_version": "23.6.0",
    "python_version": "3.9.7",
    "torch_version": "2.0.1",
    "cuda_version": "11.7"
  },
  "last_updated": "2024-03-14T12:00:00Z"
}
```

### Get Model Template
```python
@mcp.tool("get_model_template")
def get_model_template(source_type: Optional[str] = None, ctx: Context = None) -> Dict:
```

Returns a template showing the required format and fields for adding a model to the registry.

**Parameters:**
- `source_type` (optional): Get template specific to a source type (huggingface_api, onnx, or gguf)

**Response:**
```json
{
  "model_info_template": {
    "model_maker": "organization_name",
    "model_name": "unique_model_name",
    "params_count": 7000000000,
    "link": "https://huggingface.co/meta-llama/Llama-2-7b-chat",
    "license_type": "llama2",
    "quantization": "fp16"
  },
  "examples": {
    "llama2_example": {
      "model_info": {
        "model_maker": "meta",
        "model_name": "llama-2-7b-chat",
        "params_count": 7000000000,
        "link": "https://huggingface.co/meta-llama/Llama-2-7b-chat",
        "license_type": "llama2",
        "quantization": "fp16"
      }
    }
  },
  "source_info_templates": {
    "huggingface_api": {
      "source_type": "huggingface_api",
      "source_identifier": "{\"loader_class\":\"AutoModelForCausalLM\",\"checkpoint\":\"organization/model-name\"}",
      "requires_auth": true
    },
    "onnx": {
      "source_type": "onnx",
      "source_identifier": "{\"model_path\":\"/path/to/model.onnx\"}",
      "requires_auth": false
    },
    "gguf": {
      "source_type": "gguf",
      "source_identifier": "{\"model_path\":\"/path/to/model.gguf\"}",
      "requires_auth": false
    }
  }
}
```

### Add Model

*Admin only currently, in development*

```python
@mcp.tool("add_model")
def add_model(model_info: Dict,
              source_info: Optional[Dict] = None,
              ctx: Context = None) -> Dict:
```

Adds a new model to the registry with optional source information.

**Parameters:**
- `model_info`: Dictionary containing model information with the following fields:
  - `model_maker` (required): Organization or individual that created the model
  - `model_name` (required): Unique name of the model
  - `params_count` (required): Number of parameters in the model
  - `model_card_url` (required): URL to the model's documentation, card, or public webpage
  - `license_type` (required): Type of license the model is released under (e.g., "Apache 2.0", "MIT", "Llama2", "proprietary")
  - `quantization` (optional): Quantization format (e.g., fp32, fp16, int8)
- `source_info` (optional): Dictionary containing source information with the following fields:
  - `source_type` (required): Type of source (e.g., huggingface_api, openai, anthropic, ollama)
  - `source_identifier` (required): JSON-serialized string containing source-specific information. Must be a valid JSON object string.
  - `requires_auth` (optional): Whether authentication is required to access the model (default: false)

**Response:**
```json
{
  "model_id": "123",
  "source_id": "456",  // Only if source_info was provided
  "message": "Model added successfully"
}
```

**Example Usage:**
```python
model_info = {
    "model_maker": "huggingface",
    "model_name": "mistral-7b",
    "params_count": 7000000000,
    "model_card_url": "https://huggingface.co/mistralai/Mistral-7B-v0.1",
    "license_type": "Apache 2.0",
    "quantization": "fp16"
}

source_info = {
    "source_type": "huggingface_api",
    "source_identifier": json.dumps({
        "loader_class": "AutoModelForCausalLM",
        "checkpoint": "mistralai/Mistral-7B-v0.1"
    }),
    "requires_auth": false
}

response = add_model(model_info, source_info)
```

Note: The `source_identifier` must be a JSON-serialized string, not a Python dictionary. Use `json.dumps()` to convert a dictionary to a valid JSON string before passing it to the tool.

## Error Handling

FastMCP implements standard JSON-RPC 2.0 error handling with appropriate error codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses include:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Error message",
    "data": {
      "details": "Additional error details"
    }
  },
  "id": "request-id"
}
```

## Local Setup

### Prerequisites
- PostgreSQL database with pgvector extension
- Python 3.12 or higher
- Required Python packages (install via `uv sync`)

### Database Configuration
For local database configuration, review [local_database.md](local_database.md)

This configuration file specifies:
- The server name and namespace
- The JSON-RPC endpoint URL
- The available tools and their parameters in JSONSchema format

### Installation as a Python Package

The model registry can be installed as a Python package using pip:

```bash
pip install vail-model-registry
```

After installation, you can run the MCP server using the provided CLI:

```bash
# Start the MCP server
vail mcp run

# Run with global registry 
vail mcp run --registry-type global

# Run on specific host and port
vail mcp run --host 0.0.0.0 --port 9000
```

## Client Integration

To integrate the MCP server with clients like Claude Desktop or Cursor, you need to provide configuration that tells the client how to start and connect to the server. This is done using a JSON configuration file called `registry_mcp.json`:

### Client Integration Steps

1. **Using the Python Package (Recommended)**:

After installing the package with `pip install vail-model-registry`, configure clients to use the `vail` command:

```json
{
  "mcpServers": {
    "VAIL Model Registry": {
      "command": "vail",
      "args": [
        "mcp", "run",
        "--registry-type", "local",
        "--local-db-path", "/path/to/local_registry.duckdb"
      ],
      "env": {
        "DATABASE_URL": "postgresql://user:password@localhost:5432/vail_registry",
        "HUGGINGFACE_TOKEN": "your_hf_token_here"
      }
    }
  }
}
```

2. **For Cursor (Manual Setup)**:
```json
{
  "mcpServers": {
    "VAIL Model Registry": {
      "command": "/path/to/vail-model-registry/.venv/bin/python",
      "args": [
        "/path/to/your/vail-model-registry/scripts/run_mcp_server.py"
      ]
    }
  }
}
```

3. **For Claude Desktop (Manual Setup)**:
- Create a shell script that can direct Claude to the python environment where the MCP server code
  is setup properly. 

```#!/bin/bash
# Save as start_mcp_server.sh

# Change to the correct directory
cd /path/to/vail-model-registry/

# Run the server
exec /path/to/vail-model-registry/.venv/bin/python scripts/run_mcp_server.py

```

```json
{
  "mcpServers": {
    "VAIL Model Registry": {
      "command": "/path/to/start_registry_mcp_server.sh",
      "args": []
    }
  }
}
```

4. **For MCP Inspector (Debugging)**

`mcp dev vail/mcp/server.py`

# Example usage

1. In Claude Desktop, you can ask Claude to recommend a model from the registry that will run best on your hardware.
2. In Cursor, you can ask the LLM to choose a model from the registry, that will work best on your machine, and generate
   the code to run that model for you.


## Troubleshooting

### Common Issues
1. **Database Connection**
   - Verify PostgreSQL is running
   - Check connection string in `.env.local`
   - Ensure pgvector extension is installed

2. **Model Loading**
   - Verify model files exist
   - Check file permissions
   - Validate model configuration

### Logging
- Application logs: `logs/model_registry.log`
- Debug logs: `logs/debug.log`
