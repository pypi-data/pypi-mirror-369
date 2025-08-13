# VAIL Model Registry

## Overview
The VAIL Model Registry streamlines how developers discover, manage, and integrate machine learning models into applications by:
- Simplifying model discovery and selection through natural language and database queries
- Enabling flexible usage between multiple models
- Future-proofing applications as registry models are updated
- Standardizing model information access across diverse models

Learn More: https://projectvail.org

## Table of Contents

1. Architecture

2. Model Fingerprinting

3. Getting Started

4. Core Features
   1. Registry Synchronization
   2. Model Comparison
   3. Local Model Management

5. Interfaces
   1. Model Context Protocol
   2. Command line tools
   3. Python integration

6. Registry Applications

7. Miscellaneous
   1. Roadmap
   2. Further Documentation 

## Registry Architecture

With models being published to multiple places like Hugging Face, internal model hubs, and other forums, VAIL's model registry
helps developers maintain a single hub of all the models they are currently developing with.

The registry architecture is designed to be split between local and global storage for model metadata. Models can be sync'd between local and
global registries. VAIL uses a model fingerprint to determine uniqueness (more below). Local registries are meant to be used in the context of specific applications, with local observations, and with sensitivity to local hardware resources. Global models are a source of truth 
for models, used across environments and vetted by other registry users.

### Key properties

**Local Registry**
- Application-specific model cache storing relevant subsets from Global Registry
- Maintains context-aware configuration (hardware profiles, local customizations)
- Optimizes performance through local caching of model information

**Global Registry**
- Centralized discovery hub for publishing and versioning models
- Uses fingerprints as stable identifiers for consistent model tracking
- Provides broad access to identify models for various tasks

## Model Fingerprinting

### Overview

Models, when published for developers, come in a wide variety: serialization formats (safetensor, GGUF, MLX, ONNX), quantization formats (bfloat16, 8Bit, QWQ, etc),
and more. It can be difficult to confirm which model is being run at inference time and if that model has changed since the original implementation. VAIL's model
fingerprinting is designed to provide uniqueness as well as comparability between models. With model fingerprinting, it's possible to determine if
the model has changed since original publication and determine how significantly the model was changed.

Currently, model fingerprints are used to synchronize model metadata between local and global registries. Fingerprints can also be used for runtime validation 
of models when deployed, among other use cases. This ensures accurate synchronization between local and global registries and simplifies variant management (e.g., different formats/quantizations of the same model).


### Comparison Threshold
The registry syncing process uses a fingerprint similarity threshold of .998. This means that two models are considered the same if their fingerprints have a similarity of at least .998. A model in the global registry will only be synced to the local registry when it is considered distinct from all models already in the local registry. 

We consider two models to be the same when the same model files are used on different machines, or when the same model weights are serialized in different formats. Models with different quantizations or different levels of precision are considered distinct. The chosen similarity threshold aims to enforce this criteria -- e.g. when generating a fingerprint from the same model files on two different machines, the two fingerprints should have a similarity of at least .998 -- although it is not a rigorous guarantee.

- Same even when fingerprints are generated on different machines
- Same when they have distinct formats
- Different when they are used at different quantizations


## Getting Started

```bash
> pip install vail-model-registry

> vail init
```

## Core Features

### 1. Registry Synchronization
- Import models from Global to Local Registry
- Apply selective syncing based on application needs

```bash
# Syncs all models in Global Registry to Local
vail registry sync

# Sync all models in Global Registry with less than this number of parameters to Local
vail registry sync --max-params 4_000_000_000 
```

### 2. Comparing Two Models
- Determine similarity between models using fingerprinting methodology
- Quantify relationships between models in latent metric space
- Identify functional similarities or unique capabilities

```bash
# Compares models to determine their similarity to each other
vail model compare <local model ID 1> <local model ID 2>
```

