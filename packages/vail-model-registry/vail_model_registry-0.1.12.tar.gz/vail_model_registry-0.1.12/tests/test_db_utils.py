"""
Test Database Utilities

This script tests the database utilities for copying models and fingerprints
between dev and production databases, and for checking database integrity.

Usage:
  python test_db_utils.py
"""

import os
import sys
from typing import List, Optional

from vail.registry import RegistryInterface
from vail.utils import setup_logging
from vail.utils.env import load_env

# Set up logging
logger = setup_logging(log_file_name="test_db_utils.log")

# Load test environment variables
load_env("test")

# Ensure the test database schema is set up once for all tests in this file
db_url_for_setup = os.getenv("DATABASE_URL")
if db_url_for_setup and "test" in db_url_for_setup:
    RegistryInterface.setup_global_registry(db_url_for_setup)
else:
    logger.warning("DATABASE_URL not configured for test setup or does not contain 'test'. Skipping global registry setup for test_db_utils.py.")


def run_command(command: str) -> None:
    """Run a command with db_utils.py"""
    print(f"\n====== Running: {command} ======")
    exit_code = os.system(command)
    if exit_code != 0:
        logger.error(f"Command failed with exit code {exit_code}: {command}")
        print(f"Command failed with exit code {exit_code}")
    else:
        print("Command completed successfully")


def get_model_ids(registry: RegistryInterface, limit: int = 3) -> List[str]:
    """Get a list of model IDs from the dev database"""
    with registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id FROM {registry.schema}.models 
                ORDER BY id 
                LIMIT {limit}
            """)
            return [str(row[0]) for row in cur.fetchall()]


def get_model_fingerprint_types(
    registry: RegistryInterface, model_id: str
) -> List[str]:
    """Get a list of fingerprint types for a specific model"""
    with registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT DISTINCT fingerprint_type 
                FROM {registry.schema}.fingerprints 
                WHERE model_id = %s
            """,
                (model_id,),
            )
            return [row[0] for row in cur.fetchall()]


def copy_model_to_prod(
    db_connection: str, model_id: str, override_checks: bool = False
) -> Optional[str]:
    """Copy a model from dev to prod"""
    print(f"\n====== Copying model {model_id} to prod ======")

    # Create registry interfaces
    dev_registry = RegistryInterface(db_connection, use_production=False)

    # Copy model
    prod_model_id = dev_registry.copy_model_to_production(
        model_id, override_checks=override_checks
    )

    if prod_model_id:
        print(f"Model copied successfully. Prod model ID: {prod_model_id}")
    else:
        print(f"Failed to copy model {model_id} to production")

    return prod_model_id


def delete_model_from_prod(db_connection: str, model_id: str) -> None:
    """Delete a model from the production database"""
    print(f"\n====== Deleting model {model_id} from prod ======")

    # Create prod registry interface
    prod_registry = RegistryInterface(db_connection, use_production=True)

    # Delete model
    prod_registry.remove_model(model_id)
    print(f"Model {model_id} deleted from production")


def copy_fingerprint_to_prod(
    db_connection: str,
    dev_model_id: str,
    prod_model_id: str,
    fingerprint_type: str,
    override_checks: bool = False,
) -> Optional[str]:
    """Copy a fingerprint from dev to prod"""
    print(
        f"\n====== Copying fingerprint {fingerprint_type} for dev model {dev_model_id} to prod ======"
    )

    # Create registry interfaces
    dev_registry = RegistryInterface(db_connection, use_production=False)

    # Copy fingerprint
    fingerprint_id = dev_registry.copy_fingerprint_to_production(
        model_id=dev_model_id,
        prod_model_id=prod_model_id,
        fingerprint_type=fingerprint_type,
        override_checks=override_checks,
    )

    if fingerprint_id:
        print(f"Fingerprint copied successfully. Prod fingerprint ID: {fingerprint_id}")
    else:
        print(
            f"Failed to copy fingerprint {fingerprint_type} for model {dev_model_id} to production"
        )

    return fingerprint_id


