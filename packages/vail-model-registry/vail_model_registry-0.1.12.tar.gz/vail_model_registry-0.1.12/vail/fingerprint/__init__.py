"""
Unified Fingerprinting Framework

This package provides a unified framework for fingerprinting machine learning models.
"""

# Registry interface
from vail.registry import RegistryInterface

# ONNX utils
from vail.utils import load_onnx_model

# Metrics analysis
from .analysis import MetricsAnalyzer, ModelInfo, ModelPairInfo, SimilarityStats

# Fingerprinting methods
from .methods import (
    ArchitectureFingerprintingMethod,
    InputOutputFingerprintingMethod,
    UnifiedFingerprintingMethod,
    WeightFingerprintingMethod,
    get_fingerprinting_method,
)

# Similarity metrics
from .metrics import (
    UnifiedSimilarityMetric,
    compute_similarity_matrices,
    get_similarity_metric,
)

__all__ = [
    "load_onnx_model",
    "compute_similarity_matrices",
    "RegistryInterface",
    "ArchitectureFingerprintingMethod",
    "InputOutputFingerprintingMethod",
    "UnifiedFingerprintingMethod",
    "WeightFingerprintingMethod",
    "get_fingerprinting_method",
    "UnifiedSimilarityMetric",
    "get_similarity_metric",
    "MetricsAnalyzer",
    "ModelInfo",
    "ModelPairInfo",
    "SimilarityStats",
]