*To compare more than 2 models to each other*
```bash
# Generate a matrix showing the similarities across a set of models
vail model similarities --model-ids 10,11,12,13
```



### 3. Local Model Management
- View model details
- Add custom models to Local Registry (*in development*)
- Store contextual observations and evaluations (*in development*)
- Selectively share insights with other users (*in development*)

```bash
# View info for a specific model
vail model view <local model ID>
```

*To find similar models to a known model in the local registry*
```bash
vail model find-similar <local model ID>
```

## Interfaces

There are multiple ways to interact with the registry. 

### 1. Command-Line Interface
- Explore registries from terminal
- Manage model synchronization
- Perform basic administrative tasks

```bash
# Opens an interactive command line browser to view Local and Global Models available
vail registry browse
```

### 2. MCP Client Integration
- Use AI assistants (Claude Desktop, Cursor) to interact with registry via natural language
- Enable AI-assisted model discovery and information retrieval
- Streamline development workflow

```bash
# Starts an MCP server connected to the local registry to use via MCP Clients like Claude Desktop or Cursor
vail mcp run
```

The MCP client can be pointed at either the local or global registry. Running the MCP server with the local registry allows sharing with MCP client information about the local hardware and models
that have been pulled from the global registry. It does not allow adding models to the global registry.

Running the MCP server with the global registry does not provide the MCP Client with local hardware information.

Further information about connecting clients to VAIL's MCP server can be found [here](vail/docs/mcp_server.md).

*Defaults to using the local registry (i.e. `vail mcp run --registry-type local`)*


### 3. Python Library
- Programmatically query registries
- Implement automated model loading
- Build custom analysis tools and MLOps pipelines

```python
import vail
from vail.registry import LocalRegistryInterface
model_registry = LocalRegistryInterface(
    connection_string=database_url,
    local_db_path="./my_local_registry.duckdb",  # Optional: defaults to "local_registry.duckdb"
)
models = model_registry.find_models()
```
## Registry Applications

### 1. Know Your Model

With so many models out there, it can be difficult (if not impossible) to know which model you are currently using within your application. Using the registry along with model fingerprints, you can validate which model is currently being accessed, before or after you use the model.

You can compare the model's fingerprint from the registry with a newly generated fingerprint to determine if they are similar (if not the same). You can set your own thresholds for "sameness" depending on your application. 
For example, you may wish to only work with fine-tunes of a particular model that haven't altered it significantly.

### 2. Choose The Right Model

With so many models to choose from, it can be difficult to choose which model will perform best for your application. There are several factors to consider such as application requirements, hardware availability, governance/licenses, etc.
Using the registry can help this situation by allowing the developer to specify which models to use. Developers can specify criteria for which models to sync from the global registry to the local registry.
### 3. Packaging Models with Your App

If you're building an app and allowing other users to choose the model they prefer, you can package your application
with a local registry that has supported models already included. This can simplify the task of surfacing information that a user would look to when choosing
which model to run with. You can evaluate your application with specific models a priori in order to provide
info to users about application-specific model trade-offs.

## Miscellaneous

### Roadmap

We would love to support you and your efforts to build applications that utilize hundreds of different models. We are actively working on the following
but we would love to hear from you. Please reach out to tell us what would help you! developers@projectvail.org

#### 1. Verifiable Computation

VAIL is actively working with the research community to support verifiable computation for AI models, with the registry housing verifiability artifacts. Approaches include integrating with
cutting edge cryptographic techniques like zero knowledge proofs as well as supporting secure hardware devices like secure enclaves.

#### 2. Supporting Diverse Model Architecture

VAIL's model registry currently supports open source text-generation and code generation models with 70B parameters or less. We are 
working to expand support for other modalities and multi-modal models soon. We also plan to support other non-transformer based model
architectures such as diffusion and state-spaced models.

#### 3. Supporting Other Languages

We plan to support other languages where developers are building applications that incorporate AI models such as Go and Rust.


