import os

import numpy as np
import pytest
from fastmcp import Client

import vail.vail_mcp.server as mcp_server_module
from vail.registry import RegistryInterface
from vail.registry.local_interface import LocalRegistryInterface
from vail.utils.env import load_env

# Load test environment variables
load_env("test")


async def call_mcp_tool(tool_name: str, **kwargs):
    """Helper function to call MCP tools through the client"""
    from vail.vail_mcp.server import mcp_server

    async with Client(mcp_server) as client:
        result = await client.call_tool(tool_name, kwargs)
        return result.data


def get_connection_string():
    return os.getenv("DATABASE_URL")


@pytest.fixture()
def local_registry(tmp_path):
    connection_string = get_connection_string()
    if not connection_string:
        pytest.skip("DATABASE_URL environment variable not set in .env.test")
    if "test" not in connection_string:
        raise ValueError(
            "DATABASE_URL must include 'test' to prevent accidental modifications to production database"
        )
    return LocalRegistryInterface(
        connection_string=connection_string, local_db_path=str(tmp_path / "test.duckdb")
    )


@pytest.fixture
def global_registry():
    """Create a RegistryInterface instance for testing (PostgreSQL global test DB)."""
    connection_string = get_connection_string()
    if not connection_string:
        pytest.skip("DATABASE_URL environment variable not set in .env.test")
    if "test" not in connection_string:
        raise ValueError(
            "DATABASE_URL must include 'test' to prevent accidental modifications to production database"
        )

    # Ensure the test database schema is set up
    RegistryInterface.setup_global_registry(connection_string)

    return RegistryInterface(connection_string)


@pytest.fixture
def prime_mcp_with_global_test_registry(global_registry):
    """Sets the MCP server's global REGISTRY to the global PostgreSQL test DB."""
    original_server_registry = mcp_server_module.REGISTRY
    mcp_server_module.REGISTRY = (
        global_registry  # registry is the global PostgreSQL test DB
    )
    yield
    mcp_server_module.REGISTRY = (
        original_server_registry  # Or None for stricter isolation
    )


@pytest.fixture
def prime_mcp_with_local_test_registry(local_registry):
    """Sets the MCP server's global REGISTRY to a local DuckDB instance, synced from global."""
    # Populate the local registry from the global test database
    # (which is populated by the autouse setup_database fixture via the 'registry' fixture)
    sync_result = local_registry.sync_models_from_global(use_last_sync_time=False)
    if sync_result is None or sync_result[0] == 0:
        # Optionally, skip or fail if no models could be synced, as tests might rely on this data.
        # For now, we'll proceed, but tests should be aware.
        raise ValueError(
            "Error: No models were synced to the local registry during prime_mcp_with_local_test_registry."
        )

    original_server_registry = mcp_server_module.REGISTRY
    mcp_server_module.REGISTRY = local_registry
    yield
    mcp_server_module.REGISTRY = original_server_registry  # Or None


NEW_MODEL_SAMPLE_INFO = {
    "model_name": "Athene-v2",
    "model_maker": "Nexusflow",
    "quantization": "bf16",
    "context_length": 32768,
    "params_count": 72000000000,
    "source_type": "huggingface_api",
    "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"Nexusflow\/Athene-V2-Chat"}',
    "license": "apache-2.0",
    "link": "https:\/\/huggingface.co\/Nexusflow\/Athene-V2-Chat",
    "requires_auth": False,
    "human_verified": "X",
    "comment": "Have updated to HF page for link",
}


