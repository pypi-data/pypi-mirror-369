"""
Tests for the local registry functionality.

This module provides comprehensive tests for the local registry operations,
including model storage, retrieval, and management in a local environment.
"""

import json
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from vail.registry.local_interface import LocalRegistryInterface
from vail.utils.env import load_env

# Mock transformers before importing RegistryInterface
mock_auto_tokenizer = MagicMock()
with patch.dict(
    "sys.modules", {"transformers": MagicMock(AutoTokenizer=mock_auto_tokenizer)}
):
    from vail.registry import RegistryInterface


# Load test environment variables
load_env("test")


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
    """Create a RegistryInterface instance for testing."""
    connection_string = get_connection_string()
    if not connection_string:
        pytest.skip("DATABASE_URL environment variable not set in .env.test")
    if "test" not in connection_string:
        raise ValueError(
            "DATABASE_URL must include 'test' to prevent accidental modifications to production database"
        )

    # Ensure the test database schema is set up for the global registry
    RegistryInterface.setup_global_registry(connection_string)

    global_registry_instance = RegistryInterface(connection_string)

    return global_registry_instance


@pytest.fixture(autouse=True)
def cleanup_database(local_registry, global_registry):
    """Clean up the database after each test."""
    # After test completes, clean up
    with local_registry._get_local_connection() as conn:
        with conn.cursor() as cur:
            # Delete in correct order to respect foreign key constraints
            cur.execute("DELETE FROM fingerprints")
            cur.execute("DELETE FROM model_sources")
            cur.execute("DELETE FROM models")
            cur.execute("DELETE FROM hardware_info")
            conn.commit()
        # After test completes, clean up
    with global_registry._get_connection() as conn:
        with conn.cursor() as cur:
            # Delete in correct order to respect foreign key constraints
            cur.execute("DELETE FROM fingerprints")
            cur.execute("DELETE FROM model_sources")
            cur.execute("DELETE FROM models")
            cur.execute("DELETE FROM hardware_info")
            conn.commit()
    yield  # Run the test


