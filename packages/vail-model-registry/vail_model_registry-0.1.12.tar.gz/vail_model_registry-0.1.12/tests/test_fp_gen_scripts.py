"""
Test module for scripts/fp_gen functionality.

Minimal tests that verify script structure and CLI parsing.
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest


@pytest.fixture
def test_config():
    """Create a test configuration file. Content doesn't matter for these tests."""
    config = {"test": "data"}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        return f.name


class TestFingerprintRunner:
    """Test fingerprint_runner.py CLI functionality"""

    def test_script_exists_and_structure(self):
        """Test that fingerprint_runner.py exists and has expected CLI structure."""
        script_path = "scripts/fp_gen/fingerprint_runner.py"
        assert os.path.exists(script_path), f"Script {script_path} does not exist"

        with open(script_path, "r") as f:
            content = f.read()
            assert "def main()" in content
            assert "fingerprint_runner(" in content
            assert "--config" in content
            assert "--add-row" in content
            assert "--log-bucket" in content

    @patch("vail.fingerprint.runner.fingerprint_runner")
    def test_cli_argument_parsing(self, mock_runner, test_config):
        """Test that CLI arguments are parsed and passed correctly."""
        import sys

        test_args = [
            "fingerprint_runner.py",
            "--config",
            test_config,
            "--add-row",
            "--log-bucket",
            "test-bucket",
        ]

        with patch.object(sys, "argv", test_args):
            from scripts.fp_gen.fingerprint_runner import main

            main()

            mock_runner.assert_called_once_with(
                config_path=test_config, add_row=True, log_bucket="test-bucket"
            )

    def test_missing_required_config(self):
        """Test that missing required --config argument raises SystemExit."""
        import sys

        with patch.object(sys, "argv", ["fingerprint_runner.py"]):
            from scripts.fp_gen.fingerprint_runner import main

            with pytest.raises(SystemExit):
                main()


class TestScriptStructure:
    """Test that shell scripts exist and contain expected commands"""

    def test_run_fp_gcp_script_contains_expected_commands(self):
        """Test that run_fp_gcp.sh contains the expected GCP and storage commands."""
        script_path = "scripts/fp_gen/run_fp_gcp.sh"
        assert os.path.exists(script_path), f"Script {script_path} does not exist"

        with open(script_path, "r") as f:
            content = f.read()

        # Check for key bash setup and argument parsing
        assert "set -euo pipefail" in content
        assert "CONFIG_PATH=$1" in content
        assert "PROJECT_ID=$5" in content

        # Check for expected GCP commands
        assert "gcloud compute instances create-with-container" in content
        assert "gcloud compute instances delete" in content

        # Check for storage commands
        assert "gsutil mb" in content
        assert "gsutil cp" in content

        # Check for environment variable handling
        assert "DATABASE_URL" in content

    def test_build_push_fp_image_script_contains_expected_commands(self):
        """Test that build_push_fp_image.sh contains expected Docker and Cloud Build commands."""
        script_path = "scripts/fp_gen/build_push_fp_image.sh"
        assert os.path.exists(script_path), f"Script {script_path} does not exist"

        with open(script_path, "r") as f:
            content = f.read()

        # Check for key setup
        assert "set -euo pipefail" in content
        assert "PROJECT_ID=$1" in content

        # Check for Docker commands
        assert "docker build" in content
        assert "docker push" in content
        assert "vail/fingerprint/Dockerfile" in content

        # Check for Cloud Build alternative
        assert "gcloud builds submit" in content
        assert "REMOTE_BUILD" in content