@pytest.fixture(autouse=True)
def setup_database(
    global_registry, sample_model_info, sample_source_info, sample_fingerprint_info
):
    """Set up the database with sample data before each test."""
    # Clean up any existing data
    with global_registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM fingerprints")
            cur.execute("DELETE FROM model_sources")
            cur.execute("DELETE FROM models")
            cur.execute("DELETE FROM hardware_info")
            conn.commit()

    # Add sample models, sources, and fingerprints
    model_ids = []
    source_ids = []

    # First add models and sources to get their IDs
    for model_info, source_info in zip(sample_model_info, sample_source_info):
        print(f"Adding model: {model_info['model_name']}")
        model_id = global_registry.add_model(model_info)
        model_ids.append(model_id)

        source_id = global_registry.add_model_source(
            model_id, source_info["source_type"], source_info
        )
        source_ids.append(source_id)

    # Then add fingerprints using registry method
    for model_id, fingerprint_info in zip(model_ids, sample_fingerprint_info):
        print(f"Adding fingerprint for model_id: {model_id}")
        fingerprint_type = fingerprint_info["fingerprint_type"]
        fingerprint_vector = np.array(fingerprint_info["fingerprint_vector"])
        fingerprint_config = fingerprint_info["fingerprint_config"]

        try:
            fingerprint_id = global_registry.register_fingerprint(
                model_id=model_id,
                fingerprint_type=fingerprint_type,
                fingerprint_vector=fingerprint_vector,
                fingerprint_config=fingerprint_config,
            )
            print(f"Added fingerprint {fingerprint_id} for model {model_id}")
        except Exception as e:
            print(f"Error adding fingerprint for model {model_id}: {e}")

    yield  # Run the test

    # Cleanup is handled by the cleanup_database fixture


@pytest.fixture(autouse=True)
def cleanup_database(global_registry):
    """Clean up the database after each test."""
    yield  # Run the test
    # After test completes, clean up
    with global_registry._get_connection() as conn:
        with conn.cursor() as cur:
            # Delete in correct order to respect foreign key constraints
            cur.execute("DELETE FROM fingerprints")
            cur.execute("DELETE FROM model_sources")
            cur.execute("DELETE FROM models")
            cur.execute("DELETE FROM hardware_info")
            conn.commit()


@pytest.fixture
def sample_model_info():
    """Create sample model information for testing."""
    return [
        {
            "model_name": "microsoft/phi-4",
            "model_maker": "Microsoft",
            "quantization": "bf16",
            "context_length": 16384,
            "params_count": 14000000000,
        },
        {
            "model_name": "microsoft/Phi-3-mini-4k-instruct",
            "model_maker": "Microsoft",
            "quantization": "bf16",
            "context_length": 4096,
            "params_count": 3800000000,
        },
        {
            "model_name": "EleutherAI/gpt-neo-125m",
            "model_maker": "EleutherAI",
            "quantization": "fp32",
            "context_length": 2048,
            "params_count": 125000000,
        },
        {
            "model_name": "jondurbin/airoboros-70b-3.3",
            "model_maker": "jondurbin",
            "quantization": "bf16",
            "params_count": 70000000000,
        },
    ]


@pytest.fixture
def sample_source_info():
    """Create sample source information for testing."""
    return [
        {
            "source_type": "huggingface_api",
            "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"microsoft/phi-4"}',
            "license": "MIT",
            "link": "https://huggingface.co/microsoft/phi-4",
            "human_verified": "X",
            "requires_auth": False,
            "comment": "",
        },
        {
            "source_type": "huggingface_api",
            "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"microsoft/Phi-3-mini-4k-instruct"}',
            "license": "MIT",
            "link": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct",
            "human_verified": "X",
            "comment": "",
        },
        {
            "source_type": "huggingface_api",
            "source_identifier": '{"loader_class":"AutoModelForCausalLM","checkpoint":"EleutherAI/gpt-neo-125m"}',
            "license": "mit",
            "link": "https://huggingface.co/EleutherAI/gpt-neo-125m",
            "human_verified": "X",
            "requires_auth": False,
            "comment": "",
        },
        {
            "source_type": "huggingface_api",
            "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"jondurbin/airoboros-70b-3.3"}',
            "license": "Llama 3",
            "link": "https://huggingface.co/jondurbin/airoboros-70b-3.3",
            "human_verified": "X",
            "requires_auth": False,
            "comment": "",
        },
    ]


@pytest.fixture
def sample_fingerprint_info():
    """Create sample fingerprint information for testing."""
    return [
        {
            "fingerprint_type": "input_output",
            "fingerprint_vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            "fingerprint_config": {
                "method_name": "input_output_linear_approximation",
                "method_type": "input_output",
                "n0": 10,
            },
        },
        {
            "fingerprint_type": "input_output",
            "fingerprint_vector": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
            "fingerprint_config": {
                "method_name": "input_output_linear_approximation",
                "method_type": "input_output",
                "n0": 10,
            },
        },
        {
            "fingerprint_type": "input_output",
            "fingerprint_vector": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
            "fingerprint_config": {
                "method_name": "input_output_linear_approximation",
                "method_type": "input_output",
                "n0": 10,
            },
        },
        {
            "fingerprint_type": "input_output",
            "fingerprint_vector": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3],
            "fingerprint_config": {
                "method_name": "input_output_linear_approximation",
                "method_type": "input_output",
                "n0": 10,
            },
        },
    ]


