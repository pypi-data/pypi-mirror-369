"""
Model Interface for the Unified Fingerprinting Framework

This module provides a standard interface for working with models in the fingerprinting framework.
"""

import dataclasses
import glob
import hashlib
import importlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import torch
from gguf import GGUFReader
from huggingface_hub import login, snapshot_download
from transformers import AutoTokenizer

from vail.utils import load_onnx_model, setup_logging
from vail.utils.env import load_env

# Track if we've already authenticated to avoid duplicate logins
_HF_ALREADY_AUTHENTICATED = False
logger = setup_logging(log_file_name="models.log")
load_env()


class GGUFTokenizer:
    """
    A HuggingFace-compatible tokenizer wrapper for GGUF models.

    This class wraps the built-in tokenizer of GGUF models and provides
    an interface compatible with HuggingFace tokenizers.
    """

    def __init__(self, gguf_model):
        """
        Initialize the GGUF tokenizer wrapper.

        Args:
            gguf_model: The loaded GGUF model (llama_cpp.Llama instance)
        """
        self.model = gguf_model

        # Extract special tokens from GGUF metadata
        self._extract_special_tokens()

    def _extract_special_tokens(self):
        """
        Extract special token information from the GGUF model metadata.

        This method reads the actual special token IDs and strings from the GGUF file
        metadata, making the tokenizer generic and compatible with any GGUF model.
        """
        try:
            # Get the model path to read metadata
            model_path = self.model.model_path

            reader = GGUFReader(model_path)

            # Helper function to safely extract integer values from GGUF fields
            def get_token_id(field_name, default_value):
                try:
                    field = reader.get_field(field_name)
                    if field is not None:
                        # Handle different possible data structures
                        if hasattr(field, "data") and len(field.data) > 0:
                            return int(field.data[0])
                        elif hasattr(field, "parts") and len(field.parts) > 0:
                            return int(field.parts[0])
                        else:
                            return int(field)
                    return default_value
                except Exception:
                    return default_value

            # Extract special token IDs from metadata with fallbacks
            self.bos_token_id = get_token_id("tokenizer.ggml.bos_token_id", 1)
            self.eos_token_id = get_token_id("tokenizer.ggml.eos_token_id", 2)
            self.unk_token_id = get_token_id("tokenizer.ggml.unk_token_id", 0)
            self.pad_token_id = get_token_id(
                "tokenizer.ggml.pad_token_id", self.eos_token_id
            )

            # Helper function to safely decode token strings
            def get_token_string(token_id, fallback):
                try:
                    decoded = (
                        self.model.detokenize([token_id])
                        .decode("utf-8", errors="ignore")
                        .strip()
                    )
                    return decoded if decoded else fallback
                except Exception:
                    return fallback

            # Extract special token strings by decoding the token IDs
            self.bos_token = get_token_string(self.bos_token_id, "<s>")
            self.eos_token = get_token_string(self.eos_token_id, "</s>")
            self.unk_token = get_token_string(self.unk_token_id, "<unk>")
            self.pad_token = self.eos_token  # Use EOS token as pad token

            logger.info(
                f"Extracted special tokens from GGUF metadata: "
                f"BOS={self.bos_token_id}('{self.bos_token}'), "
                f"EOS={self.eos_token_id}('{self.eos_token}'), "
                f"UNK={self.unk_token_id}('{self.unk_token}'), "
                f"PAD={self.pad_token_id}('{self.pad_token}')"
            )

        except Exception as e:
            logger.warning(
                f"Failed to extract special tokens from GGUF metadata: {e}. Using fallback values."
            )
            # Fallback to LLaMA-style defaults if metadata extraction fails
            self.bos_token_id = 1
            self.eos_token_id = 2
            self.unk_token_id = 0
            self.pad_token_id = self.eos_token_id

            self.bos_token = "<s>"
            self.eos_token = "</s>"
            self.unk_token = "<unk>"
            self.pad_token = self.eos_token

    def encode(self, text: str, add_special_tokens: bool = True, **kwargs) -> List[int]:
        """
        Encode text to token IDs.

        Args:
            text: Text to encode
            add_special_tokens: Whether to add special tokens (BOS/EOS)
            **kwargs: Additional arguments (for compatibility)

        Returns:
            List of token IDs
        """
        if isinstance(text, list):
            # Batch encoding - encode each text separately
            return [self.encode(t, add_special_tokens=add_special_tokens) for t in text]

        # Convert text to bytes and tokenize
        token_ids = self.model.tokenize(
            text.encode("utf-8"), add_bos=add_special_tokens
        )
        return token_ids

    def decode(
        self, token_ids: List[int], skip_special_tokens: bool = False, **kwargs
    ) -> str:
        """
        Decode token IDs to text.

        Args:
            token_ids: List of token IDs to decode
            skip_special_tokens: Whether to skip special tokens in output
            **kwargs: Additional arguments (for compatibility)

        Returns:
            Decoded text
        """
        if not token_ids:
            return ""

        # Filter special tokens if requested
        if skip_special_tokens:
            token_ids = [
                tid
                for tid in token_ids
                if tid not in [self.bos_token_id, self.eos_token_id, self.pad_token_id]
            ]

        # Use the model's detokenize method
        try:
            # Convert list to bytes using the model's detokenize
            text_bytes = self.model.detokenize(token_ids)
            # Decode bytes to string
            return text_bytes.decode("utf-8", errors="ignore")
        except Exception:
            # Fallback: join individual token decodings
            tokens = []
            for tid in token_ids:
                try:
                    token_bytes = self.model.detokenize([tid])
                    tokens.append(token_bytes.decode("utf-8", errors="ignore"))
                except Exception:
                    pass  # Skip unknown tokens
            return "".join(tokens)

    def batch_encode_plus(
        self,
        batch_text_or_text_pairs,
        add_special_tokens: bool = True,
        padding: bool = False,
        truncation: bool = False,
        max_length: Optional[int] = None,
        return_tensors: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """
        Batch encode texts with additional features.

        Args:
            batch_text_or_text_pairs: List of texts to encode
            add_special_tokens: Whether to add special tokens
            padding: Whether to pad sequences
            truncation: Whether to truncate sequences
            max_length: Maximum sequence length
            return_tensors: Format for return tensors ('pt' for PyTorch)
            **kwargs: Additional arguments

        Returns:
            Dictionary with input_ids and attention_mask
        """
        if isinstance(batch_text_or_text_pairs, str):
            batch_text_or_text_pairs = [batch_text_or_text_pairs]

        # Encode all texts
        encoded = []
        for text in batch_text_or_text_pairs:
            token_ids = self.encode(text, add_special_tokens=add_special_tokens)

            # Truncate if needed
            if truncation and max_length and len(token_ids) > max_length:
                token_ids = token_ids[:max_length]

            encoded.append(token_ids)

        # Find max length for padding
        if padding:
            max_len = max(len(ids) for ids in encoded) if encoded else 0
            if max_length:
                max_len = min(max_len, max_length)

            # Pad sequences
            attention_mask = []
            for ids in encoded:
                mask = [1] * len(ids)
                padding_length = max_len - len(ids)
                if padding_length > 0:
                    ids.extend([self.pad_token_id] * padding_length)
                    mask.extend([0] * padding_length)
                attention_mask.append(mask)
        else:
            attention_mask = [[1] * len(ids) for ids in encoded]

        # Convert to tensors if requested
        if return_tensors == "pt":
            input_ids = torch.tensor(encoded)
            attention_mask = torch.tensor(attention_mask)
        else:
            input_ids = encoded

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }

    def encode_plus(
        self,
        text,
        add_special_tokens: bool = True,
        padding: bool = False,
        truncation: bool = False,
        max_length: Optional[int] = None,
        return_tensors: Optional[str] = None,
        **kwargs,
    ) -> Dict:
        """
        Encode a single text with additional features.

        This is a wrapper around batch_encode_plus for single texts.
        """
        result = self.batch_encode_plus(
            [text],
            add_special_tokens=add_special_tokens,
            padding=padding,
            truncation=truncation,
            max_length=max_length,
            return_tensors=return_tensors,
            **kwargs,
        )

        # Remove batch dimension for single text
        if return_tensors == "pt":
            result["input_ids"] = result["input_ids"].squeeze(0)
            result["attention_mask"] = result["attention_mask"].squeeze(0)
        else:
            result["input_ids"] = result["input_ids"][0]
            result["attention_mask"] = result["attention_mask"][0]

        return result

    def __call__(
        self,
        text,
        add_special_tokens: bool = True,
        padding: bool = False,
        truncation: bool = False,
        max_length: Optional[int] = None,
        return_tensors: Optional[str] = None,
        **kwargs,
    ):
        """
        Main tokenization method - compatible with HuggingFace tokenizers.
        """
        if isinstance(text, str):
            return self.encode_plus(
                text,
                add_special_tokens=add_special_tokens,
                padding=padding,
                truncation=truncation,
                max_length=max_length,
                return_tensors=return_tensors,
                **kwargs,
            )
        else:
            return self.batch_encode_plus(
                text,
                add_special_tokens=add_special_tokens,
                padding=padding,
                truncation=truncation,
                max_length=max_length,
                return_tensors=return_tensors,
                **kwargs,
            )

    def convert_tokens_to_ids(self, tokens):
        """Convert tokens to IDs - for compatibility."""
        if isinstance(tokens, str):
            return self.encode(tokens, add_special_tokens=False)[0]
        return [self.encode(token, add_special_tokens=False)[0] for token in tokens]

    def convert_ids_to_tokens(self, ids):
        """Convert IDs to tokens - for compatibility."""
        if isinstance(ids, int):
            return self.decode([ids])
        return [self.decode([id]) for id in ids]

    @property
    def vocab_size(self):
        """Get vocabulary size from the model."""
        if hasattr(self.model, "n_vocab"):
            return self.model.n_vocab()
        return None