def delete_fingerprint_from_prod(
    db_connection: str, model_id: str, fingerprint_type: str
) -> None:
    """Delete a fingerprint from the production database"""
    print(
        f"\n====== Deleting fingerprint {fingerprint_type} for model {model_id} from prod ======"
    )

    # Create prod registry interface
    prod_registry = RegistryInterface(db_connection, use_production=True)

    # Delete fingerprint
    with prod_registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM prod.fingerprints 
                WHERE model_id = %s AND fingerprint_type = %s
            """,
                (model_id, fingerprint_type),
            )
            conn.commit()

    print(
        f"Fingerprint {fingerprint_type} for model {model_id} deleted from production"
    )


def check_duplicates(db_connection: str) -> None:
    """Check for duplicate fingerprints in prod"""
    print("\n====== Checking for duplicate fingerprints in prod ======")

    # Create prod registry interface
    prod_registry = RegistryInterface(db_connection, use_production=True)

    # Check for duplicates
    duplicates = prod_registry.check_duplicate_fingerprints_in_prod()

    if duplicates:
        print(f"Found {len(duplicates)} duplicate fingerprints:")
        for i, dup in enumerate(duplicates):
            print(f"  Duplicate {i + 1}: {dup}")
    else:
        print("No duplicate fingerprints found")


def check_multiples(db_connection: str) -> None:
    """Check for multiple fingerprints per model/type in prod"""
    print("\n====== Checking for multiple fingerprints per model/type in prod ======")

    # Create prod registry interface
    prod_registry = RegistryInterface(db_connection, use_production=True)

    # Check for multiples
    multiples = prod_registry.check_multiple_fingerprints_per_model_in_prod()

    if multiples:
        print(f"Found {len(multiples)} models with multiple fingerprints:")
        for i, multi in enumerate(multiples):
            print(f"  Multiple {i + 1}: {multi}")
    else:
        print("No models with multiple fingerprints found")


def create_duplicate_fingerprint(
    db_connection: str, prod_model_id: str, fingerprint_type: str
) -> Optional[int]:
    """Create a duplicate fingerprint in prod for testing

    Returns:
        The ID of the created duplicate fingerprint, or None if creation failed
    """
    print(
        f"\n====== Creating duplicate fingerprint for model {prod_model_id}, type {fingerprint_type} ======"
    )

    try:
        # Create registry interfaces
        dev_registry = RegistryInterface(db_connection, use_production=False)  # noqa: F841
        prod_registry = RegistryInterface(db_connection, use_production=True)

        # Force-register the same fingerprint again to create a duplicate
        with prod_registry._get_connection() as conn:
            with conn.cursor() as cur:
                # Create a duplicate entry with the same vector but a different ID
                cur.execute(
                    """
                    INSERT INTO prod.fingerprints 
                    (model_id, fingerprint_type, fingerprint_data, fingerprint_vector, fingerprint_config)
                    SELECT 
                        model_id, 
                        fingerprint_type, 
                        fingerprint_data, 
                        fingerprint_vector, 
                        fingerprint_config
                    FROM prod.fingerprints
                    WHERE model_id = %s AND fingerprint_type = %s
                    RETURNING id
                """,
                    (prod_model_id, fingerprint_type),
                )

                result = cur.fetchone()
                duplicate_id = result[0] if result else None

                if duplicate_id:
                    print(f"Created duplicate fingerprint with ID: {duplicate_id}")
                    conn.commit()
                    return duplicate_id
                else:
                    print("Failed to create duplicate fingerprint")
                    return None
    except Exception as e:
        logger.error(f"Error creating duplicate fingerprint: {e}")
        print(f"Error creating duplicate fingerprint: {e}")
        return None


def get_safe_model_ids(db_connection: str, limit: int = 3) -> List[str]:
    """
    Get a list of model IDs from the dev database that don't have matching model_name values in prod,
    to safely run tests without risking conflicts with pre-existing prod data.
    """
    dev_registry = RegistryInterface(db_connection, use_production=False)
    prod_registry = RegistryInterface(db_connection, use_production=True)

    # Get models from dev with their names
    with dev_registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, model_name FROM dev.models 
                ORDER BY id
            """)
            dev_models = [
                (str(row[0]), row[1].lower() if row[1] else None)
                for row in cur.fetchall()
            ]

    # Get model names from prod (convert to lowercase for case-insensitive comparison)
    with prod_registry._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT LOWER(model_name) FROM prod.models
                WHERE model_name IS NOT NULL
            """)
            prod_model_names = [row[0] for row in cur.fetchall()]

    # Find models that exist in dev but don't have matching names in prod
    safe_models = []
    for model_id, model_name in dev_models:
        # Skip models with no name
        if not model_name:
            continue

        # Keep models whose names don't exist in prod
        if model_name not in prod_model_names:
            safe_models.append(model_id)

    if not safe_models:
        print(
            "WARNING: No safe models found that exist in dev but not in prod (by model_name)."
        )
        return []

    print(
        f"Found {len(safe_models)} models in dev that have unique model_name values not present in prod"
    )
    return safe_models[:limit]


def run_tests(db_connection: str) -> None:
    """Run all tests"""
    # Variables to track created resources that need cleanup
    resources_to_cleanup = {
        "prod_model_ids": [],
        "duplicate_fingerprints": [],  # Track fingerprints that were deliberately created as duplicates
    }

    try:
        # Create registry interfaces
        dev_registry = RegistryInterface(db_connection, use_production=False)
        prod_registry = RegistryInterface(db_connection, use_production=True)

        # Get some model IDs that are safe to test with (exist in dev but not in prod)
        dev_model_ids = get_safe_model_ids(db_connection, limit=1)
        if not dev_model_ids:
            print(
                "No safe models found for testing (models must exist in dev but not in prod). Exiting."
            )
            return

        print(f"Found safe models for testing: {dev_model_ids}")

        # Get fingerprint types for the first model
        dev_model_id = dev_model_ids[0]
        fingerprint_types = get_model_fingerprint_types(dev_registry, dev_model_id)
        if not fingerprint_types:
            print(
                f"No fingerprints found for model {dev_model_id} in dev database. Exiting."
            )
            return

        print(f"Found fingerprint types for model {dev_model_id}: {fingerprint_types}")

        # === Test copying a model that isn't already in prod ===
        print("\n\n======== TEST 1: Copy a model not in prod ========")
        prod_model_id = copy_model_to_prod(db_connection, dev_model_id)
        if prod_model_id:
            resources_to_cleanup["prod_model_ids"].append(prod_model_id)

        # === Test copying a fingerprint that isn't already in prod ===
        if prod_model_id and fingerprint_types:
            print("\n\n======== TEST 2: Copy a fingerprint not in prod ========")
            fingerprint_id = copy_fingerprint_to_prod(  # noqa: F841
                db_connection, dev_model_id, prod_model_id, fingerprint_types[0]
            )

        # === Test copying a model that is already in prod (should fail) ===
        if prod_model_id:
            print(
                "\n\n======== TEST 3: Copy a model already in prod (should fail) ========"
            )
            failed_copy = copy_model_to_prod(db_connection, dev_model_id)
            if failed_copy:
                # This shouldn't happen, but track it for cleanup just in case
                resources_to_cleanup["prod_model_ids"].append(failed_copy)
                print("Test failed: Model was copied again when it should have failed")
            else:
                print("Test passed: Model copy correctly failed for duplicate model")

        # === Test copying a fingerprint that is already in prod (should fail) ===
        if prod_model_id and fingerprint_types:
            print(
                "\n\n======== TEST 4: Copy a fingerprint already in prod (should fail) ========"
            )
            failed_copy = copy_fingerprint_to_prod(
                db_connection, dev_model_id, prod_model_id, fingerprint_types[0]
            )
            if not failed_copy:
                print(
                    "Test passed: Fingerprint copy correctly failed for duplicate fingerprint"
                )
            else:
                print(
                    "Test failed: Fingerprint was copied again when it should have failed"
                )

        # === Test overriding checks when copying model and fingerprint ===
        if prod_model_id and fingerprint_types:
            print(
                "\n\n======== TEST 5: Override checks when copying (should succeed) ========"
            )
            override_copy = copy_model_to_prod(
                db_connection, dev_model_id, override_checks=True
            )
            if override_copy:
                resources_to_cleanup["prod_model_ids"].append(override_copy)
                print("Test passed: Model was copied with override_checks=True")

                override_fp_copy = copy_fingerprint_to_prod(
                    db_connection,
                    dev_model_id,
                    override_copy,
                    fingerprint_types[0],
                    override_checks=True,
                )
                if override_fp_copy:
                    print(
                        "Test passed: Fingerprint was copied with override_checks=True"
                    )
                else:
                    print(
                        "Test failed: Fingerprint copy failed even with override_checks=True"
                    )
            else:
                print("Test failed: Model copy failed even with override_checks=True")

        # === Create duplicate fingerprints for testing ===
        if prod_model_id and fingerprint_types:
            print(
                "\n\n======== TEST 6: Creating duplicate fingerprints for testing ========"
            )
            # This deliberately creates a duplicate fingerprint that should be detected in TEST 7
            with prod_registry._get_connection() as conn:
                with conn.cursor() as cur:
                    # Track existing fingerprint IDs before creating duplicates
                    cur.execute(
                        """
                        SELECT id FROM prod.fingerprints
                        WHERE model_id = %s AND fingerprint_type = %s
                    """,
                        (prod_model_id, fingerprint_types[0]),
                    )

                    existing_ids = [row[0] for row in cur.fetchall()]

            create_duplicate_fingerprint(
                db_connection, prod_model_id, fingerprint_types[0]
            )

            # Find the newly created duplicate fingerprint ID
            with prod_registry._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id FROM prod.fingerprints
                        WHERE model_id = %s AND fingerprint_type = %s
                        AND id NOT IN %s
                    """,
                        (prod_model_id, fingerprint_types[0], tuple(existing_ids)),
                    )

                    new_ids = [row[0] for row in cur.fetchall()]
                    resources_to_cleanup["duplicate_fingerprints"].extend(
                        [
                            (prod_model_id, fingerprint_types[0], fingerprint_id)
                            for fingerprint_id in new_ids
                        ]
                    )

        # === Run duplicate and multiple fingerprint checks ===
        print(
            "\n\n======== TEST 7: Check for duplicate and multiple fingerprints ========"
        )
        # These checks should find the duplicate fingerprint created in TEST 6
        check_duplicates(db_connection)
        check_multiples(db_connection)

        print("\n\nAll tests completed successfully.")

    except Exception as e:
        logger.error(f"Error during tests: {e}")
        print(f"ERROR during tests: {e}")
        raise
    finally:
        # Clean up all resources created during tests
        print("\n\n======== Cleaning up test data ========")

        # Clean up duplicate fingerprints first
        prod_registry = RegistryInterface(db_connection, use_production=True)

        # Clean up models (this will cascade delete associated fingerprints)
        for prod_model_id in resources_to_cleanup.get("prod_model_ids", []):
            print(f"Cleaning up model {prod_model_id}")
            delete_model_from_prod(db_connection, prod_model_id)


if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    try:
        run_tests(database_url)
        print("\n\nAll tests completed successfully.")
    except Exception as e:
        logger.error(f"Error during tests: {e}")
        print(f"\n\nTests FAILED with error: {e}")
        sys.exit(1)