################################################################################
### Test MCP tools, some with Local and Global, some with Global only
################################################################################


@pytest.mark.parametrize(
    "registry_fixture",
    ["prime_mcp_with_global_test_registry", "prime_mcp_with_local_test_registry"],
)
@pytest.mark.usefixtures("registry_fixture")
async def test_list_models(registry_fixture):
    response = await call_mcp_tool("list_models")
    assert "models" in response
    assert "total" in response
    assert "offset" in response
    assert "limit" in response
    assert len(response["models"]) > 0
    assert "microsoft/phi-4" in [model["model_name"] for model in response["models"]]


async def test_get_model_template():
    # Test without source type
    response = await call_mcp_tool("get_model_template")
    assert "model_info_template" in response
    assert "examples" in response

    # Test with source type
    response = await call_mcp_tool("get_model_template", source_type="huggingface_api")
    assert "source_info_template" in response


@pytest.mark.usefixtures("prime_mcp_with_global_test_registry")
async def test_add_model():
    response = await call_mcp_tool(
        "add_model",
        model_info=NEW_MODEL_SAMPLE_INFO,
        source_info=NEW_MODEL_SAMPLE_INFO,
    )
    assert "model_id" in response
    assert "source_id" in response
    assert "message" in response


@pytest.mark.parametrize(
    "registry_fixture",
    ["prime_mcp_with_global_test_registry", "prime_mcp_with_local_test_registry"],
)
@pytest.mark.usefixtures("registry_fixture")
async def test_get_fingerprint_vectors(registry_fixture):
    """Test retrieving fingerprint vectors."""
    # Get model IDs from the populated registry
    models_response = await call_mcp_tool("list_models", limit=2)
    model_ids = [str(model["model_id"]) for model in models_response["models"]]

    if not model_ids:
        pytest.skip("No models found in the registry to test fingerprint retrieval.")

    response = await call_mcp_tool("get_fingerprint_vectors", model_ids=model_ids)
    assert isinstance(response, dict)
    assert "results" in response

    results = response["results"]
    assert isinstance(results, list)
    assert len(results) > 0

    # At least one fingerprint should be successful
    success_count = 0
    for result in results:
        assert "model_id" in result
        assert "status" in result
        if result["status"] == "success":
            assert "fingerprint_vector" in result
            assert isinstance(result["fingerprint_vector"], list)
            success_count += 1
        else:
            assert "error" in result

    assert success_count > 0, (
        "Expected at least one fingerprint to be retrieved successfully"
    )


@pytest.mark.parametrize(
    "registry_fixture",
    ["prime_mcp_with_global_test_registry", "prime_mcp_with_local_test_registry"],
)
@pytest.mark.usefixtures("registry_fixture")
async def test_generate_fingerprint(registry_fixture, request):
    """Test generating a fingerprint."""
    # Specifically target the GPT-Neo 125M model since it's smaller and faster to process
    target_model_name = "EleutherAI/gpt-neo-125m"

    # Get the appropriate registry based on fixture
    registry = mcp_server_module.get_registry()

    # Find the specific model by name
    models = registry.find_models()
    target_model = None
    for model in models:
        # Using the model.name property which is directly accessible
        if model.name == target_model_name:
            target_model = model
            break

    if not target_model:
        pytest.skip(f"Model {target_model_name} not found in the registry.")

    model_id = target_model.model_info["id"]

    sources = target_model.model_info["sources"]
    if not sources:
        pytest.skip(f"No sources found for model_id {model_id}.")

    source_id = str(sources[0]["source_id"])
    fingerprint_type = "input_output"  # Example type

    # Note: Actual generation might fail in test env depending on dependencies
    response = await call_mcp_tool(
        "generate_fingerprint",
        source_id=source_id,
        fingerprint_type=fingerprint_type,
        override=True,
    )

    # Assert that status is "success"
    assert "status" in response
    assert response["status"] == "success"

    # Verify that fingerprint data is returned
    assert isinstance(response["fingerprint_config"], dict)

    # For global registry, check fingerprint_id is returned
    if registry.registry_type != "local":
        assert response["fingerprint_id"] is not None
    # For local registry, fingerprint_id should be None
    else:
        assert response["fingerprint_id"] is None