class Model:
    """
    Standard interface for models in the fingerprinting framework.

    This class wraps model loaders and provides a consistent interface for operations
    needed by the fingerprinting methods.
    """

    def __init__(self, name: str, model_info: Dict, **model_loader_kwargs):
        """
        Initialize a model wrapper.

        Args:
            name: Model name or identifier
            model_info: Comprehensive information about the model from the registry
            model_loader_kwargs: Additional keyword arguments to pass to the model loader

        Notes:
            The model_info dictionary can include quantization information in the model_info['quantization']
            field. For models where the quantization specified in the registry should be enforced during loading,
            you can include a 'loader_kwargs' key in the source_identifier JSON. For example:

            {
                "loader_class": "AutoModelForCausalLM",
                "checkpoint": "mistralai/Mistral-7B-v0.1",
                "loader_kwargs": {
                    "load_in_8bit": true
                }
            }

            These loader_kwargs will be passed to the model's from_pretrained method to ensure
            it's loaded with the desired quantization settings.
        """
        self.name = name
        self.model_info = model_info
        self.model_source_type = self._get_primary_source_type()
        self.model_loader_kwargs = model_loader_kwargs

        # Check if authentication is required for the primary source
        self.requires_auth = False
        sources = self.model_info.get("sources", [])
        if sources:
            self.requires_auth = sources[0].get("requires_auth", False)

        # Set loaders using internal methods
        self.model_loader = self._get_model_loader_func()
        self.tokenizer_loader = self._get_tokenizer_loader_func()

        # Will be populated when loaded
        self.loaded_model = None
        self.loaded_tokenizer = None
        self.embedding_dimension = None
        self.vocab_size = None
        self._gguf_embeddings = None  # Cache for GGUF embeddings

    def _authenticate_huggingface(self):
        """Authenticate with Hugging Face if not already authenticated."""
        global _HF_ALREADY_AUTHENTICATED

        # Check if we've already authenticated in this session
        if _HF_ALREADY_AUTHENTICATED:
            logger.info(
                f"Using existing Hugging Face authentication for model {self.name}"
            )
            return

        # Standard authentication logic
        token_path = os.path.expanduser("~/.huggingface")
        if os.path.exists(token_path):
            with open(token_path, "r") as f:
                token = f.read().strip()
            login(token=token)
            logger.info(
                f"Logged in to Hugging Face for model {self.name} using token from ~/.huggingface/token"
            )
        else:
            raw_token = os.getenv("HUGGINGFACE_TOKEN")
            if raw_token:
                login(token=raw_token)
                logger.info(f"Logged in to Hugging Face for model {self.name}")
            else:
                logger.warning(
                    "No Hugging Face token found. Please set the HUGGINGFACE_TOKEN environment variable."
                )

        _HF_ALREADY_AUTHENTICATED = True

    def _get_primary_source_type(self) -> str:
        """Get the primary source type from model info."""
        sources = self.model_info.get("sources", [])
        if sources:
            return sources[0].get("source_type", "unknown")
        return "unknown"

    def _get_primary_source_identifier(self) -> Dict:
        """Get the primary source identifier from model info."""
        sources = self.model_info.get("sources", [])
        if sources:
            return sources[0].get("source_identifier", {})
        return {}

    def _get_model_loader_func(self) -> Callable:
        """Get a function to load the model based on model info."""
        source_identifier = self._get_primary_source_identifier()
        if not source_identifier:
            raise ValueError(f"No source identifier found for model {self.name}")

        source_type = self.model_source_type

        if source_type == "huggingface_api":
            # Parse the JSON source identifier for huggingface_api
            # Example: {loader_class: T5ForConditionalGeneration, checkpoint: 'google/t5-v1_1-small'}
            if isinstance(source_identifier, str):
                # If it's a string, try to parse it as JSON
                try:
                    source_identifier = json.loads(source_identifier)
                except json.JSONDecodeError:
                    raise ValueError(
                        f"Invalid source_identifier format for huggingface_api: {source_identifier}"
                    )

            loader_class_name = source_identifier.get("loader_class")
            checkpoint = source_identifier.get("checkpoint")

            if not loader_class_name or not checkpoint:
                raise ValueError(
                    f"Missing loader_class or checkpoint in source_identifier: {source_identifier}"
                )

            # Import the specified loader class from transformer
            # Dynamically import the class from transformers
            transformers_module = importlib.import_module("transformers")
            if hasattr(transformers_module, loader_class_name):
                loader_class = getattr(transformers_module, loader_class_name)

            # Extract loader_kwargs if present in source_identifier
            loader_kwargs = source_identifier.get("loader_kwargs", {})

            # Return a function that loads the model
            def load_model(**kwargs):
                import os

                # Authenticate if required for this model before loading
                if self.requires_auth:
                    self._authenticate_huggingface()

                os.environ["TRANSFORMERS_ATTENTION_BACKEND"] = "torch"

                # Define and create offload directory
                offload_folder = os.path.abspath("./.hf_offload_cache")
                os.makedirs(offload_folder, exist_ok=True)
                logger.info(f"Using offload directory: {offload_folder}")

                # GPU-optimized parameters for model loading
                load_kwargs = {
                    "trust_remote_code": True,
                    "low_cpu_mem_usage": True,  # Minimize CPU memory during loading
                    "device_map": "auto",  # Let accelerate handle device mapping
                    "offload_folder": offload_folder,  # Specify offload directory
                    "attn_implementation": "eager",  # Use eager attention for broader compatibility
                }

                # Combine all kwargs
                load_kwargs.update(loader_kwargs)
                load_kwargs.update(kwargs)

                # Load model directly into memory
                return loader_class.from_pretrained(checkpoint, **load_kwargs)

            return load_model

        elif source_type == "onnx_file":
            # Return a function that prioritizes file_path from kwargs, then falls back to path in source_identifier
            return lambda **kwargs: load_onnx_model(kwargs.get("file_path"))

        elif source_type == "gguf_file":
            # Parse the source identifier for GGUF files
            if isinstance(source_identifier, str):
                try:
                    source_identifier = json.loads(source_identifier)
                except json.JSONDecodeError:
                    raise ValueError(
                        f"Invalid source_identifier format for gguf_file: {source_identifier}"
                    )

            # GGUF files can be loaded from HuggingFace repos or local files
            repo_id = source_identifier.get("checkpoint")
            filename = source_identifier.get("filename")
            file_path = source_identifier.get("file_path")
            # Get quantization from model_info (models table) for consistency
            quantization = self.model_info.get("quantization")

            # Additional loader kwargs for llama_cpp
            loader_kwargs = source_identifier.get("loader_kwargs", {})

            def load_model(**kwargs):
                import glob

                from huggingface_hub import snapshot_download
                from llama_cpp import Llama

                # Authenticate if required for this model before downloading
                if self.requires_auth and repo_id:
                    self._authenticate_huggingface()

                # Determine the actual file path
                actual_file_path = None

                if file_path:
                    # Direct file path provided
                    actual_file_path = os.path.expanduser(file_path)
                elif repo_id and filename:
                    # Download specific file from HuggingFace repo
                    logger.info(f"Downloading GGUF model {filename} from {repo_id}...")
                    local_dir = f"./.hf_cache/{repo_id.replace('/', '_')}"
                    gguf_dir = snapshot_download(
                        repo_id=repo_id, allow_patterns=[filename], local_dir=local_dir
                    )
                    # Find the downloaded file
                    file_pattern = os.path.join(gguf_dir, "**", filename)
                    matching_files = glob.glob(file_pattern, recursive=True)
                    if not matching_files:
                        raise FileNotFoundError(
                            f"GGUF file {filename} not found after download"
                        )
                    actual_file_path = matching_files[0]
                    logger.info(f"GGUF file downloaded to: {actual_file_path}")
                elif repo_id and quantization:
                    # Use auxiliary function to find GGUF file by quantization
                    actual_file_path = _find_gguf_file_by_quantization(
                        repo_id=repo_id, quantization=quantization
                    )
                else:
                    # Fallback to kwargs file_path
                    actual_file_path = kwargs.get("file_path")
                    if not actual_file_path:
                        raise ValueError(
                            "No file_path provided for GGUF model loading. Need either file_path, (checkpoint + filename), or (checkpoint + quantization)"
                        )

                if not actual_file_path or not os.path.exists(actual_file_path):
                    raise FileNotFoundError(f"GGUF file not found: {actual_file_path}")

                # Default parameters for GGUF model loading
                llama_kwargs = {
                    "model_path": actual_file_path,
                    "n_ctx": 2048,  # Default context length
                    "embedding": False,  # Don't use embedding mode - we'll extract raw embeddings separately
                    "verbose": False,  # Reduce verbosity
                    "logits_all": True,  # Enable storing all logits for proper inference
                }

                # Override with any loader_kwargs from source_identifier
                llama_kwargs.update(loader_kwargs)
                # Override with any runtime kwargs
                llama_kwargs.update(kwargs)

                logger.info(
                    f"Loading GGUF model from {actual_file_path} with parameters: {llama_kwargs}"
                )
                return Llama(**llama_kwargs)

            return load_model

        else:
            raise ValueError(f"Unsupported model source type: {source_type}")

    def _get_tokenizer_loader_func(self) -> Optional[Callable]:
        """Get a function to load the tokenizer based on model info."""
        source_identifier = self._get_primary_source_identifier()
        if not source_identifier:
            raise ValueError(f"No source identifier found for model {self.name}")

        source_type = self.model_source_type

        if source_type in ["huggingface_api"]:
            if isinstance(source_identifier, str):
                # If it's a string, try to parse it as JSON
                try:
                    source_identifier = json.loads(source_identifier)
                    checkpoint = source_identifier.get("checkpoint", "")
                except json.JSONDecodeError:
                    raise ValueError(
                        f"Invalid source_identifier format for huggingface_api: {source_identifier}"
                    )
            else:
                checkpoint = source_identifier.get("checkpoint", "")

            # Return a function that loads the tokenizer
            def load_tokenizer():
                import os

                os.environ["TRANSFORMERS_ATTENTION_BACKEND"] = "torch"

                # Just use modern parameters for recent transformers
                return AutoTokenizer.from_pretrained(
                    checkpoint,
                    trust_remote_code=True,
                    use_fast=True,
                )

            return load_tokenizer
        elif source_type == "gguf_file":
            # Return a function that creates a GGUFTokenizer
            def load_tokenizer():
                if self.loaded_model is None:
                    self.load()
                return GGUFTokenizer(self.loaded_model)

            return load_tokenizer
        else:
            return None

    def load(self):
        """Load the model if not already loaded."""
        import time

        if self.loaded_model is None:
            start_time = time.time()
            logger.info(f"Loading model {self.name} (using cache if available)...")
            # The model_loader function already merges source_identifier's loader_kwargs with any additional kwargs
            self.loaded_model = self.model_loader(**self.model_loader_kwargs)
            if self.model_source_type != "gguf_file":  # @todo: ian - invert this logic
                self.loaded_model.eval()  # Ensure model is in evaluation mode
            load_time = time.time() - start_time
            # Print informative message about loading time
            logger.info(f"Model {self.name} loaded in {load_time:.2f} seconds")
        return self.loaded_model

    def load_tokenizer(self):
        """Load the tokenizer if available and not already loaded."""
        if self.loaded_tokenizer is None and self.tokenizer_loader is not None:
            logger.info(
                f"Loading tokenizer for {self.name} (using cache if available)..."
            )
            self.loaded_tokenizer = self.tokenizer_loader()
            logger.info(f"Tokenizer for {self.name} loaded")
        return self.loaded_tokenizer

    def get_input_embeddings(self):
        """Get the input embedding layer of the model."""
        if self.loaded_model is None:
            self.load()

        if self.model_source_type == "gguf_file":
            # For GGUF models, we need to extract raw embeddings from the file
            if self._gguf_embeddings is None:
                import numpy as np
                from gguf import GGMLQuantizationType, GGUFReader

                # Get the file path from the loaded model
                model_path = self.loaded_model.model_path

                logger.info(
                    f"Extracting raw token embeddings from GGUF file: {model_path}"
                )

                # Parse GGUF file for raw embeddings
                reader = GGUFReader(model_path)

                # Find token embedding tensor
                token_embd_tensor = None
                for tensor in reader.tensors:
                    if tensor.name == "token_embd.weight":
                        token_embd_tensor = tensor
                        break

                if not token_embd_tensor:
                    raise AttributeError(
                        f"Could not find token_embd.weight in GGUF file for model {self.name}"
                    )

                # Extract and convert embeddings
                gguf_embed_data = token_embd_tensor.data
                if token_embd_tensor.tensor_type == GGMLQuantizationType.F16:
                    gguf_embed_matrix = gguf_embed_data.astype(np.float32)
                else:
                    gguf_embed_matrix = gguf_embed_data

                # Get the shape - GGUF tensors store shape information
                shape = token_embd_tensor.shape
                data_size = gguf_embed_data.size

                # GGUF stores embeddings as [embedding_dim, vocab_size]
                if len(shape) == 2:
                    embedding_dim = shape[0]
                    vocab_size = shape[1]
                else:
                    # Should not happen for embeddings
                    raise ValueError(f"Unexpected tensor shape: {shape}")

                    # Check if data is already shaped (2D array)
                if gguf_embed_data.ndim == 2:
                    # Data is already shaped in the correct order [vocab_size, embedding_dim]
                    # GGUF reader handles the transposition for us
                    gguf_embed_matrix = gguf_embed_data

                else:
                    # Data is flat, need to reshape then transpose
                    # For quantized models, infer dimensions if needed
                    if embedding_dim * vocab_size != data_size:
                        vocab_size = self.loaded_model.n_vocab()
                        embedding_dim = data_size // vocab_size
                        logger.info(
                            f"Inferred dimensions: vocab={vocab_size}, embed_dim={embedding_dim}"
                        )

                    # Reshape and transpose
                    gguf_embed_matrix = gguf_embed_data.reshape(
                        embedding_dim, vocab_size
                    ).T

                # Create a simple wrapper to make it behave like a PyTorch embedding layer
                class GGUFEmbeddingWrapper:
                    def __init__(self, embeddings):
                        # Make a copy to ensure the array is writable
                        self.weight = torch.from_numpy(embeddings.copy())
                        self.num_embeddings = self.weight.shape[0]
                        self.embedding_dim = self.weight.shape[1]

                    def __call__(self, input_ids):
                        return self.weight[input_ids]

                self._gguf_embeddings = GGUFEmbeddingWrapper(gguf_embed_matrix)
                logger.info(
                    f"GGUF embeddings loaded: {self._gguf_embeddings.num_embeddings} tokens, {self._gguf_embeddings.embedding_dim} dimensions"
                )

            return self._gguf_embeddings

        elif hasattr(self.loaded_model, "get_input_embeddings"):
            return self.loaded_model.get_input_embeddings()
        elif hasattr(self.loaded_model, "embeddings"):
            return self.loaded_model.embeddings
        elif hasattr(self.loaded_model, "model") and hasattr(
            self.loaded_model.model, "get_input_embeddings"
        ):
            return self.loaded_model.model.get_input_embeddings()
        else:
            raise AttributeError(
                f"Could not find input embeddings for model {self.name}"
            )

    def get_embedding_dimension(self):
        """Get the dimension of the model's embeddings."""
        if self.embedding_dimension is None:
            if self.model_source_type == "gguf_file":
                # For GGUF models, get the dimension from the embeddings
                # The model's n_embd() might not match the stored embeddings
                embedding_layer = self.get_input_embeddings()
                if hasattr(embedding_layer, "embedding_dim"):
                    self.embedding_dimension = embedding_layer.embedding_dim
                else:
                    # Fallback to model's reported dimension
                    model = self.load()
                    self.embedding_dimension = model.n_embd()
            else:
                embedding_layer = self.get_input_embeddings()
                if hasattr(embedding_layer, "weight"):
                    self.embedding_dimension = embedding_layer.weight.shape[1]
                elif hasattr(embedding_layer, "embedding_dim"):
                    self.embedding_dimension = embedding_layer.embedding_dim
                else:
                    raise AttributeError(
                        f"Could not determine embedding dimension for model {self.name}"
                    )

        return self.embedding_dimension

    def get_vocab_size(self):
        """Get the vocabulary size of the model."""
        if self.vocab_size is None:
            loaded_model = self.load()
            if hasattr(loaded_model, "config") and hasattr(
                loaded_model.config, "vocab_size"
            ):
                self.vocab_size = loaded_model.config.vocab_size
            elif self.model_source_type == "gguf_file":
                # For GGUF models, get vocab size from the model
                if hasattr(loaded_model, "n_vocab"):
                    self.vocab_size = loaded_model.n_vocab()
                else:
                    # Fallback: try to get from model metadata
                    try:
                        # Access the underlying model if available
                        if hasattr(loaded_model, "_model"):
                            self.vocab_size = loaded_model._model.n_vocab()
                        else:
                            raise AttributeError(
                                "Cannot determine vocab size for GGUF model"
                            )
                    except Exception:
                        logger.warning(
                            f"Could not determine vocabulary size for GGUF model {self.name}"
                        )
                        self.vocab_size = None
            else:
                embedding_layer = self.get_input_embeddings()
                if hasattr(embedding_layer, "weight"):
                    self.vocab_size = embedding_layer.weight.shape[0]
                elif hasattr(embedding_layer, "num_embeddings"):
                    self.vocab_size = embedding_layer.num_embeddings
                elif hasattr(embedding_layer, "vocab_size"):
                    self.vocab_size = embedding_layer.vocab_size
                else:
                    raise AttributeError(
                        f"Could not determine vocabulary size for model {self.name}"
                    )

        return self.vocab_size

    def get_device(self):
        """Get the device the model is on."""
        if self.loaded_model is None:
            self.load()

        if hasattr(self.loaded_model, "device"):
            return self.loaded_model.device
        elif hasattr(self.loaded_model, "get_device"):
            return self.loaded_model.get_device()
        elif hasattr(self.loaded_model, "parameters"):
            # Get device from first parameter
            try:
                return next(self.loaded_model.parameters()).device
            except StopIteration:
                return torch.device("cpu")
        else:
            return torch.device("cpu")

    def run_inference(self, input_ids):
        """
        Run inference with the model on the given input IDs.

        This method provides a unified interface for running inference across different
        model types (HuggingFace, GGUF, ONNX), but the underlying batch handling
        differs between model types:

        - **HuggingFace models**: Native batch processing - can handle both single
          sequences and batches efficiently using the model's built-in capabilities
        - **GGUF models**: Custom batch processing - processes each sequence in a
          batch individually due to llama.cpp API limitations
        - **ONNX models**: Uses the model's native inference method

        Args:
            input_ids: Input token IDs. Can be:
                - torch.Tensor: Shape (seq_len,) for single sequence or
                  (batch_size, seq_len) for batch
                - List[int]: Single sequence as list of token IDs
                - np.ndarray: Single sequence as numpy array

        Returns:
            Object with at least a 'logits' attribute containing the model's output
            logits. The exact return type varies by model:
            - HuggingFace models: Returns native model output (e.g., CausalLMOutput)
            - GGUF models: Returns custom ModelOutput object with 'logits' and
              'last_hidden_state' attributes
            - ONNX models: Returns result from model's run_inference method

        Note:
            For GGUF models, batch processing is handled by processing each sequence
            individually and stacking results. For optimal performance with GGUF
            models, consider using single sequences when possible.

        Raises:
            RuntimeError: If inference fails or model doesn't produce expected output
        """
        if self.loaded_model is None:
            self.load()

        # Different models might have different inference methods
        if self.model_source_type == "gguf_file":
            # GGUF models use a different API
            try:
                # Convert input_ids to list if it's a tensor
                if torch.is_tensor(input_ids):
                    if input_ids.dim() == 2:
                        # Batch dimension - process each sequence in the batch
                        batch_size = input_ids.size(0)
                        batch_logits = []

                        for i in range(batch_size):
                            sequence_ids = input_ids[i].tolist()

                            # Reset token counter and evaluate this sequence
                            self.loaded_model.n_tokens = 0
                            self.loaded_model.eval(sequence_ids)

                            # Get logits from the last position for this sequence
                            if (
                                hasattr(self.loaded_model, "_scores")
                                and len(self.loaded_model._scores) > 0
                            ):
                                # Get logits from the last token position
                                logits_np = self.loaded_model._scores[
                                    -1, :
                                ]  # Last token position, all vocab
                                sequence_logits = torch.from_numpy(np.array(logits_np))
                                batch_logits.append(sequence_logits)
                            else:
                                raise RuntimeError("GGUF model did not produce logits")

                        # Stack all sequence logits into batch format
                        logits = torch.stack(batch_logits).unsqueeze(
                            1
                        )  # Shape: (batch_size, 1, vocab_size)
                    else:
                        # Single sequence
                        input_ids = input_ids.tolist()

                        # Reset token counter and evaluate
                        self.loaded_model.n_tokens = 0
                        self.loaded_model.eval(input_ids)

                        # Get logits from the last position
                        # _scores shape is (n_tokens, vocab_size)
                        if (
                            hasattr(self.loaded_model, "_scores")
                            and len(self.loaded_model._scores) > 0
                        ):
                            # Get logits from the last token position
                            logits_np = self.loaded_model._scores[
                                -1, :
                            ]  # Last token position, all vocab
                            logits = torch.from_numpy(np.array(logits_np))

                            # Add batch dimension to match HuggingFace format
                            logits = logits.unsqueeze(0).unsqueeze(
                                0
                            )  # Shape: (1, 1, vocab_size)
                        else:
                            raise RuntimeError("GGUF model did not produce logits")
                elif isinstance(input_ids, np.ndarray):
                    input_ids = input_ids.tolist()

                    # Reset token counter and evaluate
                    self.loaded_model.n_tokens = 0
                    self.loaded_model.eval(input_ids)

                    # Get logits from the last position
                    # _scores shape is (n_tokens, vocab_size)
                    if (
                        hasattr(self.loaded_model, "_scores")
                        and len(self.loaded_model._scores) > 0
                    ):
                        # Get logits from the last token position
                        logits_np = self.loaded_model._scores[
                            -1, :
                        ]  # Last token position, all vocab
                        logits = torch.from_numpy(np.array(logits_np))

                        # Add batch dimension to match HuggingFace format
                        logits = logits.unsqueeze(0).unsqueeze(
                            0
                        )  # Shape: (1, 1, vocab_size)
                    else:
                        raise RuntimeError("GGUF model did not produce logits")
                else:
                    # Already a list - process as single sequence
                    # Reset token counter and evaluate
                    self.loaded_model.n_tokens = 0
                    self.loaded_model.eval(input_ids)

                    # Get logits from the last position
                    # _scores shape is (n_tokens, vocab_size)
                    if (
                        hasattr(self.loaded_model, "_scores")
                        and len(self.loaded_model._scores) > 0
                    ):
                        # Get logits from the last token position
                        logits_np = self.loaded_model._scores[
                            -1, :
                        ]  # Last token position, all vocab
                        logits = torch.from_numpy(np.array(logits_np))

                        # Add batch dimension to match HuggingFace format
                        logits = logits.unsqueeze(0).unsqueeze(
                            0
                        )  # Shape: (1, 1, vocab_size)
                    else:
                        raise RuntimeError("GGUF model did not produce logits")

                # Convert to a format similar to HuggingFace output
                return type(
                    "ModelOutput",
                    (),
                    {
                        "logits": logits,
                        "last_hidden_state": None,  # GGUF doesn't provide this easily
                    },
                )
            except Exception as e:
                raise RuntimeError(
                    f"Error running inference with GGUF model {self.name}: {e}"
                )
        elif hasattr(self.loaded_model, "run_inference"):
            # ONNX models or other models with custom inference methods
            return self.loaded_model.run_inference(input_ids)
        else:
            # HuggingFace models - use native batch processing
            try:
                with torch.no_grad():
                    # Special handling for encoder-decoder models like T5
                    model_type = self.loaded_model.__class__.__name__
                    if (
                        "T5" in model_type
                        or hasattr(self.loaded_model, "encoder")
                        and hasattr(self.loaded_model, "decoder")
                    ):
                        # For encoder-decoder models, we need to provide decoder_input_ids
                        # Use the first token ID as the decoder start token
                        decoder_input_ids = torch.tensor([[0]]).to(
                            input_ids.device
                        )  # Usually 0 is the decoder start token

                        # Try with decoder_input_ids
                        return self.loaded_model(
                            input_ids=input_ids, decoder_input_ids=decoder_input_ids
                        )
                    else:
                        # Standard forward pass for other models
                        return self.loaded_model(input_ids)
            except Exception as e:
                raise RuntimeError(
                    f"Error running inference with model {self.name}: {e}"
                )

    def tokenize(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Tokenize text using the appropriate tokenizer for the model.

        For GGUF models, this uses the built-in tokenizer. For other models,
        it uses the loaded HuggingFace tokenizer.

        Args:
            text: Text to tokenize
            add_special_tokens: Whether to add special tokens (BOS, EOS)

        Returns:
            List of token IDs
        """
        if self.model_source_type == "gguf_file":
            if self.loaded_model is None:
                self.load()
            # GGUF models have their own tokenizer
            return self.loaded_model.tokenize(
                text.encode("utf-8"), add_bos=add_special_tokens
            )
        else:
            # Use HuggingFace tokenizer
            tokenizer = self.load_tokenizer()
            if tokenizer is None:
                raise ValueError(f"No tokenizer available for model {self.name}")
            return tokenizer.encode(text, add_special_tokens=add_special_tokens)

    def get_target_token_probabilities(self, input_ids, target_token_ids):
        """
        Get probabilities for specific target tokens given input IDs.

        This method handles different model architectures and returns the probabilities
        for the specified target tokens.

        Args:
            input_ids: Input token IDs (tensor or list)
            target_token_ids: List of target token IDs to get probabilities for

        Returns:
            Tensor of probabilities for each target token
        """
        if self.loaded_model is None:
            self.load()

        device = self.get_device()

        # Ensure input_ids is a tensor
        if not torch.is_tensor(input_ids):
            input_ids = torch.tensor([input_ids], device=device)
        elif input_ids.dim() == 1:
            input_ids = input_ids.unsqueeze(0)

        # Run inference
        outputs = self.run_inference(input_ids)

        # Extract logits based on model type
        if hasattr(outputs, "logits") and outputs.logits is not None:
            logits = outputs.logits

            # Check the shape of logits to determine model type
            if len(logits.shape) == 2:
                # Sequence classification model (batch_size, num_classes)
                # For these models, we'll use the class probabilities directly
                probs = torch.softmax(logits[0], dim=-1)
            else:
                # Language model (batch_size, sequence_length, vocab_size)
                # Use the last token's prediction
                logits = logits[0, -1, :]
                probs = torch.softmax(logits, dim=-1)

        else:
            # Base models with hidden states - need to project to vocabulary space
            if (
                not hasattr(outputs, "last_hidden_state")
                or outputs.last_hidden_state is None
            ):
                raise ValueError(
                    f"Model {self.name} does not provide logits or hidden states"
                )

            last_hidden_state = outputs.last_hidden_state[0, -1, :]

            # Project to vocabulary space based on model architecture
            if hasattr(self.loaded_model, "cls") and hasattr(
                self.loaded_model.cls, "predictions"
            ):
                # BERT-like models
                logits = self.loaded_model.cls.predictions.decoder(last_hidden_state)
            elif hasattr(self.loaded_model, "lm_head"):
                # GPT-like models
                logits = self.loaded_model.lm_head(last_hidden_state)
            else:
                # For models without a language modeling head, use the embedding matrix
                embedding_layer = self.get_input_embeddings()
                if hasattr(embedding_layer, "weight"):
                    logits = torch.matmul(last_hidden_state, embedding_layer.weight.t())
                else:
                    raise ValueError(
                        f"Could not determine how to project hidden states to vocabulary for model {self.name}"
                    )

            probs = torch.softmax(logits, dim=-1)

        # Extract probabilities for target tokens
        target_probs = torch.stack([probs[tid] for tid in target_token_ids])

        return target_probs

    def get_hash(self) -> str:
        """
        Get a hash that uniquely identifies this model and its configuration.

        Returns:
            Hash string
        """
        # Create a dictionary of all the components that make up the model's identity
        model_dict = {
            "name": self.name,
            "model_source_type": self.model_source_type,
            "model_loader": self.model_loader.__name__
            if hasattr(self.model_loader, "__name__")
            else str(self.model_loader),
            "tokenizer_loader": self.tokenizer_loader.__name__
            if self.tokenizer_loader and hasattr(self.tokenizer_loader, "__name__")
            else str(self.tokenizer_loader),
            "model_loader_kwargs": json.dumps(self.model_loader_kwargs, sort_keys=True),
        }

        # Convert to string and hash
        model_str = json.dumps(model_dict, sort_keys=True)
        return hashlib.md5(model_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict:
        """
        Convert the Model object to a dictionary that can be serialized.

        Returns:
            Dictionary representation of the Model object
        """
        # Create a dictionary with the model's basic information
        model_dict = {
            "id": self.model_info.get("id", ""),
            "canonical_id": self.model_info.get("canonical_id"),
            "model_maker": self.model_info.get("model_maker", ""),
            "model_name": self.model_info.get("model_name", ""),
            "params_count": self.model_info.get("params_count", None),
            "context_length": self.model_info.get("context_length", None),
            "quantization": self.model_info.get("quantization", ""),
            "license": self.model_info.get("license", ""),
            "created_at": self.model_info.get("created_at", datetime.now()),
            "last_updated": self.model_info.get("last_updated"),
            "sources": [],
        }

        # Add sources
        for source in self.model_info.get("sources", []):
            source_dict = {
                "source_id": source.get("source_id", ""),
                "source_type": source.get("source_type", ""),
                "source_identifier": source.get("source_identifier", {}),
                "requires_auth": source.get("requires_auth", False),
                "created_at": source.get("created_at", datetime.now()),
            }
            model_dict["sources"].append(source_dict)

        return model_dict

    def get_canonical_id(self) -> Optional[str]:
        """
        Get the canonical ID for this model.

        Returns:
            The canonical ID if available, None otherwise
        """
        return self.model_info.get("canonical_id")

    @classmethod
    def from_dict(cls, model_dict: Dict, **kwargs) -> "Model":
        """
        Create a Model object from a dictionary.

        Args:
            model_dict: Dictionary representation of a Model object
            **kwargs: Additional keyword arguments to pass to the Model constructor

        Returns:
            Model object
        """
        name = model_dict.get("model_name", "")
        model_info = {
            "id": model_dict.get("id", ""),
            "canonical_id": model_dict.get("canonical_id"),
            "model_maker": model_dict.get("model_maker", ""),
            "model_name": name,
            "params_count": model_dict.get("params_count", None),
            "context_length": model_dict.get("context_length", None),
            "quantization": model_dict.get("quantization", ""),
            "created_at": model_dict.get("created_at", datetime.now()),
            "last_updated": model_dict.get("last_updated"),
            "sources": model_dict.get("sources", []),
        }

        return cls(name=name, model_info=model_info, **kwargs)

    @classmethod
    def validate_source(cls, source_info: Dict) -> bool:
        """
        Validate that the source info is present and valid.

        Args:
            source_info: Dictionary containing source information with:
                - source_type: Type of source (huggingface_api, onnx, gguf)
                - source_identifier: Source-specific information
                - requires_auth: Whether authentication is required (optional)

        Returns:
            bool: True if the model can be loaded, False otherwise
        """
        try:
            # Create a temporary model instance to validate the source
            temp_model = cls(
                name="validation_model",
                model_info={
                    "model_name": "validation_model",
                    "sources": [
                        {
                            "source_type": source_info["source_type"],
                            "source_identifier": source_info["source_identifier"],
                            "requires_auth": source_info.get("requires_auth", False),
                        }
                    ],
                },
            )

            # Check that source type and identifier are valid
            source_type = temp_model._get_primary_source_type()
            source_identifier = temp_model._get_primary_source_identifier()

            if source_type == "unknown" or not source_identifier:
                return False

            return True
        except Exception:
            return False


@dataclass
class ModelFilterCriteria:
    """Data class for specifying model filter criteria."""

    maker: Optional[str] = None
    quantization: Optional[str] = None
    license: Optional[str] = None
    updated_since: Optional[datetime] = None
    # context_length: Optional[int] = None # Example: if you add this, update methods too

    # New fields for params_count comparisons
    params_count_eq: Optional[int] = None  # For exact match (replaces old params_count)
    params_count_gt: Optional[int] = None  # Greater than
    params_count_lt: Optional[int] = None  # Less than
    params_count_gte: Optional[int] = None  # Greater than or equal to
    params_count_lte: Optional[int] = None  # Less than or equal to

    # Backwards compatibility for params_count, will be mapped to params_count_eq
    # This is a property to handle a direct assignment to `params_count` if old code uses it.
    @property
    def params_count(self) -> Optional[int]:
        return self.params_count_eq

    @params_count.setter
    def params_count(self, value: Optional[int]):
        self.params_count_eq = value

    def to_dict(self) -> Dict[str, Any]:
        """Converts the filter criteria to a dictionary, excluding None values."""
        return {
            f.name: getattr(self, f.name)
            for f in dataclasses.fields(self)
            if getattr(self, f.name) is not None
        }

    def is_empty(self) -> bool:
        """Checks if any filter criteria are set."""
        return all(getattr(self, f.name) is None for f in dataclasses.fields(self))

    def to_sql_filters(
        self, table_alias: Optional[str] = None, placeholder_style: str = "?"
    ) -> Tuple[str, List[Any]]:
        """
        Converts filter criteria into SQL WHERE clause conditions and parameters.

        Args:
            table_alias: Optional alias for the table (e.g., 'm').
            placeholder_style: The placeholder style to use ('?' or '%s').

        Returns:
            Tuple containing:
            - SQL WHERE clause string with placeholders
            - List of parameter values to bind
        """
        conditions = []
        params = []

        prefix = f"{table_alias}." if table_alias else ""

        if self.maker:
            conditions.append(f"{prefix}model_maker = {placeholder_style}")
            params.append(self.maker)

        # Updated params_count filtering logic
        if self.params_count_eq is not None:
            conditions.append(f"{prefix}params_count = {placeholder_style}")
            params.append(self.params_count_eq)
        if self.params_count_gt is not None:
            conditions.append(f"{prefix}params_count > {placeholder_style}")
            params.append(self.params_count_gt)
        if self.params_count_lt is not None:
            conditions.append(f"{prefix}params_count < {placeholder_style}")
            params.append(self.params_count_lt)
        if self.params_count_gte is not None:
            conditions.append(f"{prefix}params_count >= {placeholder_style}")
            params.append(self.params_count_gte)
        if self.params_count_lte is not None:
            conditions.append(f"{prefix}params_count <= {placeholder_style}")
            params.append(self.params_count_lte)

        if self.quantization:
            conditions.append(f"{prefix}quantization = {placeholder_style}")
            params.append(self.quantization)

        if self.updated_since:
            conditions.append(f"{prefix}last_updated >= {placeholder_style}")
            params.append(self.updated_since)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        return where_clause, params

    def to_filter_string(self) -> str:
        """
        Generates a human-readable string of active filter criteria for logging.

        Returns:
            A string representing the active filters, or 'No filters applied'.
        """
        active_filters = []
        if self.maker:
            active_filters.append(f"maker='{self.maker}'")

        # Updated params_count string generation
        if self.params_count_eq is not None:
            active_filters.append(f"params_count={self.params_count_eq}")
        if self.params_count_gt is not None:
            active_filters.append(f"params_count>{self.params_count_gt}")
        if self.params_count_lt is not None:
            active_filters.append(f"params_count<{self.params_count_lt}")
        if self.params_count_gte is not None:
            active_filters.append(f"params_count>={self.params_count_gte}")
        if self.params_count_lte is not None:
            active_filters.append(f"params_count<={self.params_count_lte}")

        if self.quantization:
            active_filters.append(f"quantization='{self.quantization}'")
        if self.license:
            active_filters.append(f"license='{self.license}'")

        if self.updated_since:
            active_filters.append(
                f"updated_since>={self.updated_since.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        if not active_filters:
            return "No filters applied"
        return ", ".join(active_filters)


# ============= Canonical Model ID Functions =============


def generate_canonical_id(model_name: str, global_registry_id: int) -> str:
    """
    Generate a canonical ID combining model name and global registry ID.

    Args:
        model_name: The model name (e.g., "bigcode/starcoderbase-1b")
        global_registry_id: The global registry ID (e.g., 161)

    Returns:
        Canonical ID in format "{model_name}_{global_registry_id}"

    Examples:
        >>> generate_canonical_id("bigcode/starcoderbase-1b", 161)
        "bigcode/starcoderbase-1b_161"
        >>> generate_canonical_id("microsoft/phi-3-mini", 42)
        "microsoft/phi-3-mini_42"
    """
    # Validate and clean model_name
    if not model_name or not str(model_name).strip():
        raise ValueError("model_name must be non-empty string")

    # Convert global_registry_id to int if possible
    try:
        global_id = int(global_registry_id)
    except (ValueError, TypeError):
        raise ValueError(
            f"global_registry_id must be convertible to integer, got: {global_registry_id!r}"
        )

    # Ensure the model name is clean for use as an identifier
    clean_model_name = str(model_name).strip()

    return f"{clean_model_name}_{global_id}"


def extract_gguf_filename_base(repo_id: str) -> str:
    """
    Extract the base filename from a GGUF repository ID for pattern matching.

    Args:
        repo_id: Repository ID (e.g., "bartowski/Llama-3.2-3B-Instruct-GGUF")

    Returns:
        Base filename for pattern matching (e.g., "Llama-3.2-3B-Instruct")

    Example:
        >>> extract_gguf_filename_base("bartowski/Llama-3.2-3B-Instruct-GGUF")
        "Llama-3.2-3B-Instruct"
    """
    repo_name = repo_id.split("/")[-1]  # Get part after slash
    if repo_name.lower().endswith("-gguf"):  # Case insensitive check
        filename_base = repo_name[:-5]  # Remove "-gguf" or "-GGUF" suffix
    else:
        # If no "-gguf" suffix, use the repo name as-is
        filename_base = repo_name
    return filename_base


def _find_gguf_file_by_quantization(repo_id: str, quantization: str) -> str:
    """
    Find and download a GGUF file from a repository based on quantization pattern matching.

    Note: This function assumes authentication has already been handled by the calling context.

    Args:
        repo_id: HuggingFace repository ID (e.g., "bartowski/Llama-3.2-3B-Instruct-GGUF")
        quantization: Quantization type to search for (e.g., "Q4_K_M")

    Returns:
        Path to the downloaded GGUF file

    Raises:
        FileNotFoundError: If no matching GGUF files are found
    """

    logger.info(
        f"Downloading GGUF model with quantization {quantization} from {repo_id}..."
    )

    # Extract filename_base from checkpoint using utility function
    filename_base = extract_gguf_filename_base(repo_id)

    # Try multiple case variations for case-insensitive matching
    quantization_variants = [
        quantization,  # Original case
        quantization.lower(),  # Lowercase
        quantization.upper(),  # Uppercase
    ]

    # Remove duplicates while preserving order
    unique_variants = []
    for variant in quantization_variants:
        if variant not in unique_variants:
            unique_variants.append(variant)

    matching_files = []
    actual_file_path = None

    for variant in unique_variants:
        # Create pattern: filename_base + wildcard + quantization + wildcard
        pattern = f"{filename_base}*{variant}*.gguf"
        logger.info(f"Searching for files matching pattern: {pattern}")

        local_dir = f"./.hf_cache/{repo_id.replace('/', '_')}"
        try:
            gguf_dir = snapshot_download(
                repo_id=repo_id,
                allow_patterns=[pattern],
                local_dir=local_dir,
            )

            # Find matching files
            file_pattern = os.path.join(gguf_dir, "**", pattern)
            matching_files = glob.glob(file_pattern, recursive=True)

            if matching_files:
                actual_file_path = matching_files[0]
                logger.info(
                    f"Found matching GGUF file with quantization variant '{variant}': {actual_file_path}"
                )
                break
        except Exception as e:
            logger.debug(f"Failed to download with pattern {pattern}: {e}")
            continue

    if not matching_files:
        tried_patterns = [f"{filename_base}*{v}*.gguf" for v in unique_variants]
        raise FileNotFoundError(
            f"No GGUF files found matching any quantization pattern {tried_patterns} in {repo_id}"
        )

    return actual_file_path


def parse_canonical_id(canonical_id: str) -> tuple[str, int]:
    """
    Parse a canonical ID back into model name and global registry ID.

    Args:
        canonical_id: Canonical ID in format "{model_name}_{global_registry_id}"

    Returns:
        Tuple of (model_name, global_registry_id)

    Examples:
        >>> parse_canonical_id("bigcode/starcoderbase-1b_161")
        ("bigcode/starcoderbase-1b", 161)
        >>> parse_canonical_id("microsoft/phi-3-mini_42")
        ("microsoft/phi-3-mini", 42)
    """
    if not canonical_id or "_" not in canonical_id:
        raise ValueError(
            "Invalid canonical_id format. Expected: {model_name}_{global_registry_id}"
        )

    # Split on the last underscore to handle model names that might contain underscores
    parts = canonical_id.rsplit("_", 1)
    if len(parts) != 2:
        raise ValueError(
            "Invalid canonical_id format. Expected: {model_name}_{global_registry_id}"
        )

    model_name, global_id_str = parts

    try:
        global_registry_id = int(global_id_str)
    except ValueError:
        raise ValueError(f"Invalid global_registry_id in canonical_id: {global_id_str}")

    return model_name, global_registry_id
