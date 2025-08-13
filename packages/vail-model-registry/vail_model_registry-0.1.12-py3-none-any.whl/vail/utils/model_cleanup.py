"""
Model cleanup utilities for tests and model management.

This module provides functions to properly clean up loaded models and cache directories
to prevent accumulation of large files and memory usage.
"""

import gc
import os
import shutil
from typing import Any

import torch


def cleanup_model_instance(model: Any) -> None:
    """
    Clean up a specific model instance by clearing loaded models and tokenizers.

    Args:
        model: Model instance to clean up (should have loaded_model and loaded_tokenizer attributes)
    """
    if hasattr(model, "loaded_model") and model.loaded_model is not None:
        # Delete model attributes directly
        model.loaded_model = None
        model.loaded_tokenizer = None

        # Clear GPU cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def cleanup_cache_directories(verbose: bool = True) -> None:
    """
    Clean up HuggingFace and model cache directories.

    Args:
        verbose: Whether to print cleanup messages
    """
    if verbose:
        print("🧹 Cleaning up cache directories...")

    cache_dirs = [
        ("~/.cache/huggingface/hub", "Hugging Face hub cache"),
        ("./.hf_cache", "local HF cache"),
        ("./.hf_offload_cache", "HF offload cache"),
    ]

    for cache_dir, description in cache_dirs:
        try:
            expanded_dir = os.path.expanduser(cache_dir)
            if os.path.exists(expanded_dir):
                if verbose:
                    print(f"   Removing {description} directory: {expanded_dir}")
                shutil.rmtree(expanded_dir, ignore_errors=True)
        except Exception as e:
            if verbose:
                print(f"   Warning: Error clearing {description}: {e}")
                raise e


def full_model_cleanup(*models: Any, verbose: bool = True) -> None:
    """
    Perform comprehensive cleanup of models and cache directories.

    Args:
        *models: Variable number of model instances to clean up
        verbose: Whether to print cleanup messages
    """
    if verbose:
        print("\n🧹 Cleaning up models and cache...")

    # Clean up individual model instances
    for model in models:
        cleanup_model_instance(model)

    # Force garbage collection
    gc.collect()

    # Clean up cache directories
    cleanup_cache_directories(verbose=verbose)

    if verbose:
        print("✅ Cleanup completed!")