async def test_compare_fp_pairs():
    """Test comparing fingerprint pairs (using dummy data)."""
    dummy_vector = [0.1] * 10  # Example vector
    response = await call_mcp_tool(
        "compare_fp_pairs",
        vector_ref1=dummy_vector,
        vector_var1=dummy_vector,
        vector_ref2=dummy_vector,
        vector_var2=dummy_vector,
        family1_name="FamilyA",
        family2_name="FamilyB",
        model_name_ref1="ModelA_ref",
        model_name_var1="ModelA_var",
        model_name_ref2="ModelB_ref",
        model_name_var2="ModelB_var",
    )
    assert "status" in response
    assert response["status"] == "success"
    assert "visualization_path" in response
    assert response["visualization_path"].endswith(".png")
    assert os.path.exists(response["visualization_path"])
    os.remove(response["visualization_path"])  # Clean up the generated file


async def test_compute_fingerprint_similarity():
    """Test the compute_fingerprint_similarity MCP tool."""
    vec1 = [0.1, 0.2, 0.7]
    vec2 = [0.1, 0.3, 0.6]  # Slightly different

    # Expected L1 similarity: 1 - 0.5 * sum(|v1-v2|) = 1 - 0.5 * (|0.1-0.1| + |0.2-0.3| + |0.7-0.6|)
    # = 1 - 0.5 * (0 + 0.1 + 0.1) = 1 - 0.5 * 0.2 = 1 - 0.1 = 0.9
    expected_similarity = 0.9

    response = await call_mcp_tool(
        "compute_fingerprint_similarity", vector1=vec1, vector2=vec2
    )

    assert response["status"] == "success"
    assert response["similarity_method"] == "l1"
    assert np.isclose(response["similarity"], expected_similarity)


@pytest.mark.usefixtures("prime_mcp_with_global_test_registry")
async def test_add_model_invalid_data():
    # Test with invalid model info
    with pytest.raises(Exception):
        await call_mcp_tool(
            "add_model",
            model_info={"invalid": "data"},
            source_info=NEW_MODEL_SAMPLE_INFO,
        )

    # Test with invalid source info
    with pytest.raises(Exception):
        await call_mcp_tool(
            "add_model",
            model_info=NEW_MODEL_SAMPLE_INFO,
            source_info={"invalid": "data"},
        )


@pytest.mark.usefixtures("prime_mcp_with_local_test_registry")
async def test_get_hardware_profile():
    response = await call_mcp_tool("get_hardware_profile")
    assert "cpu" in response
    assert "memory" in response
    assert "gpu" in response
    assert "disk" in response
    assert "system" in response
    assert "last_updated" in response


@pytest.mark.parametrize(
    "registry_fixture",
    ["prime_mcp_with_global_test_registry", "prime_mcp_with_local_test_registry"],
)
@pytest.mark.usefixtures("registry_fixture")
async def test_get_similarity_matrix(registry_fixture):
    """Test the get_similarity_matrix MCP tool for both local and global registries."""
    # Get a few model IDs from the registry
    models_response = await call_mcp_tool("list_models", limit=3)
    model_ids = [str(model["model_id"]) for model in models_response["models"]]
    if len(model_ids) < 2:
        pytest.skip("Not enough models in the registry to test similarity matrix.")

    response = await call_mcp_tool(
        "get_similarity_matrix",
        model_ids=model_ids,
        fingerprint_type="input_output",
        registry_type="local" if "local" in registry_fixture else "global",
    )
    assert response["status"] == "success"
    assert response["fingerprint_type"] == "input_output"
    assert response["registry_type"] in ("local", "global")
    assert "similarity_matrix" in response
    similarities = response["similarity_matrix"]
    assert isinstance(similarities, list)
    assert all("model_id_1" in s and "model_id_2" in s for s in similarities)
    assert all("l1_similarity" in s or "cosine_similarity" in s for s in similarities)


