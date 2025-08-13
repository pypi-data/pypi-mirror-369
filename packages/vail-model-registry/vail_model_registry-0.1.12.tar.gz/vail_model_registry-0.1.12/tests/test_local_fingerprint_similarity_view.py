import os

import pytest

from vail.registry.local_interface import LocalRegistryInterface


@pytest.fixture
def temp_local_registry():
    """Fixture to create a temporary local registry for testing."""
    # Use a temporary file instead of :memory: to avoid potential issues
    db_path = "test_similarity_view.db"
    dummy_global_conn_str = "postgresql://user:pass@host:5432/dbname"

    # Clean up any existing test database
    if os.path.exists(db_path):
        os.remove(db_path)

    try:
        # Setup the local registry
        LocalRegistryInterface.setup_local_registry(db_path, dummy_global_conn_str)
        interface = LocalRegistryInterface(dummy_global_conn_str, local_db_path=db_path)

        # Add some mock data for testing
        with interface._get_local_connection() as conn:
            # Add Models
            conn.execute(
                "INSERT INTO models (id, model_name) VALUES (1, 'model-a'), (2, 'model-b'), (3, 'model-c'), (4, 'model-d');"
            )

            # Add Fingerprints
            fp1 = [1.0, 2.0, 3.0]  # Base fingerprint
            fp2 = [1.1, 2.1, 3.1]  # Similar to fp1
            fp3 = [10.0, 20.0, 30.0]  # Different from fp1, fp2
            fp4 = [1.0, 2.0, 3.0]  # Identical to fp1

            conn.execute(
                "INSERT INTO fingerprints (id, model_id, fingerprint_type, fingerprint_vector) VALUES (?, ?, ?, ?)",
                [1, 1, "io", fp1],
            )
            conn.execute(
                "INSERT INTO fingerprints (id, model_id, fingerprint_type, fingerprint_vector) VALUES (?, ?, ?, ?)",
                [2, 2, "io", fp2],
            )
            conn.execute(
                "INSERT INTO fingerprints (id, model_id, fingerprint_type, fingerprint_vector) VALUES (?, ?, ?, ?)",
                [3, 3, "io", fp3],
            )
            conn.execute(
                "INSERT INTO fingerprints (id, model_id, fingerprint_type, fingerprint_vector) VALUES (?, ?, ?, ?)",
                [4, 4, "io", fp4],
            )

            # Add a different fingerprint type for testing filtering
            conn.execute(
                "INSERT INTO fingerprints (id, model_id, fingerprint_type, fingerprint_vector) VALUES (?, ?, ?, ?)",
                [5, 1, "weights", fp1],
            )
            conn.execute(
                "INSERT INTO fingerprints (id, model_id, fingerprint_type, fingerprint_vector) VALUES (?, ?, ?, ?)",
                [6, 2, "weights", fp3],
            )

        yield interface

    finally:
        # Clean up the test database
        if os.path.exists(db_path):
            os.remove(db_path)


def test_similarity_view_creation(temp_local_registry):
    """Test that the fingerprint_similarities view is created and computes similarities."""
    with temp_local_registry._get_local_connection() as conn:
        # Test that the view exists and returns results
        result = conn.execute("SELECT * FROM fingerprint_similarities").fetchall()

        # We should have:
        # - 6 pairs for 'io' type: (1,2), (1,3), (1,4), (2,3), (2,4), (3,4)
        # - 1 pair for 'weights' type: (1,2)
        # Total: 7 pairs
        assert len(result) == 7

        # Test that all expected columns are present
        columns = [desc[0] for desc in conn.description]
        expected_columns = [
            "model_id_1",
            "model_id_2",
            "model_name_1",
            "model_name_2",
            "fingerprint_type",
            "cosine_similarity",
            "euclidean_similarity",
            "dot_product",
        ]
        for col in expected_columns:
            assert col in columns

        # Test specific similarity calculation (model 1 and 4 are identical)
        identical_pair = conn.execute(
            "SELECT * FROM fingerprint_similarities WHERE model_id_1=1 AND model_id_2=4 AND fingerprint_type='io'"
        ).fetchone()

        assert identical_pair is not None
        # Convert to dict for easier access
        row_dict = dict(zip(columns, identical_pair))

        # For identical vectors, cosine similarity should be 1.0
        assert abs(row_dict["cosine_similarity"] - 1.0) < 0.001
        # For identical vectors, euclidean similarity should be 1.0
        assert abs(row_dict["euclidean_similarity"] - 1.0) < 0.001


def test_get_similarities_method(temp_local_registry):
    """Test the get_similarities method."""
    # Test basic functionality - get similarities for a pair
    results = temp_local_registry.get_model_similarities(model_ids=[1, 2])
    assert len(results) == 2  # One for 'io' type, one for 'weights' type

    # Test with fingerprint_type filter
    results = temp_local_registry.get_model_similarities(
        model_ids=[1, 2], fingerprint_type="io"
    )
    assert len(results) == 1
    assert results[0]["model_id_1"] == 1
    assert results[0]["model_id_2"] == 2
    assert results[0]["fingerprint_type"] == "io"

    # Test with threshold filtering
    results = temp_local_registry.get_model_similarities(
        model_ids=[1, 2, 3, 4],
        fingerprint_type="io",
        threshold=0.95,
        similarity_metric="cosine_similarity",
    )
    # Should include pairs (1,2) and (1,4) - both with high cosine similarity
    # (1,4) should be 1.0 (identical), (1,2) should be high (similar)
    assert len(results) >= 1

    # Test error handling
    with pytest.raises(ValueError):
        temp_local_registry.get_model_similarities(model_ids=[1])  # Only one model ID


def test_find_similar_models_method(temp_local_registry):
    """Test the find_similar_models method."""
    # Find models similar to model 1 with high threshold
    results = temp_local_registry.find_similar_models(
        model_id=1,
        fingerprint_type="io",
        threshold=0.95,
        similarity_metric="cosine_similarity",
    )

    # Should find at least model 4 (identical) and possibly model 2 (similar)
    assert len(results) >= 1

    # Check that model 4 is in the results (identical to model 1)
    model_ids_found = set()
    for result in results:
        if result["model_id_1"] == 1:
            model_ids_found.add(result["model_id_2"])
        else:
            model_ids_found.add(result["model_id_1"])

    assert 4 in model_ids_found  # Model 4 should be found (identical to model 1)

    # Test with euclidean distance metric
    results = temp_local_registry.find_similar_models(
        model_id=1,
        fingerprint_type="io",
        threshold=0.1,  # Small distance threshold
        similarity_metric="euclidean_similarity",
    )

    # Should find model 4 (distance = 0) and possibly model 2 (small distance)
    assert len(results) >= 1

    # Test with no results
    results = temp_local_registry.find_similar_models(
        model_id=99,  # Non-existent model
        fingerprint_type="io",
    )
    assert len(results) == 0
