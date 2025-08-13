"""
Unified Fingerprinting Methods

This module provides implementations of different fingerprinting methods for
machine learning models.
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

import numpy as np
import torch
from scipy import linalg

from vail.registry import Model
from vail.utils import onnx_utils

# Try importing optional dependencies
try:
    import onnx  # noqa: F401

    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


class UnifiedFingerprintingMethod(ABC):
    """Base class for all fingerprinting methods."""

    def __init__(self, method_name: str, method_type: str):
        """
        Initialize the fingerprinting method.

        Args:
            method_name: Name of the method
            method_type: Type of fingerprinting (input_output, weight, architecture)
        """
        self.method_name = method_name
        self.method_type = method_type

    @abstractmethod
    def generate_fingerprint(self, model: Union[str, Any], **kwargs) -> np.ndarray:
        """
        Generate a fingerprint for the given model.

        Args:
            model: Either a model ID or a Model object
            kwargs: Additional method-specific parameters

        Returns:
            Fingerprint as a numpy array
        """
        pass

    def get_config(self) -> Dict:
        """
        Get the configuration of the fingerprinting method.

        Returns:
            Dictionary with method configuration
        """
        return {"method_name": self.method_name, "method_type": self.method_type}


class InputOutputFingerprintingMethod(UnifiedFingerprintingMethod):
    """Fingerprinting method based on input-output behavior (linear approximation)."""

    def __init__(
        self,
        n0: int = 40,
        probe_tokens_path: str = None,
        target_tokens_path: str = None,
    ):
        """
        Initialize the input-output fingerprinting method.

        Args:
            n0: Parameter controlling the number of probe sequences (default 40)
            probe_tokens_path: Path to a file containing probe tokens (one per line)
            target_tokens_path: Path to a file containing target tokens (one per line)
        """
        super().__init__(
            method_name="input_output_linear_approximation", method_type="input_output"
        )
        self.n0 = n0
        self.probe_tokens_path = probe_tokens_path
        self.target_tokens_path = target_tokens_path
        # Load tokens if a path is provided
        self.probe_tokens = self._load_tokens(self.probe_tokens_path)
        self.target_tokens = self._load_tokens(self.target_tokens_path)

    def _load_tokens(self, file_path: str) -> List[str]:
        """
        Load tokens from the specified file path.

        Args:
            file_path: Path to the file containing tokens (one per line)

        Returns:
            List of tokens
        """
        if not file_path:
            raise ValueError("Token file path not provided")

        if not os.path.exists(file_path):
            raise ValueError(f"Token file path does not exist: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            tokens = f.read().strip().split("\n")

        # Remove duplicates while preserving order
        return list(dict.fromkeys(tokens))

    def _load_target_tokens(self) -> List[str]:
        """Load target tokens from the specified file path (legacy method)."""
        return self._load_tokens(self.target_tokens_path)

    def generate_fingerprint(self, model: Union[str, "Model"], **kwargs) -> np.ndarray:
        """
        Generate fingerprint using linear approximation of input-output behavior.

        Args:
            model: Model to fingerprint (either a Model instance or a model ID)
            **kwargs: Additional parameters

        Returns:
            Fingerprint as a numpy array
        """
        # Load model and tokenizer
        loaded_model = model.load()
        tokenizer = model.load_tokenizer()

        if tokenizer is None:
            raise ValueError("Tokenizer is required for this fingerprinting method")

        device = model.get_device()

        # Get embedding dimension
        n = model.get_embedding_dimension()
        if n is None:
            raise ValueError("Could not determine embedding dimension")

        # Ensure n0 is valid
        n0 = min(self.n0, n)

        # Get embedding layer
        embedding_layer = model.get_input_embeddings()
        if embedding_layer is None:
            raise ValueError("Could not get input embeddings layer")

        # Process probe tokens
        processed_inputs = []
        vocab_size = model.get_vocab_size()  # Get vocabulary size for validation

        for token in self.probe_tokens:
            if isinstance(token, str):
                try:
                    # Use the tokenizer to properly tokenize the string
                    token_ids = tokenizer.encode(token, add_special_tokens=False)
                    # Filter out invalid token IDs
                    valid_ids = [tid for tid in token_ids if 0 <= tid < vocab_size]
                    if valid_ids:  # Only add if there are valid IDs
                        processed_inputs.append(valid_ids)
                except Exception:
                    # Skip tokens that cause encoding issues
                    continue
            else:
                # If it's already a token ID
                if 0 <= token < vocab_size:
                    processed_inputs.append([token])

        # Process target tokens - ensure it matches lin_approx behavior
        if self.target_tokens is None:
            raise ValueError(
                "Target tokens are required but not available. Please provide a valid target_tokens_path."
            )

        target_ids = []
        for token in self.target_tokens:
            if isinstance(token, str):
                try:
                    token_ids = tokenizer.encode(token, add_special_tokens=False)
                    # Filter out invalid token IDs
                    valid_ids = [tid for tid in token_ids if 0 <= tid < vocab_size]
                    if valid_ids:  # Only add if there are valid IDs
                        target_ids.extend(valid_ids)
                except Exception:
                    # Skip tokens that cause encoding issues
                    continue
            else:
                # If it's already a token ID
                if 0 <= token < vocab_size:
                    target_ids.append(token)

        if not target_ids:
            raise ValueError("No valid target token IDs found")

        # Number of tokens
        N = len(processed_inputs)
        if N == 0:
            raise ValueError("No valid probe tokens found")

        M = len(target_ids)

        # Initialize matrices V and U
        V = torch.zeros((n, N), device=device)
        U = torch.zeros((n, N), device=device)

        # Get target token embeddings
        target_embeddings = torch.zeros((n, M), device=device)
        with torch.no_grad():
            for j, token_id in enumerate(target_ids):
                token_tensor = torch.tensor([token_id], device=device)
                embedding = embedding_layer(token_tensor)[0]
                target_embeddings[:, j] = embedding

        # Process each input sequence
        with torch.no_grad():
            for i, token_ids in enumerate(processed_inputs):
                # Convert token IDs to tensors
                token_tensor = torch.tensor(token_ids, device=device)

                # Get embeddings for the token
                embeddings = embedding_layer(token_tensor)

                # Create positional encodings (simplified)
                position_ids = torch.arange(len(token_ids), device=device)
                position_embeddings = torch.sin(position_ids.float())

                # Combine embeddings with positional encodings
                combined_embeddings = embeddings + position_embeddings.unsqueeze(1)

                # Compute the average embedding
                v_i = torch.mean(combined_embeddings, dim=0)

                # Store the average embedding
                V[:, i] = v_i

                # Get target token probabilities using the model's method
                target_probs = model.get_target_token_probabilities(
                    token_ids, target_ids
                )

                # Form linear combination u_i = sum(p_j * w_j)
                u_i = torch.sum(
                    torch.stack(
                        [target_probs[j] * target_embeddings[:, j] for j in range(M)]
                    ),
                    dim=0,
                )
                U[:, i] = u_i

        # Move to CPU for final computation with scipy
        V_np = V.cpu().numpy()
        U_np = U.cpu().numpy()

        # Find matrix A such that AV ≈ U using least squares
        V_pinv = linalg.pinv(V_np)
        A = U_np @ V_pinv
        eigenvalues = np.linalg.eigvals(A)
        top_values = np.sort(np.abs(eigenvalues))[-n0:]
        fingerprint = top_values / np.linalg.norm(top_values)

        # Clean up memory before returning
        # Clear PyTorch tensors
        del V, U, target_embeddings
        del V_np, U_np, V_pinv, A, eigenvalues, top_values

        # Clear loaded model and tokenizer references
        del loaded_model, tokenizer, embedding_layer

        # Force garbage collection
        import gc

        gc.collect()

        # Clear CUDA cache if using GPU
        if device.type == "cuda":
            torch.cuda.empty_cache()

        return fingerprint

    def get_config(self) -> Dict:
        """Get the configuration of the fingerprinting method."""
        config = super().get_config()
        config.update(
            {
                "n0": self.n0,
                "probe_tokens_path": self.probe_tokens_path,
                "target_tokens_path": self.target_tokens_path,
            }
        )
        return config


class WeightFingerprintingMethod(UnifiedFingerprintingMethod):
    """
    Implements weight-based fingerprinting.
    This method analyzes the weights of the model.
    """

    def __init__(self, size: int = 50):
        """
        Initialize the weight-based fingerprinting method.

        Args:
            size: Size parameter for fingerprint matrix
        """
        super().__init__("weight_fingerprint", "weight")
        self.size = size

    def generate_fingerprint(self, model: Any, **kwargs) -> np.ndarray:
        """
        Generate a fingerprint using the model weights.

        Args:
            model: Model object or model ID

        Returns:
            Fingerprint as a numpy array
        """
        # Get model state dict
        loaded_model = model.load()

        # Extract weight matrices from the model
        matrices = []
        for name, param in loaded_model.state_dict().items():
            # Only use weight matrices (2D+)
            if param.dim() > 1:
                matrices.append(param.cpu().detach().numpy())

        # Sort by size
        matrices.sort(key=lambda x: x.size, reverse=True)

        # Combine matrices through multiplication
        combined_matrix = None
        for matrix in matrices:
            if combined_matrix is None:
                combined_matrix = matrix
            else:
                if combined_matrix.shape[1] == matrix.shape[0]:
                    try:
                        # Safe matrix multiply
                        combined_matrix = self._safe_matrix_multiply(
                            combined_matrix, matrix
                        )
                    except:  # noqa: E722
                        continue

        if combined_matrix is None:
            # Return a zero vector as fallback
            return np.zeros(self.size * self.size)

        # Get fingerprint from the combined matrix
        fingerprint = self._get_top_singular_values(combined_matrix, self.size)

        # Normalize
        if np.any(fingerprint):
            fingerprint = fingerprint / np.linalg.norm(fingerprint)

        return fingerprint

    def _safe_matrix_multiply(
        self, matrix1: np.ndarray, matrix2: np.ndarray
    ) -> np.ndarray:
        """Safely multiply two matrices while avoiding overflow."""
        # Convert to float64 for better precision
        matrix1 = matrix1.astype(np.float64)
        matrix2 = matrix2.astype(np.float64)

        # Normalize matrices by their max absolute values
        max1 = np.max(np.abs(matrix1))
        max2 = np.max(np.abs(matrix2))

        if max1 > 0 and max2 > 0:
            matrix1_normalized = matrix1 / max1
            matrix2_normalized = matrix2 / max2

            # Perform multiplication with normalized matrices
            result = np.matmul(matrix1_normalized, matrix2_normalized)

            # Handle any NaN or Inf values
            result = np.nan_to_num(result, 0)
        else:
            result = np.matmul(matrix1, matrix2)

        return result

    def _get_top_singular_values(self, matrix: np.ndarray, size: int) -> np.ndarray:
        """Extract top singular values from a matrix."""
        try:
            # Handle non-finite values
            matrix = np.nan_to_num(matrix, 0)

            # Get singular values
            singular_values = np.linalg.svd(matrix, compute_uv=False)

            # Initialize result array
            result = np.zeros(size * size, dtype=np.float64)

            # Copy values
            n_values = min(len(singular_values), size * size)
            result[:n_values] = singular_values[:n_values]

            return result

        except np.linalg.LinAlgError:
            # Return zeros if SVD fails
            return np.zeros(size * size)

    def get_config(self) -> Dict:
        """Get the configuration of the fingerprinting method."""
        config = super().get_config()
        config.update({"size": self.size})
        return config


class ArchitectureFingerprintingMethod(UnifiedFingerprintingMethod):
    """
    Implements architecture-based fingerprinting for ONNX models.
    This method analyzes the graph structure of the model.
    """

    def __init__(self, size: int = 50):
        """
        Initialize the architecture-based fingerprinting method.

        Args:
            size: Size parameter for fingerprint matrix
        """
        super().__init__("architecture_fingerprint", "architecture")
        self.size = size

        if not ONNX_AVAILABLE:
            raise ImportError("ONNX is required for architecture-based fingerprinting")

    def generate_fingerprint(self, model: Union[str, "Model"], **kwargs) -> np.ndarray:
        """
        Generate a fingerprint using the model architecture.

        Args:
            model: Either a Model object or a model ID
            **kwargs: Additional parameters

        Returns:
            Fingerprint as a numpy array
        """
        # Load model
        if hasattr(model, "load"):
            # Model object provided
            onnx_model = model.load()
        elif isinstance(model, str):
            # Path to ONNX file provided directly
            if os.path.exists(model):
                onnx_model = onnx_utils.load_onnx_model(model)
            else:
                raise FileNotFoundError(f"ONNX model file not found at path: {model}")
        else:
            raise ValueError(
                "Either a Model object or an ONNX model path must be provided"
            )

        # Generate fingerprint
        fingerprint = onnx_utils.generate_onnx_fingerprint(onnx_model, size=self.size)

        return fingerprint

    def get_config(self) -> Dict:
        """Get the configuration of the fingerprinting method."""
        config = super().get_config()
        config.update({"size": self.size})
        return config


def get_fingerprinting_method(
    method_type: str, **kwargs
) -> UnifiedFingerprintingMethod:
    """
    Factory function to create a fingerprinting method.

    Args:
        method_type: Type of fingerprinting method (input_output, weight, architecture)
        kwargs: Additional method-specific parameters

    Returns:
        Fingerprinting method instance
    """
    # Remove model_paths from kwargs as it's handled separately
    method_kwargs = kwargs.copy()
    if "model_paths" in method_kwargs:
        method_kwargs.pop("model_paths")

    if method_type == "input_output":
        # Get parameters for InputOutputFingerprintingMethod
        return InputOutputFingerprintingMethod(
            n0=method_kwargs.get("n0", 40),
            probe_tokens_path=method_kwargs.get("probe_tokens_path", None),
            target_tokens_path=method_kwargs.get("target_tokens_path", None),
        )
    elif method_type == "weight":
        return WeightFingerprintingMethod(**method_kwargs)
    elif method_type == "architecture":
        return ArchitectureFingerprintingMethod(**method_kwargs)
    else:
        raise ValueError(f"Unknown fingerprinting method type: {method_type}")