@pytest.mark.parametrize(
    "registry_fixture",
    ["prime_mcp_with_global_test_registry", "prime_mcp_with_local_test_registry"],
)
@pytest.mark.usefixtures("registry_fixture")
async def test_find_similar_models(registry_fixture):
    """Test the find_similar_models MCP tool for both local and global registries."""
    # Get a reference model ID from the registry
    models_response = await call_mcp_tool("list_models", limit=2)
    model_ids = [str(model["model_id"]) for model in models_response["models"]]
    if not model_ids:
        pytest.skip("No models in the registry to test find_similar_models.")
    reference_model_id = model_ids[0]

    response = await call_mcp_tool(
        "find_similar_models",
        reference_model_id=reference_model_id,
        fingerprint_type="input_output",
        threshold=0.0,  # No threshold to get all
        limit=5,
        registry_type="local" if "local" in registry_fixture else "global",
    )
    assert response["status"] == "success"
    assert response["reference_model_id"] == reference_model_id
    assert response["fingerprint_type"] == "input_output"
    assert response["similarity_metric"] == "l1_similarity"
    assert response["registry_type"] in ("local", "global")
    assert "similar_models" in response
    assert isinstance(response["similar_models"], list)
    # Each similar model should have required fields
    for sim in response["similar_models"]:
        assert "similar_model_id" in sim
        assert "fingerprint_type" in sim
        assert "similarity_score" in sim or "l1_similarity" in sim


