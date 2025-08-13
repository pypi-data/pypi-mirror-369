"""
Test module for the InputOutput fingerprinting method.

This module tests the InputOutput fingerprinting method with a real model,
analyzing each component of the algorithm to ensure they make semantic sense.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from vail.fingerprint import InputOutputFingerprintingMethod
from vail.fingerprint.metrics import l1_similarity
from vail.utils.env import load_env

# Load test environment variables
load_env("test")


class RealModelWrapper:
    """
    A simple wrapper for HuggingFace models to match the fingerprinting interface.
    """

    def __init__(self, model_name="distilgpt2"):
        """Initialize with a small model for testing."""
        print(f"Loading model: {model_name}")
        self.model_name = model_name

        # Set device based on availability
        if torch.backends.mps.is_available():
            self._device = "mps"
        elif torch.cuda.is_available():
            self._device = "cuda"
        else:
            self._device = "cpu"
        print(f"Using device: {self._device}")

        # Load model and tokenizer
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Move model to device
        self.model = self.model.to(self._device)
        print("Model loaded successfully")

    def load(self):
        return self.model

    def load_tokenizer(self):
        return self.tokenizer

    def get_device(self):
        return torch.device(self._device)

    def get_embedding_dimension(self):
        return self.model.config.hidden_size

    def get_vocab_size(self):
        return self.model.config.vocab_size

    def get_input_embeddings(self):
        return self.model.get_input_embeddings()

    def run_inference(self, input_tensor):
        # Ensure input tensor is on the correct device and has the right type
        if not isinstance(input_tensor, torch.Tensor):
            input_tensor = torch.tensor(
                input_tensor, device=self._device, dtype=torch.long
            )
        elif input_tensor.device != self._device:
            input_tensor = input_tensor.to(self._device)

        with torch.no_grad():
            return self.model(input_tensor)

    def get_target_token_probabilities(self, input_ids, target_token_ids):
        """
        Get probabilities for specific target tokens given input IDs.

        Args:
            input_ids: Input token IDs (tensor or list)
            target_token_ids: List of target token IDs to get probabilities for

        Returns:
            Tensor of probabilities for each target token
        """
        device = self.get_device()

        # Ensure input_ids is a tensor
        if not torch.is_tensor(input_ids):
            input_ids = torch.tensor([input_ids], device=device)
        elif input_ids.dim() == 1:
            input_ids = input_ids.unsqueeze(0)

        # Run inference
        outputs = self.run_inference(input_ids)

        # Extract logits
        if hasattr(outputs, "logits") and outputs.logits is not None:
            logits = outputs.logits

            # Use the last token's prediction for language models
            if len(logits.shape) == 3:  # [batch, seq_len, vocab]
                logits = logits[0, -1, :]
            else:  # [batch, vocab]
                logits = logits[0]

            # Convert to probabilities
            probs = torch.softmax(logits, dim=-1)

            # Extract probabilities for target tokens
            target_probs = torch.stack([probs[tid] for tid in target_token_ids])

            return target_probs
        else:
            raise ValueError("Model does not provide logits")


def analyze_embeddings(model_wrapper, probe_tokens):
    """
    Analyze the input embeddings for probe tokens.

    Args:
        model_wrapper: The model wrapper
        probe_tokens: List of tokens to analyze

    Returns:
        Tuple of (token_embeddings, visualization_data)
    """
    print("\n=== Analyzing Input Embeddings ===")

    # Get model and tokenizer
    tokenizer = model_wrapper.load_tokenizer()
    embedding_layer = model_wrapper.get_input_embeddings()
    device = model_wrapper.get_device()

    # Process tokens and get embeddings
    token_embeddings = {}
    visualization_data = []

    for token in probe_tokens:
        # Tokenize
        token_ids = tokenizer.encode(token, add_special_tokens=False)
        token_tensor = torch.tensor(token_ids, device=device)

        # Get embeddings
        with torch.no_grad():
            embeddings = embedding_layer(token_tensor)

        # Print info
        token_text = f"{token} ({tokenizer.decode(token_ids)})"
        print(f"Token: {token_text}")
        print(f"  IDs: {token_ids}")
        print(f"  Embedding shape: {embeddings.shape}")
        print(f"  Embedding mean: {embeddings.mean().item():.4f}")
        print(f"  Embedding std: {embeddings.std().item():.4f}")
        print(f"  First few values: {embeddings[0, :5].cpu().numpy()}")

        # Store for return
        token_embeddings[token] = {
            "ids": token_ids,
            "embedding": embeddings.cpu().numpy(),
        }

        # Prepare visualization data
        if len(token_ids) == 1:  # Only visualize single tokens for clarity
            embedding_vec = embeddings[0].cpu().numpy()
            # Store only the first 20 dimensions for visualization
            visualization_data.append((token, embedding_vec[:20]))

    # Visualize embeddings
    if visualization_data:
        plt.figure(figsize=(12, 8))
        for token, embedding in visualization_data:
            plt.plot(embedding, label=token)

        plt.title("Probe Token Embeddings (First 20 Dimensions)")
        plt.xlabel("Dimension")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.savefig("probe_embeddings.png")
        print("Saved embedding visualization to probe_embeddings.png")

    return token_embeddings, visualization_data


def analyze_model_outputs(model_wrapper, probe_tokens, target_tokens):
    """
    Analyze the model outputs for probe tokens.

    Args:
        model_wrapper: The model wrapper
        probe_tokens: List of tokens to use as input
        target_tokens: List of tokens to analyze in the output

    Returns:
        Dict of output analysis data
    """
    print("\n=== Analyzing Model Outputs ===")

    # Get model and tokenizer
    model = model_wrapper.load()  # noqa: F841
    tokenizer = model_wrapper.load_tokenizer()
    device = model_wrapper.get_device()

    # Process target tokens
    target_ids = []
    target_token_texts = []

    for token in target_tokens:
        ids = tokenizer.encode(token, add_special_tokens=False)
        # Include all valid token IDs
        for tid in ids:
            if 0 <= tid < model_wrapper.get_vocab_size():
                target_ids.append(tid)
                target_token_texts.append(f"{token} ({tokenizer.decode([tid])})")

    print(f"Target tokens: {target_token_texts}")

    # Process probe tokens and get model outputs
    output_data = {}
    logits_visualization = []

    for token in probe_tokens:
        # Tokenize
        token_ids = tokenizer.encode(token, add_special_tokens=False)
        input_tensor = torch.tensor([token_ids], device=device)

        # Run inference
        with torch.no_grad():
            outputs = model_wrapper.run_inference(input_tensor)

        # Get logits
        if hasattr(outputs, "logits"):
            logits = outputs.logits

            # Use the last token's prediction for sequence models
            if len(logits.shape) == 3:  # [batch, seq_len, vocab]
                logits = logits[0, -1, :]
            else:  # [batch, vocab]
                logits = logits[0]

            # Get probabilities
            probs = torch.softmax(logits, dim=-1)

            # Extract probabilities for target tokens
            target_probs = {
                target_ids[i]: probs[target_ids[i]].item()  # Store with token ID as key
                for i in range(len(target_ids))
            }

            # Print info
            print(f"\nInput token: {token}")
            print("  Top predicted target tokens:")
            sorted_targets = sorted(
                target_probs.items(), key=lambda x: x[1], reverse=True
            )
            for target_id, prob in sorted_targets[:5]:
                print(f"    {target_id}: {prob:.4f}")

            # Store for return
            output_data[token] = {
                "logits": logits.cpu().numpy(),
                "target_probs": target_probs,
            }

            # Prepare visualization data - only for target tokens
            target_probs_vec = [probs[tid].item() for tid in target_ids[:20]]
            logits_visualization.append((token, target_probs_vec))

    # Visualize target token probabilities - focusing on subtokens
    if logits_visualization:
        plt.figure(figsize=(14, 10))

        # Get the number of subtokens we have probability data for
        num_subtokens = len(logits_visualization[0][1])

        # Set up the bar chart
        x = np.arange(num_subtokens)
        bar_width = 0.2

        # Plot probabilities for each input
        for i, (token, probs) in enumerate(logits_visualization):
            plt.bar(x + i * bar_width, probs, width=bar_width, label=token)

        # Format labels to fit
        formatted_labels = [
            label[:8] + "..." if len(label) > 8 else label
            for label in target_token_texts
        ]

        # Apply labels - no defensive coding, this should work if everything is set up correctly
        plt.xticks(
            x
            + bar_width
            * (len(logits_visualization) - 1)
            / 2,  # Center ticks between grouped bars
            formatted_labels,
            rotation=45,
            ha="right",
        )

        plt.xlabel("Target Subtokens")
        plt.ylabel("Probability")
        plt.title("Target Subtoken Probabilities for Different Inputs")
        plt.legend()
        plt.tight_layout()
        plt.savefig("target_probabilities.png")
        print("Saved target probabilities to target_probabilities.png")

    return output_data


def analyze_linear_approximation(
    model_wrapper, embedding_data, output_data, target_tokens
):
    """
    Analyze the linear approximation component of the algorithm.

    Args:
        model_wrapper: The model wrapper
        embedding_data: Dict of token embeddings
        output_data: Dict of model outputs
        target_tokens: List of target tokens

    Returns:
        Tuple of (transformation_matrix, eigenvalues, fingerprint)
    """
    print("\n=== Analyzing Linear Approximation ===")

    # Get tokenizer
    tokenizer = model_wrapper.load_tokenizer()
    device = model_wrapper.get_device()
    embedding_layer = model_wrapper.get_input_embeddings()

    # Get embedding dimension
    n = model_wrapper.get_embedding_dimension()

    # Get target token embeddings
    target_ids = []
    for token in target_tokens:
        ids = tokenizer.encode(token, add_special_tokens=False)
        if ids:
            # Add all valid token IDs (mimicking the actual functionality)
            for tid in ids:
                if 0 <= tid < model_wrapper.get_vocab_size():
                    target_ids.append(tid)

    target_embeddings = torch.zeros((n, len(target_ids)), device=device)
    with torch.no_grad():
        for j, token_id in enumerate(target_ids):
            token_tensor = torch.tensor([token_id], device=device)
            embedding = embedding_layer(token_tensor)[0]
            target_embeddings[:, j] = embedding

    # Create input embedding matrix V and output matrix U
    probe_tokens = list(embedding_data.keys())
    N = len(probe_tokens)

    V = torch.zeros((n, N), device=device)
    U = torch.zeros((n, N), device=device)

    for i, token in enumerate(probe_tokens):
        # Get embeddings and apply positional encoding
        embeddings = torch.tensor(embedding_data[token]["embedding"], device=device)

        # Create positional encodings (similar to the actual implementation)
        position_ids = torch.arange(embeddings.shape[0], device=device)
        position_embeddings = torch.sin(position_ids.float())

        # Apply positional encoding - fix the dimension alignment
        combined_embeddings = embeddings + position_embeddings.unsqueeze(1)

        # Compute the average embedding (matching the actual implementation)
        v_i = torch.mean(combined_embeddings, dim=0)
        V[:, i] = v_i

        # Get the target probabilities
        target_probs = torch.tensor(
            [output_data[token]["target_probs"][tid] for tid in target_ids],
            device=device,
        )

        # Form linear combination u_i = sum(p_j * w_j)
        u_i = torch.sum(
            torch.stack(
                [
                    target_probs[j] * target_embeddings[:, j]
                    for j in range(len(target_probs))
                ]
            ),
            dim=0,
        )
        U[:, i] = u_i

    # Print some stats about V and U
    print(f"V matrix shape: {V.shape}")
    print(f"V matrix mean: {V.mean().item():.4f}")
    print(f"V matrix std: {V.std().item():.4f}")

    print(f"U matrix shape: {U.shape}")
    print(f"U matrix mean: {U.mean().item():.4f}")
    print(f"U matrix std: {U.std().item():.4f}")

    # Compute transformation matrix A
    V_np = V.cpu().numpy()
    U_np = U.cpu().numpy()

    # Find matrix A such that AV ≈ U using least squares
    V_pinv = np.linalg.pinv(V_np)
    A = U_np @ V_pinv

    print(f"A matrix shape: {A.shape}")
    print(f"A matrix mean: {np.mean(A):.4f}")
    print(f"A matrix std: {np.std(A):.4f}")

    # Calculate the approximation error
    approx_U = A @ V_np
    error = np.mean(np.square(U_np - approx_U))
    print(f"Approximation error: {error:.6f}")

    # Visualize a sample of the A matrix
    plt.figure(figsize=(10, 8))
    # Plot a 10x10 section of the matrix if it's large
    plot_size = min(10, A.shape[0], A.shape[1])
    plt.imshow(A[:plot_size, :plot_size], cmap="viridis")
    plt.colorbar(label="Value")
    plt.title(f"Transformation Matrix A (First {plot_size}x{plot_size} elements)")
    plt.xlabel("Column")
    plt.ylabel("Row")
    plt.savefig("transformation_matrix.png")
    print("Saved transformation matrix visualization to transformation_matrix.png")

    # Extract eigenvalues
    eigenvalues = np.linalg.eigvals(A)
    print(f"Eigenvalues shape: {eigenvalues.shape}")

    # Sort by magnitude and normalize
    sorted_indices = np.argsort(np.abs(eigenvalues))[::-1]
    sorted_eigenvalues = eigenvalues[sorted_indices]

    # Print top eigenvalues
    print("Top 10 eigenvalues by magnitude:")
    for i, ev in enumerate(sorted_eigenvalues[:10]):
        print(f"  {i + 1}: {ev}")

    # Get top n values for fingerprint
    n0 = min(20, len(eigenvalues))
    top_values = np.abs(sorted_eigenvalues[:n0])
    fingerprint = top_values / np.linalg.norm(top_values)

    print(f"Fingerprint shape: {fingerprint.shape}")
    print(f"Fingerprint: {fingerprint}")

    # Visualize eigenvalues
    plt.figure(figsize=(12, 10))
    plt.subplot(2, 1, 1)
    plt.scatter(np.real(eigenvalues), np.imag(eigenvalues), alpha=0.6)
    plt.grid(True)
    plt.title("Eigenvalues in Complex Plane")
    plt.xlabel("Real Part")
    plt.ylabel("Imaginary Part")

    plt.subplot(2, 1, 2)
    plt.bar(range(len(fingerprint)), fingerprint)
    plt.title("Normalized Fingerprint")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("eigenvalues_and_fingerprint.png")
    print(
        "Saved eigenvalues and fingerprint visualization to eigenvalues_and_fingerprint.png"
    )

    return A, eigenvalues, fingerprint


def generate_full_fingerprint(model_wrapper, probe_tokens_path, target_tokens_path):
    """
    Generate a full fingerprint using the InputOutputFingerprintingMethod.

    Args:
        model_wrapper: The model wrapper
        probe_tokens_path: Path to probe tokens file
        target_tokens_path: Path to target tokens file

    Returns:
        Fingerprint as a numpy array, sorted by magnitude (largest to smallest)
    """
    print("\n=== Generating Full Fingerprint ===")

    # Ensure paths are absolute
    probe_tokens_path = os.path.abspath(probe_tokens_path)
    target_tokens_path = os.path.abspath(target_tokens_path)

    print(f"Using probe tokens file: {probe_tokens_path}")
    print(f"Using target tokens file: {target_tokens_path}")

    method = InputOutputFingerprintingMethod(
        n0=20,  # Use a small value for testing/visualization
        probe_tokens_path=probe_tokens_path,
        target_tokens_path=target_tokens_path,
    )

    # Generate fingerprint
    fingerprint = method.generate_fingerprint(model_wrapper)

    # Re-sort the fingerprint to match our step-by-step approach (largest to smallest)
    sorted_indices = np.argsort(fingerprint)[::-1]
    sorted_fingerprint = fingerprint[sorted_indices]

    print(f"Generated fingerprint shape: {sorted_fingerprint.shape}")
    print(f"First few values: {sorted_fingerprint[:5]}")

    return sorted_fingerprint


def run_full_analysis(model_name="distilgpt2"):
    """
    Run a full analysis with a real model.

    Args:
        model_name: Name of the HuggingFace model to test
    """
    # Define small set of probe and target tokens for detailed analysis
    probe_tokens = ["the", "of", "hello", "world", "homomorphism"]
    target_tokens = [
        "the",
        "of",
        "and",
        "to",
        "a",
        "in",
        "is",
        "that",
        "polymorphism",
        "swimmingly",
    ]

    try:
        # Create model wrapper
        model_wrapper = RealModelWrapper(model_name)

        # Analyze input embeddings
        embedding_data, _ = analyze_embeddings(model_wrapper, probe_tokens)

        # Analyze model outputs
        output_data = analyze_model_outputs(model_wrapper, probe_tokens, target_tokens)

        # Analyze linear approximation
        A, eigenvalues, fingerprint = analyze_linear_approximation(
            model_wrapper, embedding_data, output_data, target_tokens
        )

        # Create temporary token files with absolute paths
        current_dir = os.path.abspath(os.getcwd())
        temp_probe_path = os.path.join(current_dir, "temp_probe_tokens.txt")
        temp_target_path = os.path.join(current_dir, "temp_target_tokens.txt")

        try:
            # Write tokens to files
            with open(temp_probe_path, "w") as f:
                f.write("\n".join(probe_tokens))

            with open(temp_target_path, "w") as f:
                f.write("\n".join(target_tokens))

            print("Created temporary token files at:")
            print(f"  Probe tokens: {temp_probe_path}")
            print(f"  Target tokens: {temp_target_path}")

            # Generate full fingerprint using the actual method
            full_fingerprint = generate_full_fingerprint(
                model_wrapper, temp_probe_path, temp_target_path
            )

            # Compare the two fingerprints
            print("\n=== Comparing Fingerprints ===")
            print("1. Step-by-step fingerprint (first 5 values):")
            print(fingerprint[:5])
            print("2. Full method fingerprint (first 5 values):")
            print(full_fingerprint[:5])

            # Visualize comparison
            plt.figure(figsize=(10, 6))

            # Ensure the fingerprints are the same length for comparison
            min_len = min(len(fingerprint), len(full_fingerprint))
            plt.plot(fingerprint[:min_len], label="Step-by-step", alpha=0.7)
            plt.plot(full_fingerprint[:min_len], label="Full method", alpha=0.7)

            plt.title("Fingerprint Comparison")
            plt.xlabel("Index")
            plt.ylabel("Value")
            plt.legend()
            plt.grid(True)
            plt.savefig("fingerprint_comparison.png")
            print("Saved fingerprint comparison to fingerprint_comparison.png")

        finally:
            # Clean up temporary files
            for path in [temp_probe_path, temp_target_path]:
                if os.path.exists(path):
                    os.remove(path)

        print("\n=== Analysis Complete ===")
        print(f"Generated {model_name} fingerprint successfully")

    except Exception as e:
        print(f"Error during analysis: {e}")


def test_io_fingerprint_regression():
    """
    Regression test for the input-output fingerprinting method.
    Compares the fingerprint generated with a known reference fingerprint
    to ensure algorithm consistency.
    """
    # Create model wrapper with a deterministic small model
    model_wrapper = RealModelWrapper("distilgpt2")

    # Use token files from the helper_data directory
    probe_tokens_path = "helper_data/io_tokens/probe_tokens.txt"
    target_tokens_path = "helper_data/io_tokens/target_tokens.txt"

    # Reference fingerprint from a known good run
    # This was generated using the same model and tokens as above
    known_fingerprint = np.array(
        [
            0.012841776257480574,
            0.012841776257480574,
            0.012998572443123343,
            0.012998572443123343,
            0.01313830778398323,
            0.01313830778398323,
            0.016976186556059782,
            0.016976186556059782,
            0.019419675842355055,
            0.019419675842355055,
            0.02231026420149185,
            0.02241093491577133,
            0.02241093491577133,
            0.025064448561560475,
            0.025064448561560475,
            0.030901513480599618,
            0.030901513480599618,
            0.035160469159614606,
            0.05019407161509782,
            0.05019407161509782,
            0.05204601902566832,
            0.05204601902566832,
            0.05205604618985589,
            0.05205604618985589,
            0.05206718408507579,
            0.05388046625242034,
            0.056425863552021484,
            0.056425863552021484,
            0.059473644162574356,
            0.0697731683634851,
            0.11695997185094022,
            0.1233292612511527,
            0.1233292612511527,
            0.12445932366411168,
            0.12445932366411168,
            0.14111378530247443,
            0.14111378530247443,
            0.1909264907640857,
            0.35403208627170496,
            0.823887307308786,
        ]
    )

    # Create fingerprinting method with fixed parameters
    method = InputOutputFingerprintingMethod(
        n0=40,  # Use n0=40 as requested
        probe_tokens_path=probe_tokens_path,
        target_tokens_path=target_tokens_path,
    )

    # Generate fingerprint
    computed_fingerprint = method.generate_fingerprint(model_wrapper)

    # Sort both fingerprints by magnitude to ensure consistent comparison

    # Calculate L1 similarity between fingerprints
    similarity = l1_similarity(known_fingerprint, computed_fingerprint)

    # Print similarity for debugging
    print(f"Known fingerprint: {known_fingerprint}")
    print(f"Computed fingerprint: {computed_fingerprint}")
    print(f"L1 similarity: {similarity}")

    # Test should pass if similarity is high enough
    assert similarity >= 0.99, (
        f"Fingerprint changed significantly! L1 similarity: {similarity}"
    )


if __name__ == "__main__":
    print("====== InputOutput Fingerprinting Method Analysis ======")

    # Try to use real token files if they exist
    probe_tokens_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "sample_data",
        "io_tokens",
        "probe_tokens.txt",
    )
    target_tokens_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "sample_data",
        "io_tokens",
        "target_tokens.txt",
    )

    # Run full analysis
    run_full_analysis("distilgpt2")  # Use a small model for testing

    print("\n====== Analysis complete ======")