@pytest.fixture
def sample_model_info():
    """Create sample model information for testing."""
    now = datetime.now()
    return [
        {
            "model_name": "microsoft/phi-4",
            "model_maker": "Microsoft",
            "quantization": "bf16",
            "context_length": 16384,
            "params_count": 14000000000,
            "license": "mit",
            "created_at": now,
            "last_updated": now,
        },
        {
            "model_name": "microsoft/Phi-3-mini-4k-instruct",
            "model_maker": "Microsoft",
            "quantization": "bf16",
            "context_length": 4096,
            "params_count": 3800000000,
            "license": "mit",
            "created_at": now,
            "last_updated": now,
        },
        {
            "model_name": "t5_v1_1-small_conditional_generation",
            "model_maker": "google",
            "quantization": "",
            "context_length": 1024,
            "params_count": 60000000,
            "license": "apache-2.0",
            "created_at": now,
            "last_updated": now,
        },
        {
            "model_name": "jondurbin/airoboros-70b-3.3",
            "model_maker": "jondurbin",
            "quantization": "bf16",
            "context_length": 4096,
            "params_count": 70000000000,
            "license": "llama3",
            "created_at": now,
            "last_updated": now,
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
            "source_identifier": '{"loader_class":"T5ForConditionalGeneration","checkpoint":"google/t5-v1_1-small"}',
            "license": "Apache 2.0",
            "link": "https://huggingface.co/google/t5-v1_1-small",
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


# ----------------------- Tests -----------------------


def test_hardware_info(local_registry, global_registry):
    """Test hardware information operations."""
    # Get hardware info
    hardware_info = local_registry.get_saved_hardware_info()

    # Verify structure
    assert hardware_info.cpu is not None and hardware_info.cpu != {}
    assert hardware_info.memory is not None and hardware_info.memory != {}
    assert hardware_info.gpu is not None  # GPU might be empty list if no GPU available
    assert hardware_info.disk is not None and hardware_info.disk != {}
    assert hardware_info.system is not None and hardware_info.system != {}
    assert hardware_info.last_updated is not None

    # Verify data types
    assert isinstance(hardware_info.cpu["count"], int)
    assert isinstance(hardware_info.memory["total"], int)
    assert isinstance(hardware_info.disk["total"], int)
    assert isinstance(hardware_info.system["os"], str)


def test_sync_models_from_global(
    local_registry, global_registry, sample_model_info, sample_source_info
):
    """Test syncing models from the global registry to the local registry."""
    try:
        for idx, model in enumerate(sample_model_info):
            model_id = global_registry.add_model(model)
            global_registry.add_model_source(
                model_id, "huggingface_api", sample_source_info[idx]
            )

            # Register a simple fingerprint so the local sync accepts the model
            fp_vec = np.array([0.1, 0.2, 0.3, idx * 1.0])
            global_registry.register_fingerprint(
                model_id=str(model_id),
                fingerprint_type="input_output",
                fingerprint_vector=fp_vec,
                fingerprint_config={},
            )
        assert global_registry.count_models() == len(sample_model_info)
    except Exception as e:
        raise e

    # Rather than asserting the return value, let's examine what's actually returned
    result = local_registry.sync_models_from_global()
    assert result is not None, "sync_models_from_global should return a tuple of counts"
    success_count, processed_count = result
    assert success_count == len(sample_model_info), (
        f"Expected {len(sample_model_info)} models to be successfully synced"
    )
    assert processed_count == len(sample_model_info), (
        f"Expected {len(sample_model_info)} models to be processed"
    )

    assert local_registry.count_models() == len(sample_model_info)

    # Verify last_updated time was set for all models
    with local_registry._get_local_connection() as conn:
        result = conn.execute("""
            SELECT id, last_updated FROM models
        """).fetchall()

        assert len(result) == len(sample_model_info)
        for row in result:
            assert row[1] is not None, f"Model {row[0]} has no last_updated time"


def test_sync_one_model_from_global(
    local_registry, global_registry, sample_model_info, sample_source_info
):
    """Test syncing one model from the global registry to the local registry."""
    assert global_registry.count_models() == 0
    for idx, model in enumerate(sample_model_info):
        global_model_id = global_registry.add_model(model)
        global_registry.add_model_source(
            global_model_id, "huggingface_api", sample_source_info[idx]
        )
        fp_vec = np.array([0.1, 0.2, 0.3])
        global_registry.register_fingerprint(
            model_id=str(global_model_id),
            fingerprint_type="input_output",
            fingerprint_vector=fp_vec,
            fingerprint_config={},
        )
    assert global_registry.count_models() == len(sample_model_info)

    status, local_model_id = local_registry.copy_model_from_global(global_model_id)
    assert status == "added"
    assert local_model_id is not None
    local_model = local_registry.find_model(local_model_id)

    assert local_model is not None
    assert local_registry.count_models() == 1

    # Verify last_updated time was set for the copied model
    with local_registry._get_local_connection() as conn:
        result = conn.execute(
            """
            SELECT last_updated FROM models WHERE id = ?
        """,
            (local_model_id,),
        ).fetchone()
        print(result)
        assert result[0] is not None, "Model has no last_updated time"


def test_sync_metadata_helpers(local_registry):
    assert local_registry._get_sync_value("foo") is None

    now = datetime.now()
    local_registry._set_sync_value("foo", now)
    retrieved = local_registry._get_sync_value("foo")

    # DuckDB returns `datetime` objects too – allow slight microsecond drift
    assert abs((retrieved - now).total_seconds()) < 1e-3


def test_sync_all_models_tracks_sync_time(local_registry):
    # First run should set the sync timestamp
    result = local_registry.sync_models_from_global()
    assert result is not None, "Should return a tuple of counts"
    ts1 = local_registry._get_sync_value("models_last_sync")
    assert ts1 is not None

    # Second run should update the timestamp (later than the first)
    result = local_registry.sync_models_from_global()
    assert result is not None, "Should return a tuple of counts"
    ts2 = local_registry._get_sync_value("models_last_sync")
    assert ts2 >= ts1


def test_sync_model_source_update(local_registry, global_registry, sample_model_info):
    """Test that updating a model's sources in the global registry updates the corresponding local model sources when fingerprints match."""

    # --- Step 1: Add model to global registry with an initial source ---
    model_id = global_registry.add_model(sample_model_info[0])
    assert model_id is not None, "Failed to add model to global registry"

    initial_source_info = {
        "source_type": "huggingface_api",
        "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"microsoft/phi-4"}',
        "requires_auth": False,
    }
    global_registry.add_model_source(model_id, "huggingface_api", initial_source_info)

    # Register a fingerprint so similarity checks can work
    fingerprint_vec = np.array([0.1, 0.2, 0.3])
    global_registry.register_fingerprint(
        model_id=str(model_id),
        fingerprint_type="input_output",
        fingerprint_vector=fingerprint_vec,
        fingerprint_config={},
    )

    # --- Step 2: Copy model to local registry ---
    status, local_model_id = local_registry.copy_model_from_global(model_id)
    assert status == "added", "Model should be added for the first time"
    assert local_model_id is not None, "Failed to copy model to local registry"

    local_model = local_registry.find_model(local_model_id)
    assert local_model is not None, "Model not found in local registry after copy"
    assert len(local_model.model_info["sources"]) == 1, (
        "Local model should have exactly one source after initial copy"
    )

    # --- Step 3: Add a NEW source to the model in the global registry ---
    new_source_info = {
        "source_type": "huggingface_api",
        "source_identifier": {
            "loader_class": "AutoModelForCausalLM",
            "checkpoint": "microsoft/phi-4-different",
        },
        "requires_auth": False,
    }
    global_registry.add_model_source(model_id, "huggingface_api", new_source_info)

    global_model = global_registry.find_model(model_id)
    print(f"Global Model Sources: {global_model.model_info['sources']}")

    # --- Step 4: Sync again – should update local sources not create new model ---
    status, updated_local_model_id = local_registry.copy_model_from_global(model_id)
    assert status == "updated", "Model should be updated on second sync"
    assert updated_local_model_id == local_model_id, (
        "Fingerprint match should map to existing local model id"
    )

    updated_local_model = local_registry.find_model(local_model_id)
    assert updated_local_model is not None, "Updated local model not found"

    # Local sources should now mirror global sources (2 entries)
    assert len(updated_local_model.model_info["sources"]) == 2, (
        "Local model sources were not correctly refreshed from global registry"
    )

    # Check that the new source identifier is present in the local registry
    local_source_identifiers_checkpoints = [
        s["source_identifier"].get("checkpoint")
        for s in updated_local_model.model_info["sources"]
    ]
    print(f"Local Model Sources: {local_source_identifiers_checkpoints}")
    print(
        f"New Source Identifier: {new_source_info['source_identifier'].get('checkpoint')}"
    )
    assert (
        new_source_info["source_identifier"].get("checkpoint")
        in local_source_identifiers_checkpoints
    ), "New source identifier not found in local registry after sync"

    # Verify on the DB level that all source rows reference the local model id
    with local_registry._get_local_connection() as conn:
        result = conn.execute(
            """
            SELECT model_id, source_identifier FROM model_sources WHERE model_id = ?
            """,
            (local_model_id,),
        ).fetchall()

        assert len(result) == 2, "Unexpected number of source rows in local DB"
        for row in result:
            assert row[0] == local_model_id, (
                "Source row model_id does not match local model id"
            )
            assert (json.loads(row[1]))[
                "checkpoint"
            ] in local_source_identifiers_checkpoints


def test_incremental_sync_new_model_added_after_sync_time(
    local_registry, global_registry, sample_model_info, sample_source_info
):
    """Test that a new model added to global registry after models_last_sync time is copied to local."""

    # Add initial model (M1) to global and sync
    model_info_1 = sample_model_info[0].copy()
    model_info_1["created_at"] = datetime.now()  # Set created_at for determinism
    global_model_id_1 = global_registry.add_model(model_info_1)
    global_registry.add_model_source(
        global_model_id_1, "huggingface_api", sample_source_info[0]
    )
    fp_vec = np.array([0.1, 0.2, 0.3])
    global_registry.register_fingerprint(
        str(global_model_id_1), "input_output", fp_vec, {}
    )

    assert local_registry.sync_models_from_global()  # Initial full sync
    assert local_registry.count_models() == 1

    # models_last_sync is now set to 'initial_time_str' by the sync operation
    # Verify this (optional, but good for sanity)
    sync_time_after_first_sync = local_registry._get_sync_value("models_last_sync")
    assert sync_time_after_first_sync is not None

    # Advance time and add a new model (M2) to global.
    # Ensure this model's last_updated time is after sync_time_after_first_sync
    model_info_2 = sample_model_info[1].copy()
    # Make sure the new model is considered "updated" after the first sync
    model_info_2["created_at"] = sync_time_after_first_sync + timedelta(seconds=10)
    model_info_2["last_updated"] = sync_time_after_first_sync + timedelta(seconds=10)

    global_model_id_2 = global_registry.add_model(model_info_2)
    global_registry.add_model_source(
        global_model_id_2, "huggingface_api", sample_source_info[1]
    )
    fp_vec_2 = np.array([0.4, 0.5, 0.6])
    global_registry.register_fingerprint(
        str(global_model_id_2), "input_output", fp_vec_2, {}
    )

    # Perform incremental sync
    success_count, processed_count = local_registry.sync_models_from_global(
        use_last_sync_time=True
    )
    assert success_count == 1  # Should only sync the new model M2
    assert processed_count == 1  # Should only process the new model M2

    # Assertions
    assert local_registry.count_models() == 2

    # Verify the model was actually added to the local registry.
    # `status`` should be up_to_date because global model's last_updated timestamp is from
    # when it was added to the global registry, which is before it was synced to local, and
    # that syncing time is the local model's last_updated timestamp.
    status, synced_model_id = local_registry.copy_model_from_global(global_model_id_2)
    assert synced_model_id is not None, (
        "Model ID should be returned if model is present locally"
    )
    assert status == "up_to_date", (
        f"Model sync status was {status}, expected 'up_to_date' after introducing a delay."
    )


def test_incremental_sync_existing_model_updated_after_sync_time(
    local_registry, global_registry, sample_model_info, sample_source_info
):
    """Test that an existing model updated in global after models_last_sync time is updated locally."""
    # Add initial model (M1)
    model_info_1 = sample_model_info[0].copy()
    original_params_count = model_info_1["params_count"]
    model_info_1["created_at"] = datetime.now()
    model_info_1["last_updated"] = datetime.now()
    fp_vec = np.array([0.1, 0.2, 0.3])

    global_model_id_1 = global_registry.add_model(model_info_1)
    global_registry.add_model_source(
        global_model_id_1, "huggingface_api", sample_source_info[0]
    )
    global_registry.register_fingerprint(
        str(global_model_id_1), "input_output", fp_vec, {}
    )

    # Initial sync - should add the model
    local_registry.sync_models_from_global(
        use_last_sync_time=False
    )  # Updated method call

    assert local_registry.count_models() == 1
    local_model_m1_initial = local_registry.find_models()[0]
    assert local_model_m1_initial is not None
    assert local_model_m1_initial.model_info["params_count"] == original_params_count

    # Get the last sync time after initial sync
    sync_time_after_first_sync = local_registry._get_sync_value("models_last_sync")
    assert sync_time_after_first_sync is not None

    # Update M1 in global: change params_count and its last_updated timestamp
    # (Updating the last_updated timestamp to be way later just to trigger the update)
    updated_params_count = original_params_count + 100
    new_last_updated_time = sync_time_after_first_sync + timedelta(hours=1)

    with global_registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {global_registry.schema}.models SET params_count = %s, last_updated = %s WHERE id = %s",
                (
                    updated_params_count,
                    new_last_updated_time,
                    global_model_id_1,
                ),
            )
            conn.commit()

    # Perform incremental sync
    success_count, processed_count = local_registry.sync_models_from_global(
        use_last_sync_time=True
    )  # Updated method call
    assert success_count >= 1  # Should update 1 model
    assert processed_count >= 1  # Should process 1 model

    # Verify direct copy now shows as up-to-date or updated, and properties are correct
    status, model_id = local_registry.copy_model_from_global(global_model_id_1)
    assert status == "updated", f"Model sync status was {status}, expected 'updated'"

    # Assertions
    assert local_registry.count_models() == 1
    local_m1_after_update = local_registry.find_models()[0]
    assert local_m1_after_update is not None
    assert local_m1_after_update.model_info["params_count"] == updated_params_count
    # Check that the local model's last_updated time is now later or equal to the global model's new update time
    # (it will be the time of the *local sync* operation)
    assert (
        local_m1_after_update.model_info["last_updated"] >= sync_time_after_first_sync
    )

    # local_m1_after_update's last_updated should be the time of the second sync
    print(f"Local M1 After Update: {local_m1_after_update}")
    assert (
        abs(
            (
                local_m1_after_update.model_info["last_updated"]
                - sync_time_after_first_sync
            ).total_seconds()
        )
        < 1
    )
    sync_time_after_second_sync = local_registry._get_sync_value("models_last_sync")
    assert (
        abs((sync_time_after_second_sync - sync_time_after_first_sync).total_seconds())
        < 1
    )


def test_get_fingerprint(local_registry, sample_model_info):
    """Test retrieving a specific fingerprint for a model."""
    # Add a model
    model_dict = sample_model_info[0]
    current_time = datetime.now()
    with local_registry._get_local_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO models (
                id, model_maker, model_name,
                params_count, context_length, quantization, created_at, last_updated
            ) VALUES (nextval('model_id_seq'), ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """,
            (
                model_dict["model_maker"],
                model_dict["model_name"],
                model_dict["params_count"],
                model_dict.get("context_length"),
                model_dict["quantization"],
                current_time,
                current_time,
            ),
        )
        local_model_id = cursor.fetchone()[0]

    # Add a fingerprint for this model
    fingerprint_type = "input_output"
    fingerprint_vector = [0.1, 0.2, 0.3]
    fingerprint_config = {"param1": "value1"}
    with local_registry._get_local_connection() as conn:
        conn.execute(
            """
            INSERT INTO fingerprints (
                id, model_id, fingerprint_type, fingerprint_vector, fingerprint_config, created_at, last_updated
            ) VALUES (nextval('fingerprint_id_seq'), ?, ?, ?, ?, ?, ?)
        """,
            (
                local_model_id,
                fingerprint_type,
                fingerprint_vector,
                json.dumps(fingerprint_config),
                current_time,
                current_time,
            ),
        )

    # Test retrieving the fingerprint
    retrieved_fp_vector = local_registry.get_fingerprint(
        local_model_id, fingerprint_type
    )
    assert retrieved_fp_vector is not None
    assert isinstance(retrieved_fp_vector, np.ndarray)

    # Test retrieving a non-existent fingerprint type
    non_existent_fp_vector = local_registry.get_fingerprint(
        local_model_id, "non_existent_type"
    )
    assert non_existent_fp_vector is None

    # Test retrieving from a non-existent model_id
    non_existent_model_fp = local_registry.get_fingerprint(9999, fingerprint_type)
    assert non_existent_model_fp is None


def test_get_all_fingerprints_by_type(local_registry, sample_model_info):
    """Test retrieving all fingerprints of a specific type across all models."""
    current_time = datetime.now()
    fp_type_1 = "input_output"
    fp_type_2 = "activation_maps"

    model_ids = []
    # Add two models
    for i in range(2):
        model_dict = sample_model_info[i]
        with local_registry._get_local_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO models (
                    id, model_maker, model_name,
                    params_count, context_length, quantization, created_at, last_updated
                ) VALUES (nextval('model_id_seq'), ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """,
                (
                    model_dict["model_maker"],
                    model_dict["model_name"],
                    model_dict["params_count"],
                    model_dict.get("context_length"),
                    model_dict["quantization"],
                    current_time,
                    current_time,
                ),
            )
            model_id = cursor.fetchone()[0]
            model_ids.append(model_id)

    # Add fingerprints
    # Model 0: fp_type_1
    # Model 1: fp_type_1 and fp_type_2
    fp_data = [
        (model_ids[0], fp_type_1, [0.1, 0.1], {"cfg": "a"}),
        (model_ids[1], fp_type_1, [0.2, 0.2], {"cfg": "b"}),
        (model_ids[1], fp_type_2, [0.3, 0.3], {"cfg": "c"}),
    ]

    with local_registry._get_local_connection() as conn:
        for mid, ftype, fvec, fcfg in fp_data:
            conn.execute(
                """
                INSERT INTO fingerprints (
                    id, model_id, fingerprint_type, fingerprint_vector, fingerprint_config, created_at, last_updated
                ) VALUES (nextval('fingerprint_id_seq'), ?, ?, ?, ?, ?, ?)
            """,
                (mid, ftype, fvec, json.dumps(fcfg), current_time, current_time),
            )

    # Test retrieving all fingerprints of fp_type_1
    type1_fingerprints = local_registry.get_all_fingerprints_by_type(fp_type_1)
    assert len(type1_fingerprints) == 2
    model_ids_found_type1 = {fp["model_id"] for fp in type1_fingerprints}
    assert model_ids_found_type1 == set(model_ids)
    for fp in type1_fingerprints:
        assert fp["fingerprint_type"] == fp_type_1
        assert fp["created_at"] is not None
        assert fp["last_updated"] is not None
        if fp["model_id"] == model_ids[0]:
            assert fp["config"] == {"cfg": "a"}
        elif fp["model_id"] == model_ids[1]:
            assert fp["config"] == {"cfg": "b"}

    # Test retrieving all fingerprints of fp_type_2
    type2_fingerprints = local_registry.get_all_fingerprints_by_type(fp_type_2)
    assert len(type2_fingerprints) == 1
    assert type2_fingerprints[0]["model_id"] == model_ids[1]
    assert type2_fingerprints[0]["fingerprint_type"] == fp_type_2
    assert type2_fingerprints[0]["config"] == {"cfg": "c"}

    # Test retrieving a non-existent fingerprint type
    non_existent_fingerprints = local_registry.get_all_fingerprints_by_type(
        "non_existent_type"
    )
    assert len(non_existent_fingerprints) == 0


def test_up_to_date_status_based_on_timestamps(
    local_registry, global_registry, sample_model_info
):
    """Test that 'up_to_date' status is returned when global model's timestamp is not newer than local model's."""

    # --- Step 1: Add model to global registry with a specific timestamp ---
    global_timestamp = datetime.now() - timedelta(days=1)  # Yesterday
    model_copy = sample_model_info[0].copy()
    model_copy["created_at"] = global_timestamp
    model_copy["last_updated"] = global_timestamp

    global_model_id = global_registry.add_model(model_copy)

    # Add a source for the model
    source_info = {
        "source_type": "huggingface_api",
        "source_identifier": '{"loader_class":"AutoModelForCausalLM", "checkpoint":"microsoft/phi-test"}',
        "requires_auth": False,
    }
    global_registry.add_model_source(global_model_id, "huggingface_api", source_info)

    # Register a fingerprint so similarity checks can work
    fingerprint_vec = np.array([0.1, 0.2, 0.3])
    global_registry.register_fingerprint(
        model_id=str(global_model_id),
        fingerprint_type="input_output",
        fingerprint_vector=fingerprint_vec,
        fingerprint_config={},
    )

    # --- Step 2: First copy to local registry should be "added" ---
    status1, local_model_id = local_registry.copy_model_from_global(global_model_id)
    assert status1 == "added", "First copy should result in 'added' status"

    # --- Step 3: Try to copy again with same global model (timestamps unchanged) ---
    status2, local_model_id2 = local_registry.copy_model_from_global(global_model_id)
    assert status2 == "up_to_date", (
        f"Expected 'up_to_date' status when global timestamp unchanged, got '{status2}'"
    )
    assert local_model_id == local_model_id2, "Local model ID should be the same"

    # --- Step 4: Update global model with OLDER timestamp (should still be up_to_date) ---
    older_timestamp = global_timestamp - timedelta(days=1)  # Two days ago
    model_copy["last_updated"] = older_timestamp

    # Directly update the global model's timestamp in the database
    with global_registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE models SET last_updated = %s WHERE id = %s",
                (older_timestamp, global_model_id),
            )
            conn.commit()

    # Try to copy again - should be "up_to_date" since global is older
    status3, local_model_id3 = local_registry.copy_model_from_global(global_model_id)
    assert status3 == "up_to_date", (
        f"Expected 'up_to_date' status when global timestamp is older, got '{status3}'"
    )


