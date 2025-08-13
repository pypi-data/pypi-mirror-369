import io
import json
import logging
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from vail.fingerprint import get_fingerprinting_method
from vail.registry import Model, RegistryInterface
from vail.utils import setup_logging
from vail.utils.env import load_env

# google-cloud-storage is optional; import lazily to avoid mandatory dependency for local runs
try:
    from google.cloud import storage  # type: ignore
except ImportError:  # pragma: no cover
    storage = None  # type: ignore

__all__ = [
    "fingerprint_runner",
]


class _StreamToLogger(io.TextIOBase):
    """Redirects a standard IO stream to the logging system."""

    def __init__(self, level: int, logger: logging.Logger):
        super().__init__()
        self.level = level
        self.logger = logger

    def write(self, buf: str) -> int:  # type: ignore[override]
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())
        return len(buf)

    def flush(self):  # noqa: D401 – standard IO interface
        pass


def _redirect_streams(logger: logging.Logger) -> None:
    """Send stdout / stderr to *both* console & file via logger."""

    sys.stdout = _StreamToLogger(logging.INFO, logger)  # type: ignore[assignment]
    sys.stderr = _StreamToLogger(logging.ERROR, logger)  # type: ignore[assignment]


def _download_gcs_file(uri: str) -> Path:
    """Download a file from GS URI to a temporary location and return path."""

    if not uri.startswith("gs://"):
        raise ValueError("Expected a gs:// URI")
    if storage is None:
        raise RuntimeError(
            "google-cloud-storage is required for gs:// URIs but is not installed."
        )

    client = storage.Client()
    bucket_name, *blob_parts = uri[5:].split("/", 1)
    blob_path = blob_parts[0] if blob_parts else ""
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    fd, tmp_path = tempfile.mkstemp()
    os.close(fd)
    blob.download_to_filename(tmp_path)
    return Path(tmp_path)


def fingerprint_runner(
    config_path: str,
    add_row: bool = False,
    log_bucket: Optional[str] = None,
) -> None:
    """Core fingerprint generation workflow.

    Parameters
    ----------
    config_path
        Local path or ``gs://`` URI pointing to the JSON configuration file
        (same shape as existing *run_experiment* configs).
    add_row
        If True, generate and insert a *new* fingerprint row even when a
        fingerprint of the same type already exists for the model.
    log_bucket
        Optional GCS bucket to which the complete log file will be uploaded at
        the end of the run.  It will be placed under ``logs/`` with a
        timestamped filename.
    """

    # NOTE: In GCP runs, DATABASE_URL is injected directly via the container environment (see run_fp_gcp.sh),
    # so load_env() is not needed there. It is only necessary for local runs where .env is present.
    # Load env file (if any)
    load_env()

    # Handle remote config file
    if config_path.startswith("gs://"):
        tmp_path = _download_gcs_file(config_path)
        config_path = str(tmp_path)

    # Timestamp for file naming
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    # Initialise logging (sends to console & file)
    logger = setup_logging(f"fp_run_{ts}.log")
    _redirect_streams(logger)

    logger.info("VAIL Fingerprint Runner started")
    logger.debug(f"Config path: {config_path}")

    # Parse configuration
    with open(config_path, "r", encoding="utf-8") as fp:
        cfg = json.load(fp)

    models = cfg["models"]
    methods = cfg["methods"]
    method_args = cfg.get("method_args", {})

    # Registry connection from environment (.env)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error(
            "DATABASE_URL is not set. Ensure it is provided in the .env file or as an env var."
        )
        raise RuntimeError("DATABASE_URL missing")

    registry = RegistryInterface(connection_string=db_url)

    for model_id in models:
        for method_type in methods:
            try:
                if not add_row and registry.get_fingerprint(model_id, method_type):
                    logger.info(
                        f"Skipping existing fingerprint – model={model_id}, method={method_type}"
                    )
                    continue

                # Instantiate method
                fp_kwargs = method_args.get(method_type, {})
                fingerprint_method = get_fingerprinting_method(method_type, **fp_kwargs)

                logger.info(
                    f"Generating {method_type} fingerprint for model {model_id}"
                )

                # Build a Model object similarly to scripts/run_experiment.py
                try:
                    model_loader_info = registry.get_model_loader_info(model_id)
                except Exception as e:  # noqa: BLE001
                    logger.exception(
                        f"Could not fetch loader info for model {model_id}: {e}"
                    )
                    continue

                model_obj = Model(name=model_id, model_info=model_loader_info)  # type: ignore[arg-type]

                fingerprint_vector = fingerprint_method.generate_fingerprint(model_obj)

                registry.register_fingerprint(
                    model_id=model_id,
                    fingerprint_type=method_type,
                    fingerprint_vector=fingerprint_vector,
                    fingerprint_config=fingerprint_method.get_config(),
                )
                logger.info(
                    f"Stored {method_type} fingerprint for model {model_id} in registry"
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    f"Failed generating fingerprint – model={model_id}, method={method_type}: {exc}"
                )

    logger.info("Fingerprint run complete.")

    # Upload logs to GCS, if requested
    if log_bucket:
        if storage is None:
            logger.warning("google-cloud-storage not installed; skipping log upload")
        else:
            try:
                client = storage.Client()
                bucket = client.bucket(log_bucket)
                log_file = Path(logger.handlers[0].baseFilename)
                blob = bucket.blob(f"logs/{log_file.name}")
                blob.upload_from_filename(str(log_file))
                logger.info(f"Uploaded log to gs://{log_bucket}/logs/{log_file.name}")
            except Exception:  # noqa: BLE001
                logger.exception("Failed to upload log file to GCS")

    # Function intentionally returns None
