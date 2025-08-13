"""
Test module for the models module.
"""

import traceback
from datetime import datetime, timedelta

import pytest

from vail.registry import Model as RegistryModel
from vail.registry.models import ModelFilterCriteria
from vail.utils.env import load_env

# Load test environment variables
load_env("test")


@pytest.fixture
def valid_huggingface_source():
    return {
        "source_type": "huggingface_api",
        "requires_auth": False,
        "source_identifier": '{"loader_class": "AutoModelForCausalLM", "checkpoint": "deepcogito/cogito-v1-preview-llama-3B"}',
    }


@pytest.fixture
def valid_onnx_source():
    return {
        "source_type": "onnx_file",
        "source_identifier": {"file_path": "path/to/model.onnx"},
        "requires_auth": False,
    }


@pytest.fixture
def valid_gguf_source():
    """Fixture for a valid GGUF source using TinyLlama"""
    return {
        "source_type": "gguf_file",
        "source_identifier": {
            "checkpoint": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
            "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "loader_kwargs": {
                "n_ctx": 512,  # Smaller context for testing
                "n_gpu_layers": 0,  # CPU only for CI/CD
            },
        },
        "requires_auth": False,
    }


@pytest.fixture
def valid_gguf_source_local():
    """Fixture for a GGUF source with local file path"""
    return {
        "source_type": "gguf_file",
        "source_identifier": {"file_path": "/path/to/local/model.gguf"},
        "requires_auth": False,
    }


@pytest.fixture
def invalid_source():
    return {
        "source_type": "invalid_type",
        "source_identifier": {},
        "requires_auth": False,
    }


def test_validate_source_huggingface(valid_huggingface_source):
    """Test validate_source with a valid Hugging Face source"""
    try:
        assert RegistryModel.validate_source(valid_huggingface_source) is True
    except Exception:
        print("\nError in test_validate_source_huggingface:")
        print(traceback.format_exc())
        raise


def test_validate_source_onnx(valid_onnx_source):
    """Test validate_source with a valid ONNX source"""
    try:
        assert RegistryModel.validate_source(valid_onnx_source) is True
    except Exception:
        print("\nError in test_validate_source_onnx:")
        print(traceback.format_exc())
        raise


def test_validate_source_gguf(valid_gguf_source):
    """Test validate_source with a valid GGUF source"""
    try:
        assert RegistryModel.validate_source(valid_gguf_source) is True
    except Exception:
        print("\nError in test_validate_source_gguf:")
        print(traceback.format_exc())
        raise


def test_validate_source_gguf_local(valid_gguf_source_local):
    """Test validate_source with a valid local GGUF source"""
    try:
        assert RegistryModel.validate_source(valid_gguf_source_local) is True
    except Exception:
        print("\nError in test_validate_source_gguf_local:")
        print(traceback.format_exc())
        raise


def test_validate_source_invalid(invalid_source):
    """Test validate_source with an invalid source type"""
    try:
        assert RegistryModel.validate_source(invalid_source) is False
    except Exception:
        print("\nError in test_validate_source_invalid:")
        print(traceback.format_exc())
        raise


def test_validate_source_missing_required_fields():
    """Test validate_source with missing required fields"""
    try:
        invalid_source = {
            "source_type": "huggingface_api",
            "source_identifier": {},  # Missing required fields
        }
        assert RegistryModel.validate_source(invalid_source) is False
    except Exception:
        print("\nError in test_validate_source_missing_required_fields:")
        print(traceback.format_exc())
        raise


def test_validate_source_missing_source_type():
    """Test validate_source with missing source_type"""
    try:
        invalid_source = {
            "source_identifier": {
                "loader_class": "AutoModelForCausalLM",
                "checkpoint": "mistralai/Mistral-7B-v0.1",
            }
        }
        assert RegistryModel.validate_source(invalid_source) is False
    except Exception:
        print("\nError in test_validate_source_missing_source_type:")
        print(traceback.format_exc())
        raise


def test_validate_source_missing_source_identifier():
    """Test validate_source with missing source_identifier"""
    try:
        invalid_source = {"source_type": "huggingface_api"}
        assert RegistryModel.validate_source(invalid_source) is False
    except Exception:
        print("\nError in test_validate_source_missing_source_identifier:")
        print(traceback.format_exc())
        raise


def test_validate_source_with_auth_required():
    """Test validate_source with authentication required"""
    try:
        source_with_auth = {
            "source_type": "huggingface_api",
            "source_identifier": {
                "loader_class": "AutoModelForCausalLM",
                "checkpoint": "microsoft/Phi-3-mini-4k-instruct",
            },
            "requires_auth": True,
        }

        assert RegistryModel.validate_source(source_with_auth) is True
    except Exception:
        print("\nError in test_validate_source_with_auth_required:")
        print(traceback.format_exc())
        raise