# ===== CANONICAL ID TESTS =====


def test_find_model_with_canonical_id(
    local_registry, global_registry, sample_model_info, sample_source_info
):
    """Test finding models using canonical IDs in addition to local IDs."""
    # Add a model to the global registry first
    model_dict = sample_model_info[0]
    global_model_id = global_registry.add_model(model_dict)
    global_registry.add_model_source(
        global_model_id, "huggingface_api", sample_source_info[0]
    )

    # Add a fingerprint to make it sync-eligible
    fp_vec = np.array([0.1, 0.2, 0.3])
    global_registry.register_fingerprint(
        model_id=str(global_model_id),
        fingerprint_type="input_output",
        fingerprint_vector=fp_vec,
        fingerprint_config={},
    )

    # Copy the model to local registry
    status, local_model_id = local_registry.copy_model_from_global(global_model_id)
    assert status == "added"
    assert local_model_id is not None

    # Test finding by local ID (should still work)
    model_by_local_id = local_registry.find_model(local_model_id)
    assert model_by_local_id is not None
    assert model_by_local_id.model_info["id"] == local_model_id

    # Test finding by canonical ID (new functionality)
    expected_canonical_id = f"{model_dict['model_name']}_{global_model_id}"
    model_by_canonical_id = local_registry.find_model(expected_canonical_id)
    assert model_by_canonical_id is not None
    assert model_by_canonical_id.model_info["id"] == local_model_id
    assert model_by_canonical_id.model_info["canonical_id"] == expected_canonical_id

    # Both should return the same model
    assert (
        model_by_local_id.model_info["model_name"]
        == model_by_canonical_id.model_info["model_name"]
    )