async def test_similarity_matrix_consistency_local_vs_global(
    global_registry, local_registry
):
    """Test that local and global registries produce the same similarity matrices for the same models."""
    # Sync local registry with global registry first
    sync_result = local_registry.sync_models_from_global(use_last_sync_time=False)
    if sync_result is None or sync_result[0] == 0:
        pytest.skip("No models were synced to local registry for comparison")

    # Get models from both registries
    global_models = global_registry.find_models()
    local_models = local_registry.find_models()

    if len(global_models) < 2 or len(local_models) < 2:
        pytest.skip(
            "Need at least 2 models in both registries for similarity matrix comparison"
        )

    # Create a mapping between global and local models by name
    global_models_by_name = {model.name: model for model in global_models}
    local_models_by_name = {model.name: model for model in local_models}

    # Find common models (models that exist in both registries)
    common_model_names = set(global_models_by_name.keys()) & set(
        local_models_by_name.keys()
    )
    if len(common_model_names) < 2:
        pytest.skip("Need at least 2 common models between registries for comparison")

    # Use up to 3 common models for testing
    test_model_names = list(common_model_names)[:3]

    # Get corresponding model IDs for each registry
    global_model_ids = [
        global_models_by_name[name].model_info["id"] for name in test_model_names
    ]
    local_model_ids = [
        local_models_by_name[name].model_info["id"] for name in test_model_names
    ]

    print(f"Testing {len(test_model_names)} common models:")
    for i, name in enumerate(test_model_names):
        print(
            f"  {name}: global_id={global_model_ids[i]}, local_id={local_model_ids[i]}"
        )

    # Test different fingerprint types and similarity metrics
    fingerprint_types = ["input_output"]
    similarity_metrics = ["l1_similarity", "cosine_similarity", "euclidean_similarity"]

    for fingerprint_type in fingerprint_types:
        # Check if models have fingerprints of this type in both registries
        global_models_with_fingerprints = []
        local_models_with_fingerprints = []

        for i, name in enumerate(test_model_names):
            global_fp = global_registry.get_fingerprint(
                str(global_model_ids[i]), fingerprint_type
            )
            local_fp = local_registry.get_fingerprint(
                int(local_model_ids[i]), fingerprint_type
            )

            if global_fp is not None and local_fp is not None:
                global_models_with_fingerprints.append(str(global_model_ids[i]))
                local_models_with_fingerprints.append(str(local_model_ids[i]))
                print(
                    f"Model {name}: both registries have {fingerprint_type} fingerprints"
                )
            else:
                print(
                    f"Model {name}: global_fp={'exists' if global_fp is not None else 'missing'}, local_fp={'exists' if local_fp is not None else 'missing'}"
                )

        if len(global_models_with_fingerprints) < 2:
            continue  # Skip this fingerprint type if not enough models have it

        # Get similarity matrix from global registry
        original_server_registry = mcp_server_module.REGISTRY
        try:
            mcp_server_module.REGISTRY = global_registry
            global_response = await call_mcp_tool(
                "get_similarity_matrix",
                model_ids=global_models_with_fingerprints,
                fingerprint_type=fingerprint_type,
                registry_type="global",
            )

            # Get similarity matrix from local registry
            mcp_server_module.REGISTRY = local_registry
            local_response = await call_mcp_tool(
                "get_similarity_matrix",
                model_ids=local_models_with_fingerprints,
                fingerprint_type=fingerprint_type,
                registry_type="local",
            )

        finally:
            mcp_server_module.REGISTRY = original_server_registry

        # Both should succeed
        assert global_response["status"] == "success"
        assert local_response["status"] == "success"

        # Get similarity matrices
        global_similarities = global_response["similarity_matrix"]
        local_similarities = local_response["similarity_matrix"]

        print(f"Global similarities count: {len(global_similarities)}")
        print(f"Local similarities count: {len(local_similarities)}")

        # Both should have the same number of similarity pairs
        # With 3 models, we expect C(3,2) = 3 pairs (only pairs where both models are in the requested list)
        expected_pairs = (
            len(global_models_with_fingerprints)
            * (len(global_models_with_fingerprints) - 1)
            // 2
        )
        assert len(global_similarities) == len(local_similarities), (
            f"Different number of similarity pairs: global={len(global_similarities)}, local={len(local_similarities)}"
        )
        print(
            f"✓ Both registries returned {len(global_similarities)} pairs (expected: {expected_pairs} for {len(global_models_with_fingerprints)} models)"
        )

        # Since model IDs are different, we need to compare by model names
        # Create mappings from model IDs to names for comparison
        global_id_to_name = {
            str(model.model_info["id"]): model.name for model in global_models
        }
        local_id_to_name = {
            str(model.model_info["id"]): model.name for model in local_models
        }

        # Convert similarity results to use model names for comparison
        def normalize_similarity(sim, id_to_name_map):
            return {
                "model_name_1": id_to_name_map.get(
                    str(sim["model_id_1"]), str(sim["model_id_1"])
                ),
                "model_name_2": id_to_name_map.get(
                    str(sim["model_id_2"]), str(sim["model_id_2"])
                ),
                "fingerprint_type": sim["fingerprint_type"],
                "l1_similarity": sim.get("l1_similarity"),
                "cosine_similarity": sim.get("cosine_similarity"),
                "euclidean_similarity": sim.get("euclidean_similarity"),
                "dot_product": sim.get("dot_product"),
            }

        global_normalized = [
            normalize_similarity(sim, global_id_to_name) for sim in global_similarities
        ]
        local_normalized = [
            normalize_similarity(sim, local_id_to_name) for sim in local_similarities
        ]

        # Create sets of similarity pairs for comparison (ignoring order)
        def make_pair_key(sim):
            # Sort model names to ensure consistent key regardless of order
            names = sorted([sim["model_name_1"], sim["model_name_2"]])
            return (names[0], names[1], sim["fingerprint_type"])

        # Create dictionaries mapping pair keys to similarity values
        global_pairs = {make_pair_key(sim): sim for sim in global_normalized}
        local_pairs = {make_pair_key(sim): sim for sim in local_normalized}

        # Verify we have the same set of pairs
        global_keys = set(global_pairs.keys())
        local_keys = set(local_pairs.keys())

        assert global_keys == local_keys, (
            f"Different model pairs between registries. Global: {global_keys}, Local: {local_keys}"
        )

        print(f"Comparing {len(global_keys)} similarity pairs...")

        # Compare similarity values for each pair
        tolerance = 1e-6  # Relaxed tolerance for cross-database comparison

        for pair_key in global_keys:
            global_sim = global_pairs[pair_key]
            local_sim = local_pairs[pair_key]

            model1, model2, fp_type = pair_key
            print(f"\nComparing {model1} ↔ {model2}:")

            for metric in similarity_metrics:
                global_val = global_sim.get(metric)
                local_val = local_sim.get(metric)

                if global_val is not None and local_val is not None:
                    diff = abs(global_val - local_val)
                    assert diff < tolerance, (
                        f"Mismatch in {metric} for models {model1}-{model2}: "
                        f"global={global_val}, local={local_val}, diff={diff}"
                    )
                    print(f"  ✓ {metric}: {global_val:.6f} (diff: {diff:.2e})")
                else:
                    # Both should be None or both should have values
                    assert global_val is None and local_val is None, (
                        f"One registry has None for {metric} while other has value: "
                        f"global={global_val}, local={local_val}"
                    )
                    print(f"  ✓ {metric}: None (both registries)")

        print(f"\n🎉 All {len(global_keys)} similarity pairs match between registries!")