def test_gguf_model_loading(valid_gguf_source):
    """Test loading a GGUF model from HuggingFace"""
    try:
        model_info = {
            "model_name": "TinyLlama-GGUF-Test",
            "sources": [valid_gguf_source],
        }

        model = RegistryModel(name="TinyLlama-GGUF-Test", model_info=model_info)

        # Test that model can be loaded
        loaded_model = model.load()
        assert loaded_model is not None

        # Test model attributes
        assert hasattr(loaded_model, "n_ctx")
        assert hasattr(loaded_model, "n_vocab")

    except Exception:
        print("\nError in test_gguf_model_loading:")
        print(traceback.format_exc())
        raise


def test_gguf_tokenizer():
    """Test GGUFTokenizer functionality"""
    try:
        from vail.registry.models import GGUFTokenizer

        model_info = {
            "model_name": "TinyLlama-GGUF-Test",
            "sources": [
                {
                    "source_type": "gguf_file",
                    "source_identifier": {
                        "checkpoint": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
                        "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                    },
                    "requires_auth": False,
                }
            ],
        }

        model = RegistryModel(name="TinyLlama-GGUF-Test", model_info=model_info)
        model.load()

        # Load tokenizer
        tokenizer = model.load_tokenizer()
        assert tokenizer is not None
        assert isinstance(tokenizer, GGUFTokenizer)

        # Test basic tokenization
        text = "Hello, world!"
        token_ids = tokenizer.encode(text)
        assert isinstance(token_ids, list)
        assert len(token_ids) > 0
        assert all(isinstance(tid, int) for tid in token_ids)

        # Test decoding
        decoded_text = tokenizer.decode(token_ids)
        assert isinstance(decoded_text, str)
        assert len(decoded_text) > 0

        # Test batch encoding
        texts = ["Hello", "World", "Test"]
        batch_encoded = tokenizer.batch_encode_plus(texts, padding=True)
        assert "input_ids" in batch_encoded
        assert "attention_mask" in batch_encoded
        assert len(batch_encoded["input_ids"]) == 3

        # Test single text encoding with padding
        single_encoded = tokenizer.encode_plus("Test text", padding=True, max_length=10)
        assert "input_ids" in single_encoded
        assert "attention_mask" in single_encoded

        # Test special tokens
        assert hasattr(tokenizer, "bos_token_id")
        assert hasattr(tokenizer, "eos_token_id")
        assert hasattr(tokenizer, "pad_token_id")

    except Exception:
        print("\nError in test_gguf_tokenizer:")
        print(traceback.format_exc())
        raise


def test_gguf_embeddings():
    """Test extracting embeddings from GGUF models"""
    try:
        model_info = {
            "model_name": "TinyLlama-GGUF-Test",
            "sources": [
                {
                    "source_type": "gguf_file",
                    "source_identifier": {
                        "checkpoint": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
                        "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                    },
                    "requires_auth": False,
                }
            ],
        }

        model = RegistryModel(name="TinyLlama-GGUF-Test", model_info=model_info)

        # Get embeddings
        embeddings = model.get_input_embeddings()
        assert embeddings is not None

        # Check embedding properties
        assert hasattr(embeddings, "weight")
        assert hasattr(embeddings, "num_embeddings")
        assert hasattr(embeddings, "embedding_dim")

        # Test dimensions
        embedding_dim = model.get_embedding_dimension()
        assert isinstance(embedding_dim, int)
        assert embedding_dim > 0

        vocab_size = model.get_vocab_size()
        assert isinstance(vocab_size, int)
        assert vocab_size > 0

        # Test that embeddings have correct shape
        # Note: TinyLlama has embedding_dim=1152
        assert embeddings.weight.shape == (vocab_size, embedding_dim)
        assert embeddings.num_embeddings == vocab_size
        assert embeddings.embedding_dim == embedding_dim

    except Exception:
        print("\nError in test_gguf_embeddings:")
        print(traceback.format_exc())
        raise


def test_gguf_inference():
    """Test running inference with GGUF models"""
    try:
        model_info = {
            "model_name": "TinyLlama-GGUF-Test",
            "sources": [
                {
                    "source_type": "gguf_file",
                    "source_identifier": {
                        "checkpoint": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
                        "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                        "loader_kwargs": {
                            "n_ctx": 128,  # Small context for testing
                        },
                    },
                    "requires_auth": False,
                }
            ],
        }

        model = RegistryModel(name="TinyLlama-GGUF-Test", model_info=model_info)
        model.load()

        # Tokenize some text
        text = "The capital of France is"
        token_ids = model.tokenize(text)

        # Run inference
        outputs = model.run_inference(token_ids)
        assert outputs is not None
        assert hasattr(outputs, "logits")
        assert outputs.logits is not None

        # Check logits shape
        assert outputs.logits.dim() == 3  # (batch, sequence, vocab)
        assert outputs.logits.shape[0] == 1  # batch size
        assert outputs.logits.shape[1] == 1  # single token prediction
        assert outputs.logits.shape[2] == model.get_vocab_size()

        # Test get_target_token_probabilities
        target_tokens = [0, 1, 2]  # Some example token IDs
        probs = model.get_target_token_probabilities(token_ids, target_tokens)
        assert probs is not None
        assert len(probs) == len(target_tokens)
        assert all(0 <= p <= 1 for p in probs)

    except Exception:
        print("\nError in test_gguf_inference:")
        print(traceback.format_exc())
        raise


def test_gguf_model_creation_from_dict():
    """Test creating a GGUF model from dictionary representation"""
    try:
        model_dict = {
            "model_id": "test-gguf-001",
            "model_maker": "TheBloke",
            "model_name": "TinyLlama-GGUF",
            "params_count": 1100000000,
            "context_length": 2048,
            "quantization": "Q4_K_M",
            "license": "Apache-2.0",
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "sources": [
                {
                    "source_id": "src-001",
                    "source_type": "gguf_file",
                    "source_identifier": {
                        "checkpoint": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
                        "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                    },
                    "requires_auth": False,
                    "created_at": datetime.now(),
                }
            ],
        }

        # Create model from dict
        model = RegistryModel.from_dict(model_dict)

        # Verify model properties
        assert model.name == "TinyLlama-GGUF"
        assert model.model_source_type == "gguf_file"
        assert model.model_info["quantization"] == "Q4_K_M"
        assert model.model_info["params_count"] == 1100000000

        # Test to_dict conversion
        converted_dict = model.to_dict()
        assert converted_dict["model_name"] == model_dict["model_name"]
        assert converted_dict["quantization"] == model_dict["quantization"]
        assert len(converted_dict["sources"]) == 1
        assert converted_dict["sources"][0]["source_type"] == "gguf_file"

    except Exception:
        print("\nError in test_gguf_model_creation_from_dict:")
        print(traceback.format_exc())
        raise


def test_model_filter_criteria():
    """Test ModelFilterCriteria dataclass"""
    criteria = ModelFilterCriteria(
        maker="Mistral",
        params_count_eq=1000000,
        quantization="8-bit",
        updated_since=datetime.now() - timedelta(days=1),
    )

    assert criteria.maker == "Mistral"
    assert criteria.params_count_eq == 1000000


def test_model_filter_criteria_to_sql_filters():
    """Test ModelFilterCriteria to_sql_filters method for different styles and aliases."""
    now = datetime.now()
    criteria_full = ModelFilterCriteria(
        maker="Mistral",
        params_count_eq=1000000,
        params_count_gt=500000,
        params_count_lte=2000000,
        quantization="8-bit",
        updated_since=now,
    )

    # Test case 1: DuckDB style ('?') without alias
    where_clause, params = criteria_full.to_sql_filters(placeholder_style="?")
    expected_where_duckdb = (
        "model_maker = ? AND "
        "params_count = ? AND params_count > ? AND params_count <= ? AND "
        "quantization = ? AND last_updated >= ?"
    )
    assert where_clause == expected_where_duckdb
    assert params == ["Mistral", 1000000, 500000, 2000000, "8-bit", now]

    # Test case 2: PostgreSQL style ('%s') without alias
    where_clause, params = criteria_full.to_sql_filters(placeholder_style="%s")
    expected_where_postgres = (
        "model_maker = %s AND "
        "params_count = %s AND params_count > %s AND params_count <= %s AND "
        "quantization = %s AND last_updated >= %s"
    )
    assert where_clause == expected_where_postgres
    assert params == ["Mistral", 1000000, 500000, 2000000, "8-bit", now]

    # Test case 3: DuckDB style ('?') with alias 'm'
    where_clause, params = criteria_full.to_sql_filters(
        table_alias="m", placeholder_style="?"
    )
    expected_where_duckdb_alias = (
        "m.model_maker = ? AND "
        "m.params_count = ? AND m.params_count > ? AND m.params_count <= ? AND "
        "m.quantization = ? AND m.last_updated >= ?"
    )
    assert where_clause == expected_where_duckdb_alias
    assert params == ["Mistral", 1000000, 500000, 2000000, "8-bit", now]

    # Test case 4: PostgreSQL style ('%s') with alias 'm'
    where_clause, params = criteria_full.to_sql_filters(
        table_alias="m", placeholder_style="%s"
    )
    expected_where_postgres_alias = (
        "m.model_maker = %s AND "
        "m.params_count = %s AND m.params_count > %s AND m.params_count <= %s AND "
        "m.quantization = %s AND m.last_updated >= %s"
    )
    assert where_clause == expected_where_postgres_alias
    assert params == ["Mistral", 1000000, 500000, 2000000, "8-bit", now]

    # Test case 5: No filters set
    criteria_empty = ModelFilterCriteria()
    where_clause, params = criteria_empty.to_sql_filters()
    assert where_clause == "1=1"
    assert params == []

    # Test case 6: Single filter (maker)
    criteria_single = ModelFilterCriteria(maker="TestMaker")
    where_clause, params = criteria_single.to_sql_filters(
        table_alias="x", placeholder_style="%s"
    )
    assert where_clause == "x.model_maker = %s"
    assert params == ["TestMaker"]

    # Test case 7: Single filter (params_count_eq), default placeholder
    criteria_single_params = ModelFilterCriteria(params_count_eq=500)
    where_clause, params = criteria_single_params.to_sql_filters()
    assert where_clause == "params_count = ?"
    assert params == [500]

    # Test case 8: Single filter (params_count_gt)
    criteria_gt = ModelFilterCriteria(params_count_gt=1000)
    where_clause, params = criteria_gt.to_sql_filters(
        table_alias="t", placeholder_style="%s"
    )
    assert where_clause == "t.params_count > %s"
    assert params == [1000]

    # Test case 9: Single filter (params_count_lte)
    criteria_lte = ModelFilterCriteria(params_count_lte=2000)
    where_clause, params = criteria_lte.to_sql_filters(placeholder_style="?")
    assert where_clause == "params_count <= ?"
    assert params == [2000]


# ===== CANONICAL ID TESTS =====


def test_generate_canonical_id_standalone():
    """Test the standalone generate_canonical_id function."""
    from vail.registry.models import generate_canonical_id

    # Test normal cases
    assert (
        generate_canonical_id("microsoft/phi-3-mini", 42) == "microsoft/phi-3-mini_42"
    )
    assert (
        generate_canonical_id("meta-llama/Llama-3.1-8B", 789)
        == "meta-llama/Llama-3.1-8B_789"
    )

    # Test with float global_id (should convert to int then string)
    assert (
        generate_canonical_id("bigcode/starcoderbase-1b", 161.0)
        == "bigcode/starcoderbase-1b_161"
    )

    # Test with string global_id (should work as-is)
    assert (
        generate_canonical_id("microsoft/DialoGPT-large", "123")
        == "microsoft/DialoGPT-large_123"
    )

    # Test works with model name that already has an underscore
    assert (
        generate_canonical_id("EleutherAI/pythia-1.4b_deduped", 143)
        == "EleutherAI/pythia-1.4b_deduped_143"
    )


def test_parse_canonical_id_standalone():
    """Test the standalone parse_canonical_id function."""
    from vail.registry.models import parse_canonical_id

    # Test normal cases
    model_name, global_id = parse_canonical_id("microsoft/phi-3-mini_42")
    assert model_name == "microsoft/phi-3-mini"
    assert global_id == 42

    model_name, global_id = parse_canonical_id("meta-llama/Llama-3.1-8B_789")
    assert model_name == "meta-llama/Llama-3.1-8B"
    assert global_id == 789

    # Test with hyphenated model names
    model_name, global_id = parse_canonical_id("bigcode/starcoderbase-1b_161")
    assert model_name == "bigcode/starcoderbase-1b"
    assert global_id == 161

    # Test with complex model names containing underscores
    model_name, global_id = parse_canonical_id("EleutherAI/pythia-1.4b_deduped_143")
    assert model_name == "EleutherAI/pythia-1.4b_deduped"
    assert global_id == 143


def test_parse_canonical_id_edge_cases():
    """Test parse_canonical_id with edge cases and error handling."""
    from vail.registry.models import parse_canonical_id

    # Test invalid formats (should raise ValueError)
    with pytest.raises(ValueError, match="Invalid canonical_id format"):
        parse_canonical_id("invalid-format")

    with pytest.raises(ValueError, match="Invalid global_registry_id"):
        parse_canonical_id("no_underscore_at_end")

    with pytest.raises(ValueError, match="Invalid global_registry_id"):
        parse_canonical_id("ends_with_underscore_")

    with pytest.raises(ValueError, match="Invalid global_registry_id"):
        parse_canonical_id("multiple_underscores_but_no_number_at_end_abc")

    # Test non-numeric global ID (should raise ValueError)
    with pytest.raises(ValueError, match="Invalid global_registry_id"):
        parse_canonical_id("model/name_not_a_number")


def test_model_get_canonical_id():
    """Test the Model instance method for getting canonical ID."""
    # Create a model instance with canonical_id in model_info (correct constructor signature)
    model_info = {
        "id": 1,
        "model_name": "microsoft/phi-3-mini",
        "canonical_id": "microsoft/phi-3-mini_42",
        "model_maker": "microsoft",
        "params_count": 3800000000,
        "sources": [
            {
                "source_type": "huggingface_api",
                "source_identifier": {
                    "loader_class": "AutoModelForCausalLM",
                    "checkpoint": "microsoft/phi-3-mini",
                },
                "requires_auth": False,
            }
        ],
    }

    model = RegistryModel(name="microsoft/phi-3-mini", model_info=model_info)
    assert model.get_canonical_id() == "microsoft/phi-3-mini_42"


def test_model_get_canonical_id_not_available():
    """Test Model.get_canonical_id() when canonical_id is not available."""
    # Create a model instance without canonical_id (correct constructor signature)
    model_info = {
        "id": 1,
        "model_name": "test/model",
        "model_maker": "test",
        "params_count": 1000000,
        "sources": [
            {
                "source_type": "huggingface_api",
                "source_identifier": {
                    "loader_class": "AutoModelForCausalLM",
                    "checkpoint": "test/model",
                },
                "requires_auth": False,
            }
        ],
    }

    model = RegistryModel(name="test/model", model_info=model_info)
    assert model.get_canonical_id() is None


def test_canonical_id_roundtrip():
    """Test that generating and parsing canonical IDs is consistent."""
    from vail.registry.models import generate_canonical_id, parse_canonical_id

    test_cases = [
        ("microsoft/phi-3-mini", 42),
        ("meta-llama/Llama-3.1-8B", 789),
        ("bigcode/starcoderbase-1b", 161),
        ("EleutherAI/pythia-1.4b_deduped", 143),
        ("company/model_with_many_underscores_in_name", 999),
    ]

    for original_name, original_id in test_cases:
        # Generate canonical ID
        canonical_id = generate_canonical_id(original_name, original_id)

        # Parse it back
        parsed_name, parsed_id = parse_canonical_id(canonical_id)

        # Should match original
        assert parsed_name == original_name
        assert parsed_id == original_id


def test_gguf_filename_base_extraction():
    """Test filename_base extraction logic for different repo name formats"""
    from vail.registry.models import extract_gguf_filename_base

    test_cases = [
        # (repo_id, expected_filename_base)
        ("bartowski/Llama-3.2-3B-Instruct-GGUF", "Llama-3.2-3B-Instruct"),
        ("bartowski/Llama-3.2-3B-Instruct-gguf", "Llama-3.2-3B-Instruct"),  # lowercase
        ("microsoft/Phi-3-mini-gguf", "Phi-3-mini"),
        ("unsloth/deepseek-70B-gguf", "deepseek-70B"),
        ("someorg/model-without-gguf-suffix", "model-without-gguf-suffix"),  # no suffix
    ]

    for repo_id, expected_base in test_cases:
        # Use the actual function from models.py for consistency
        filename_base = extract_gguf_filename_base(repo_id)
        assert filename_base == expected_base, (
            f"Failed for {repo_id}: expected '{expected_base}', got '{filename_base}'"
        )

    print("✓ GGUF filename_base extraction test passed")


def test_gguf_pattern_based_loading():
    """Test the new checkpoint + quantization loading path"""
    model_info = {
        "model_name": "Test-GGUF-Pattern",
        "quantization": "Q4_K_M",  # This is the key - quantization from model_info
        "sources": [
            {
                "source_type": "gguf_file",
                "source_identifier": {
                    "checkpoint": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                    "loader_kwargs": {"n_ctx": 512},
                },
                "requires_auth": False,
            }
        ],
    }

    model = RegistryModel(name="Test-GGUF-Pattern", model_info=model_info)

    # Test that the model recognizes it should use pattern-based loading
    source_identifier = model._get_primary_source_identifier()
    assert "checkpoint" in source_identifier
    assert "quantization" not in source_identifier  # Should NOT be here
    assert model.model_info.get("quantization") == "Q4_K_M"  # Should be here

    # Test that model_source_type is correct
    assert model.model_source_type == "gguf_file"

    print("✓ GGUF pattern-based loading configuration test passed")