def test_find_model_canonical_id_not_found(local_registry):
    """Test that find_model returns None for non-existent canonical IDs."""
    # Try to find a model with a canonical ID that doesn't exist
    non_existent_model = local_registry.find_model("non/existent_999")
    assert non_existent_model is None


def test_find_model_canonical_id_mixed_types(
    local_registry, global_registry, sample_model_info, sample_source_info
):
    """Test find_model with various input types for IDs."""
    # Add a model to global registry first
    model_dict = sample_model_info[0]
    global_model_id = global_registry.add_model(model_dict)
    global_registry.add_model_source(
        global_model_id, "huggingface_api", sample_source_info[0]
    )

    # Add fingerprint
    fp_vec = np.array([0.1, 0.2, 0.3])
    global_registry.register_fingerprint(
        model_id=str(global_model_id),
        fingerprint_type="input_output",
        fingerprint_vector=fp_vec,
        fingerprint_config={},
    )

    # Copy to local registry
    status, local_model_id = local_registry.copy_model_from_global(global_model_id)
    assert status == "added"

    expected_canonical_id = f"{model_dict['model_name']}_{global_model_id}"

    # Test with integer local ID
    model1 = local_registry.find_model(local_model_id)
    assert model1 is not None

    # Test with string representation of local ID
    model2 = local_registry.find_model(str(local_model_id))
    assert model2 is not None

    # Test with float representation of local ID (should convert to int)
    model3 = local_registry.find_model(float(local_model_id))
    assert model3 is not None

    # Test with canonical ID (string)
    model4 = local_registry.find_model(expected_canonical_id)
    assert model4 is not None

    # All should return the same model
    assert all(
        model.model_info["id"] == local_model_id
        for model in [model1, model2, model3, model4]
    )


