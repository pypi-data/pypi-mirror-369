"""
Test module for GGUF model functionality and comparisons.

This module tests:
1. GGUF tokenizer functionality and special token extraction
2. Raw token embeddings comparison between SafeTensor and GGUF formats
3. Model outputs/logits comparison between SafeTensor and GGUF formats
4. Fingerprints comparison using the InputOutputFingerprintingMethod
"""

import os

import numpy as np
import pytest
import torch

from vail.fingerprint.methods import InputOutputFingerprintingMethod
from vail.fingerprint.metrics import cosine_similarity
from vail.registry.models import Model
from vail.utils.env import load_env
from vail.utils.model_cleanup import cleanup_cache_directories, cleanup_model_instance

# Load test environment variables
load_env("test")
skip_large = os.getenv("RUN_LARGE_TESTS", "0") != "1"

# ── Config ────────────────────────────────────────────────────────────────────
HF_MODEL = "Qwen/Qwen3-0.6B"
GGUF_REPO = "second-state/Qwen3-0.6B-GGUF"
GGUF_FILENAME = "Qwen3-0.6B-f16.gguf"  # Exact f16 quantization!
CTX_LEN = 512
EMBED_DIM = 1024  # Qwen3-0.6B embedding dimension


@pytest.fixture
def safetensor_model():
    """Create SafeTensor model wrapper."""
    return Model(
        name="qwen3_safetensor",
        model_info={
            "model_name": "Qwen3-0.6B",
            "sources": [
                {
                    "source_type": "huggingface_api",
                    "source_identifier": {
                        "loader_class": "AutoModelForCausalLM",
                        "checkpoint": HF_MODEL,
                        "loader_kwargs": {
                            "torch_dtype": "float16",
                        },
                    },
                    "requires_auth": False,
                }
            ],
        },
    )


@pytest.fixture
def gguf_model():
    """Create GGUF model wrapper."""
    return Model(
        name="qwen3_gguf",
        model_info={
            "model_name": "Qwen3-0.6B-f16-GGUF",
            "sources": [
                {
                    "source_type": "gguf_file",
                    "source_identifier": {
                        "checkpoint": GGUF_REPO,
                        "filename": GGUF_FILENAME,
                        "loader_kwargs": {
                            "n_ctx": CTX_LEN,
                        },
                    },
                    "requires_auth": False,
                }
            ],
        },
    )


@pytest.fixture
def test_prompts():
    """Test prompts for model comparison."""
    return [
        "Hello, how are you today?",
        "In a shocking turn of events,",
        "Once upon a time,",
    ]


@pytest.fixture
def test_tokens():
    """Test tokens for embedding comparison."""
    return [
        (1, "<s>"),
        (2, "</s>"),
        (15043, "Hello"),
        (29892, ","),
        (920, "how"),
    ]


@pytest.fixture(scope="module", autouse=True)
def cleanup_models_after_all_tests():
    """Fixture to clean up cache directories only after ALL tests complete."""
    # This runs before all tests in the module
    yield

    # This runs after ALL tests in the module - use utility function
    try:
        cleanup_cache_directories()
    except Exception as e:
        assert False, f"Error cleaning up cache directories: {e}"