def test_canonical_id_in_model_info(
    local_registry, global_registry, sample_model_info, sample_source_info
):
    """Test that canonical_id is included in model info (to_dict)."""
    # Add a model to global registry first
    model_dict = sample_model_info[0]
    global_model_id = global_registry.add_model(model_dict)
    global_registry.add_model_source(
        global_model_id, "huggingface_api", sample_source_info[0]
    )

    # Add fingerprint
    fp_vec = np.array([0.1, 0.2, 0.3])
    global_registry.register_fingerprint(
        model_id=str(global_model_id),
        fingerprint_type="input_output",
        fingerprint_vector=fp_vec,
        fingerprint_config={},
    )

    # Copy to local registry
    status, local_model_id = local_registry.copy_model_from_global(global_model_id)
    assert status == "added"

    # Retrieve the model and check serialization
    model = local_registry.find_model(local_model_id)
    model_dict_result = model.to_dict()

    expected_canonical_id = f"{model_dict['model_name']}_{global_model_id}"
    assert "canonical_id" in model_dict_result
    assert model_dict_result["canonical_id"] == expected_canonical_id


def test_canonical_id_column_exists(local_registry):
    """Test that the canonical_id column exists in the models table."""
    # The canonical_id column should always exist in the models table
    with local_registry._get_local_connection() as conn:
        cursor = conn.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'models' AND column_name = 'canonical_id'
        """)
        assert cursor.fetchone() is not None


def test_canonical_id_sync_behavior(
    local_registry, global_registry, sample_model_info, sample_source_info
):
    """Test that canonical_id is properly set during sync operations."""
    # Add models to global registry
    model_dict1 = sample_model_info[0]
    model_dict2 = sample_model_info[1]  # Assuming there's a second model

    global_model_id1 = global_registry.add_model(model_dict1)
    global_model_id2 = global_registry.add_model(model_dict2)

    global_registry.add_model_source(
        global_model_id1, "huggingface_api", sample_source_info[0]
    )
    global_registry.add_model_source(
        global_model_id2, "huggingface_api", sample_source_info[1]
    )

    # Add fingerprints to make them sync-eligible
    fp_vec1 = np.array([0.1, 0.2, 0.3])
    fp_vec2 = np.array([0.4, 0.5, 0.6])

    global_registry.register_fingerprint(
        model_id=str(global_model_id1),
        fingerprint_type="input_output",
        fingerprint_vector=fp_vec1,
        fingerprint_config={},
    )
    global_registry.register_fingerprint(
        model_id=str(global_model_id2),
        fingerprint_type="input_output",
        fingerprint_vector=fp_vec2,
        fingerprint_config={},
    )

    # Sync models
    result = local_registry.sync_models_from_global(use_last_sync_time=False)
    assert result is not None
    success_count, processed_count = result
    assert success_count == 2  # Should sync both models
    assert processed_count == 2

    # Check that canonical IDs were properly set
    local_models = local_registry.find_models()
    canonical_ids = {
        model.model_info["canonical_id"]
        for model in local_models
        if model.model_info["canonical_id"]
    }

    expected_canonical_id1 = f"{model_dict1['model_name']}_{global_model_id1}"
    expected_canonical_id2 = f"{model_dict2['model_name']}_{global_model_id2}"

    assert expected_canonical_id1 in canonical_ids
    assert expected_canonical_id2 in canonical_ids