class TestLlamaModelComparison:
    """Test class for comparing Llama models in different formats."""

    @pytest.mark.skipif(skip_large, reason="Requires large model download")
    def test_gguf_tokenizer_functionality(self, gguf_model):
        """Test GGUF tokenizer functionality and special token extraction."""
        print("\n=================================")
        print("=== Testing GGUF Tokenizer ===")
        print("=================================")

        try:
            # Load the model
            gguf_model.load()

            # Load the tokenizer (should return GGUFTokenizer)
            tokenizer = gguf_model.load_tokenizer()

            print(f"Tokenizer type: {type(tokenizer)}")
            print(f"Tokenizer class: {tokenizer.__class__.__name__}")

            # Assert tokenizer is not None
            assert tokenizer is not None, "Tokenizer should not be None"

            # Assert tokenizer has the expected class name
            assert tokenizer.__class__.__name__ == "GGUFTokenizer", (
                f"Expected GGUFTokenizer, got {tokenizer.__class__.__name__}"
            )

            # Test basic encoding/decoding
            test_text = "Hello, how are you?"
            print(f"\nTest text: {test_text}")

            # Test encode
            token_ids = tokenizer.encode(test_text)
            print(f"Token IDs: {token_ids}")

            # Assert encode returns a list of integers
            assert isinstance(token_ids, list), "Token IDs should be a list"
            assert len(token_ids) > 0, "Token IDs should not be empty"
            assert all(isinstance(tid, int) for tid in token_ids), (
                "All token IDs should be integers"
            )

            # Test decode
            decoded_text = tokenizer.decode(token_ids)
            print(f"Decoded text: {decoded_text}")

            # Assert decode returns a string
            assert isinstance(decoded_text, str), "Decoded text should be a string"
            # Note: decoded text might not exactly match input due to tokenization
            # but it should contain the main content
            assert "Hello" in decoded_text, "Decoded text should contain 'Hello'"

            # Test encode_plus
            encoded = tokenizer.encode_plus(test_text, return_tensors=None)
            print(f"\nEncode_plus output: {encoded}")

            # Assert encode_plus returns a dictionary with input_ids
            assert isinstance(encoded, dict), "encode_plus should return a dictionary"
            assert "input_ids" in encoded, "encode_plus should contain 'input_ids'"
            assert encoded["input_ids"] == token_ids, (
                "encode_plus input_ids should match encode output"
            )

            # Test batch encoding
            batch_texts = ["Hello world", "How are you?", "This is a test"]
            batch_encoded = tokenizer.batch_encode_plus(batch_texts, padding=True)
            print("\nBatch encoding:")
            for i, text in enumerate(batch_texts):
                print(f"  '{text}' -> {batch_encoded['input_ids'][i]}")

            # Assert batch encoding returns proper structure
            assert isinstance(batch_encoded, dict), (
                "batch_encode_plus should return a dictionary"
            )
            assert "input_ids" in batch_encoded, (
                "batch_encode_plus should contain 'input_ids'"
            )
            assert len(batch_encoded["input_ids"]) == len(batch_texts), (
                "batch_encode_plus should return same number of sequences as input"
            )

            # Test special tokens
            print("\nSpecial tokens (extracted from GGUF metadata):")
            print(
                f"  BOS token: '{tokenizer.bos_token}' (ID: {tokenizer.bos_token_id})"
            )
            print(
                f"  EOS token: '{tokenizer.eos_token}' (ID: {tokenizer.eos_token_id})"
            )
            print(
                f"  UNK token: '{tokenizer.unk_token}' (ID: {tokenizer.unk_token_id})"
            )
            print(
                f"  PAD token: '{tokenizer.pad_token}' (ID: {tokenizer.pad_token_id})"
            )
            print(f"  Vocab size: {tokenizer.vocab_size}")

            # Assert special tokens are properly set
            assert tokenizer.bos_token_id is not None, "BOS token ID should be set"
            assert tokenizer.eos_token_id is not None, "EOS token ID should be set"
            assert tokenizer.unk_token_id is not None, "UNK token ID should be set"
            assert tokenizer.pad_token_id is not None, "PAD token ID should be set"

            # Assert special token IDs are valid integers
            assert isinstance(tokenizer.bos_token_id, int), (
                "BOS token ID should be an integer"
            )
            assert isinstance(tokenizer.eos_token_id, int), (
                "EOS token ID should be an integer"
            )
            assert isinstance(tokenizer.unk_token_id, int), (
                "UNK token ID should be an integer"
            )
            assert isinstance(tokenizer.pad_token_id, int), (
                "PAD token ID should be an integer"
            )

            # Assert vocab size is reasonable
            assert isinstance(tokenizer.vocab_size, int), (
                "Vocab size should be an integer"
            )
            assert tokenizer.vocab_size > 0, "Vocab size should be positive"
            assert tokenizer.vocab_size < 1000000, (
                "Vocab size should be reasonable (< 1M)"
            )

            # Test that special tokens are within vocab range
            assert 0 <= tokenizer.bos_token_id < tokenizer.vocab_size, (
                f"BOS token ID {tokenizer.bos_token_id} should be within vocab range"
            )
            assert 0 <= tokenizer.eos_token_id < tokenizer.vocab_size, (
                f"EOS token ID {tokenizer.eos_token_id} should be within vocab range"
            )
            assert 0 <= tokenizer.unk_token_id < tokenizer.vocab_size, (
                f"UNK token ID {tokenizer.unk_token_id} should be within vocab range"
            )
            assert 0 <= tokenizer.pad_token_id < tokenizer.vocab_size, (
                f"PAD token ID {tokenizer.pad_token_id} should be within vocab range"
            )

            # Show how this is different from hardcoded values
            print("\n🔍 Comparison with default hardcoded LLaMA defaults:")
            print(f"  BOS: extracted={tokenizer.bos_token_id}, old_hardcoded=1")
            print(f"  EOS: extracted={tokenizer.eos_token_id}, old_hardcoded=2")
            print(f"  UNK: extracted={tokenizer.unk_token_id}, old_hardcoded=0")
            print(f"  PAD: extracted={tokenizer.pad_token_id}, old_hardcoded=2")

            # Test round-trip consistency for a simple case
            simple_text = "Hello"
            simple_tokens = tokenizer.encode(simple_text)
            simple_decoded = tokenizer.decode(simple_tokens)
            assert "Hello" in simple_decoded, (
                f"Round-trip failed: '{simple_text}' -> {simple_tokens} -> '{simple_decoded}'"
            )

        finally:
            # Clean up model instance
            try:
                cleanup_model_instance(gguf_model)
            except Exception as e:
                assert False, f"Error cleaning up model instance: {e}"

    @pytest.mark.skipif(skip_large, reason="Requires large model download")
    def test_logits_comparison(self, safetensor_model, gguf_model, test_prompts):
        """Test that logits from both models are similar on same inputs."""
        print("\n=================================")
        print("=== Comparing Model Logits ===")
        print("=================================")

        try:
            # Load models
            safetensor_model.load()
            gguf_model.load()

            similarities = []

            for prompt in test_prompts:
                print(f"\n📝 Testing prompt: {prompt!r}")

                # Use GGUF tokenizer to ensure consistent tokenization
                token_ids = gguf_model.tokenize(prompt, add_special_tokens=True)
                print(
                    f"   Token IDs: {token_ids[:10]}{'...' if len(token_ids) > 10 else ''}"
                )

                token_ids_tensor = torch.stack([torch.tensor(token_ids)])

                # Get outputs from both models
                st_output = safetensor_model.run_inference(token_ids_tensor)
                gguf_output = gguf_model.run_inference(token_ids_tensor)

                # Check that outputs contain logits
                assert hasattr(st_output, "logits") and st_output.logits is not None, (
                    "SafeTensor model output doesn't contain logits"
                )
                assert (
                    hasattr(gguf_output, "logits") and gguf_output.logits is not None
                ), "GGUF model output doesn't contain logits"

                st_logits = st_output.logits[0, -1, :].cpu()
                gguf_logits = gguf_output.logits[0, -1, :].cpu()

                # Compare logits
                st_logits_np = st_logits.numpy()
                gguf_logits_np = gguf_logits.numpy()

                # Cosine similarity
                cosine_sim = cosine_similarity(st_logits_np, gguf_logits_np)
                similarities.append(cosine_sim)
                print(f"   Logits cosine similarity: {cosine_sim:.6f}")

                # Top predictions
                st_top_id = st_logits.argmax().item()
                gguf_top_id = gguf_logits.argmax().item()

                # Try to decode the tokens
                try:
                    tokenizer = safetensor_model.load_tokenizer()
                    if tokenizer:
                        st_token = tokenizer.decode([st_top_id])
                        gguf_token = tokenizer.decode([gguf_top_id])
                    else:
                        st_token = f"[ID: {st_top_id}]"
                        gguf_token = f"[ID: {gguf_top_id}]"
                except Exception:
                    st_token = f"[ID: {st_top_id}]"
                    gguf_token = f"[ID: {gguf_top_id}]"

                print(f"   SafeTensor next token: {st_token!r}")
                print(f"   GGUF next token: {gguf_token!r}")
                print(
                    f"   Token match: {'✅ YES' if st_top_id == gguf_top_id else '❌ NO'}"
                )

                assert cosine_sim > 0.99, f"Logits similarity too low: {cosine_sim}"

            # Check average similarity
            avg_similarity = np.mean(similarities)
            print(f"\nAverage logits similarity: {avg_similarity:.6f}")
            assert avg_similarity > 0.98, (
                f"Average logits similarity too low: {avg_similarity}"
            )

        finally:
            # Clean up model instances explicitly
            cleanup_model_instance(safetensor_model)
            cleanup_model_instance(gguf_model)

    @pytest.mark.skipif(skip_large, reason="Requires large model download")
    @torch.no_grad()
    def test_embeddings_comparison(self, safetensor_model, gguf_model, test_tokens):
        """Test that raw token embeddings are similar between SafeTensor and GGUF models."""
        print("\n=================================")
        print("=== Comparing Raw Token Embeddings ===")
        print("=================================")

        try:
            # Load both models
            safetensor_model.load()
            gguf_model.load()

            # Get input embeddings
            st_embeddings = safetensor_model.get_input_embeddings()
            gguf_embeddings = gguf_model.get_input_embeddings()

            # Compare dimensions
            assert st_embeddings.weight.shape == gguf_embeddings.weight.shape, (
                f"Embedding shapes don't match: {st_embeddings.weight.shape} vs {gguf_embeddings.weight.shape}"
            )

            print(f"Embedding shape: {st_embeddings.weight.shape}")

            # Compare specific tokens
            token_similarities = []

            print("\nToken-by-token comparison:")
            for token_id, token_str in test_tokens:
                st_embed = st_embeddings.weight[token_id].cpu().numpy()
                gguf_embed = gguf_embeddings.weight[token_id].cpu().numpy()

                # Calculate cosine similarity using the proper function
                cosine_sim = cosine_similarity(st_embed, gguf_embed)
                token_similarities.append(cosine_sim)

                max_diff = np.abs(st_embed - gguf_embed).max()

                print(f"  Token {token_id} ('{token_str}'):")
                print(f"    Cosine similarity: {cosine_sim:.6f}")
                print(f"    Max absolute diff: {max_diff:.6f}")

                # Token embeddings should be very similar
                assert cosine_sim > 0.999, (
                    f"Token {token_id} embedding similarity too low: {cosine_sim}"
                )

            # Overall statistics
            print("\nOverall statistics (first 1000 tokens):")
            n_check = min(
                1000, st_embeddings.weight.shape[0], gguf_embeddings.weight.shape[0]
            )
            similarities = []

            for i in range(n_check):
                st_embed = st_embeddings.weight[i].cpu().numpy()
                gguf_embed = gguf_embeddings.weight[i].cpu().numpy()

                # Use the proper cosine similarity function
                sim = cosine_similarity(st_embed, gguf_embed)
                similarities.append(sim)

            mean_sim = np.mean(similarities)
            min_sim = np.min(similarities)
            max_sim = np.max(similarities)

            print(f"  Mean cosine similarity: {mean_sim:.6f}")
            print(f"  Min cosine similarity: {min_sim:.6f}")
            print(f"  Max cosine similarity: {max_sim:.6f}")

            # Embeddings should match almost perfectly
            assert mean_sim > 0.999, f"Mean embedding similarity too low: {mean_sim}"
            assert min_sim > 0.998, f"Min embedding similarity too low: {min_sim}"

            if mean_sim > 0.999:
                print("\n✅ Raw token embeddings match perfectly!")
            else:
                print("\n❌ Raw token embeddings differ!")

        finally:
            # Clean up model instances explicitly
            cleanup_model_instance(safetensor_model)
            cleanup_model_instance(gguf_model)

    @pytest.mark.skipif(skip_large, reason="Requires large model download")
    @torch.no_grad()
    def test_fingerprints_comparison(self, safetensor_model, gguf_model):
        """Test that fingerprints are similar between SafeTensor and GGUF models."""
        print("\n=================================")
        print("=== Comparing Model Fingerprints ===")
        print("=================================")

        try:
            # Create IO fingerprinting method
            fingerprint_method = InputOutputFingerprintingMethod(
                n0=10,  # Small value for faster testing
                probe_tokens_path="helper_data/io_tokens/probe_tokens.txt",
                target_tokens_path="helper_data/io_tokens/target_tokens.txt",
            )

            print("Generating SafeTensor fingerprint...")
            safetensor_fingerprint = fingerprint_method.generate_fingerprint(
                safetensor_model
            )
            print(f"SafeTensor fingerprint shape: {safetensor_fingerprint.shape}")

            print("\nGenerating GGUF fingerprint...")
            gguf_fingerprint = fingerprint_method.generate_fingerprint(gguf_model)
            print(f"GGUF fingerprint shape: {gguf_fingerprint.shape}")

            # Ensure fingerprints have the same shape
            assert safetensor_fingerprint.shape == gguf_fingerprint.shape, (
                f"Fingerprint shapes don't match: {safetensor_fingerprint.shape} vs {gguf_fingerprint.shape}"
            )

            # Compute similarity
            similarity = cosine_similarity(
                safetensor_fingerprint,
                gguf_fingerprint,
            )

            print(f"\nFingerprint Cosine Similarity: {similarity:.6f}")

            # For the same model in different formats, we expect high similarity
            assert similarity > 0.99, f"Fingerprint similarity too low: {similarity}"

            if similarity > 0.99:
                print(
                    "✅ Fingerprints are highly similar - models are likely the same!"
                )
            elif similarity > 0.9:
                print("⚠️  Fingerprints are similar but not identical")
            else:
                print("❌ Fingerprints differ significantly - models may be different")

        finally:
            # Clean up model instances explicitly
            cleanup_model_instance(safetensor_model)
            cleanup_model_instance(gguf_model)


def test_model_fixtures_creation(safetensor_model, gguf_model):
    """Test that model fixtures can be created successfully."""
    assert safetensor_model.name == "qwen3_safetensor"
    assert gguf_model.name == "qwen3_gguf"

    # Verify model info structure
    assert "sources" in safetensor_model.model_info
    assert "sources" in gguf_model.model_info

    # Verify source types
    assert safetensor_model.model_info["sources"][0]["source_type"] == "huggingface_api"
    assert gguf_model.model_info["sources"][0]["source_type"] == "gguf_file"
