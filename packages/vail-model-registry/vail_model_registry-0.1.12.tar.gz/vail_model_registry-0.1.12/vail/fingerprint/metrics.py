"""
Unified Similarity Metrics

This module provides implementations of various similarity metrics for
comparing fingerprints.
"""

from typing import Callable, Dict, List

import numpy as np
from scipy.spatial.distance import jensenshannon


class UnifiedSimilarityMetric:
    """Base class for all similarity metrics."""

    def __init__(self, metric_name: str, metric_func: Callable):
        """
        Initialize the similarity metric.

        Args:
            metric_name: Name of the metric
            metric_func: Function to compute similarity
        """
        self.metric_name = metric_name
        self.metric_func = metric_func

    def compute(self, fp1: np.ndarray, fp2: np.ndarray) -> float:
        """
        Compute similarity between two fingerprints.

        Args:
            fp1: First fingerprint
            fp2: Second fingerprint

        Returns:
            Similarity score (between 0 and 1)
        """
        return self.metric_func(fp1, fp2)


# Similarity metric implementations


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity (between -1 and 1 if both vectors are real, between
        0 and 1 if one or both vectors are complex)
    """
    # Handle complex vectors
    if np.iscomplexobj(vec1) or np.iscomplexobj(vec2):
        return complex_cosine_similarity(vec1, vec2)

    # Reshape vectors to ensure they're 1D
    vec1 = np.array(vec1, dtype=np.float64).flatten()
    vec2 = np.array(vec2, dtype=np.float64).flatten()

    # Calculate dot product and norms
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    # Compute similarity
    similarity = dot_product / (norm1 * norm2 + 1e-12)

    return similarity


def complex_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two complex vectors.

    Args:
        vec1: First vector (possibly complex)
        vec2: Second vector (possibly complex)

    Returns:
        Cosine similarity (between 0 and 1)
    """
    # Reshape vectors to ensure they're 1D
    vec1 = vec1.flatten()
    vec2 = vec2.flatten()

    # Calculate hermitian dot product
    dot_product = np.vdot(vec1, vec2)

    # Calculate norms
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    # Compute similarity (magnitude of complex result)
    similarity = np.abs(dot_product) / (norm1 * norm2)

    return similarity


def l1_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate similarity based on L1 distance between two vectors.
    For complex vectors, sorts by magnitude but compares the raw values.

    Args:
        vec1: First vector (possibly complex)
        vec2: Second vector (possibly complex)

    Returns:
        Similarity measure (1 - normalized distance)
    """
    # Flatten vectors
    vec1 = vec1.flatten()
    vec2 = vec2.flatten()

    # Get magnitudes for sorting
    vec1_mag = np.abs(vec1)
    vec2_mag = np.abs(vec2)

    # Sort vectors by magnitude but keep original values
    idx1 = np.argsort(vec1_mag)
    idx2 = np.argsort(vec2_mag)

    vec1_sorted = vec1[idx1]
    vec2_sorted = vec2[idx2]

    # Calculate L1 distance directly (works for both real and complex vectors)
    distance = np.sum(np.abs(vec1_sorted - vec2_sorted))

    # Normalize by the sum of magnitudes
    max_possible_distance = np.sum(vec1_mag) + np.sum(vec2_mag)

    # Convert to similarity (1 - normalized distance)
    similarity = 1 - (distance / max_possible_distance)

    return similarity


def js_divergence_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate similarity based on Jensen-Shannon divergence between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Similarity measure (1 - JS divergence)
    """
    # Flatten vectors
    vec1 = vec1.flatten()
    vec2 = vec2.flatten()

    # Ensure vectors are non-negative (for probability interpretation)
    vec1_pos = np.abs(vec1)
    vec2_pos = np.abs(vec2)

    # Normalize vectors to sum to 1 (to be treated as probability distributions)
    sum1 = np.sum(vec1_pos)
    sum2 = np.sum(vec2_pos)

    vec1_norm = vec1_pos / sum1
    vec2_norm = vec2_pos / sum2

    # Calculate JS divergence
    js_div = jensenshannon(vec1_norm, vec2_norm)

    # Convert to similarity (1 - JS divergence)
    similarity = 1 - js_div

    return similarity


def complex_euclidean_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate similarity based on Euclidean distance between two complex vectors.

    Args:
        vec1: First vector (possibly complex)
        vec2: Second vector (possibly complex)

    Returns:
        Similarity measure (1 - normalized distance)
    """
    # Flatten vectors
    vec1 = vec1.flatten()
    vec2 = vec2.flatten()

    # Calculate Euclidean distance in the complex plane
    # For complex vectors, this is sqrt(sum(|a_i - b_i|^2))
    distance = np.sqrt(np.sum(np.abs(vec1 - vec2) ** 2))

    # Normalize by the maximum possible distance
    # A conservative upper bound is the sum of the norms
    max_possible_distance = np.linalg.norm(vec1) + np.linalg.norm(vec2)

    # Convert to similarity (1 - normalized distance)
    similarity = 1 - (distance / max_possible_distance)

    return similarity


def correlation_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate similarity based on Pearson correlation coefficient between two vectors.
    For complex vectors, calculates correlation separately for real and imaginary parts
    and combines them.

    Args:
        vec1: First vector (possibly complex)
        vec2: Second vector (possibly complex)

    Returns:
        Similarity measure based on correlation coefficient (ranges from -1 to 1)
    """
    # Flatten vectors
    vec1 = vec1.flatten()
    vec2 = vec2.flatten()

    # For complex vectors, handle real and imaginary parts separately
    if np.iscomplexobj(vec1) or np.iscomplexobj(vec2):
        # Calculate correlation for real parts
        real_corr = np.corrcoef(np.real(vec1), np.real(vec2))[0, 1]

        # Calculate correlation for imaginary parts
        imag_corr = np.corrcoef(np.imag(vec1), np.imag(vec2))[0, 1]

        # Handle NaN values (can occur if one part is constant)
        if np.isnan(real_corr):
            real_corr = 0.0
        if np.isnan(imag_corr):
            imag_corr = 0.0

        # Combine correlations (weighted by the variance in each part)
        real_var = np.var(np.real(vec1)) + np.var(np.real(vec2))
        imag_var = np.var(np.imag(vec1)) + np.var(np.imag(vec2))
        total_var = real_var + imag_var

        # Weight by variance
        if total_var == 0:
            combined_corr = 0.0
        else:
            combined_corr = (real_corr * real_var + imag_corr * imag_var) / total_var
    else:
        # For real vectors, calculate correlation directly
        combined_corr = np.corrcoef(vec1, vec2)[0, 1]

        # Handle NaN values
        if np.isnan(combined_corr):
            combined_corr = 0.0

    return combined_corr


def wasserstein_distance_similarity(vec1, vec2):
    """
    Calculate similarity based on the actual Wasserstein distance (Earth Mover's Distance)
    between two vectors interpreted as distributions.

    Parameters:
        vec1: First vector (possibly complex)
        vec2: Second vector (possibly complex)

    Returns:
        similarity: Similarity measure (1 - normalized distance)
    """
    # For complex vectors, we need to work with magnitudes
    vec1_mag = np.abs(vec1)
    vec2_mag = np.abs(vec2)

    # Normalize vectors to create proper probability distributions
    vec1_norm = vec1_mag / np.sum(vec1_mag)
    vec2_norm = vec2_mag / np.sum(vec2_mag)

    # Create points for the distributions (using indices as positions)
    positions = np.arange(len(vec1_norm))  # noqa: F841

    # Calculate the Wasserstein distance (EMD)
    # This is the minimum "work" needed to transform one distribution into another
    # where work is defined as the amount of distribution weight moved times the distance

    # First, compute the cumulative distribution functions
    cdf1 = np.cumsum(vec1_norm)
    cdf2 = np.cumsum(vec2_norm)

    # The 1D Wasserstein distance is the L1 norm of the difference between CDFs
    wasserstein_dist = np.sum(np.abs(cdf1 - cdf2))

    # Normalize by the maximum possible distance
    # In 1D, the maximum Wasserstein distance is bounded by the range of the support
    max_possible_distance = len(vec1_norm) - 1  # Maximum distance in the discrete case

    # Convert to similarity (1 - normalized distance)
    normalized_dist = wasserstein_dist / max_possible_distance
    similarity = 1 - normalized_dist

    return similarity


# Factory function to get a similarity metric


def get_similarity_metric(metric_name: str) -> UnifiedSimilarityMetric:
    """
    Get a similarity metric by name.

    Args:
        metric_name: Name of the metric

    Returns:
        Similarity metric instance
    """
    metrics = {
        "cosine": UnifiedSimilarityMetric("cosine", cosine_similarity),
        "complex_cosine": UnifiedSimilarityMetric(
            "complex_cosine", complex_cosine_similarity
        ),
        "l1": UnifiedSimilarityMetric("l1", l1_similarity),
        "js_divergence": UnifiedSimilarityMetric(
            "js_divergence", js_divergence_similarity
        ),
        "euclidean": UnifiedSimilarityMetric("euclidean", complex_euclidean_similarity),
        "correlation": UnifiedSimilarityMetric("correlation", correlation_similarity),
        "wasserstein": UnifiedSimilarityMetric(
            "wasserstein", wasserstein_distance_similarity
        ),
    }

    if metric_name not in metrics:
        raise ValueError(f"Unknown similarity metric: {metric_name}")

    return metrics[metric_name]


def compute_similarity_matrices(fingerprints: Dict, metrics: List[str]) -> Dict:
    """
    Compute similarity matrices for the specified fingerprints using the specified metrics.

    Args:
        fingerprints: Dictionary of fingerprints
        metrics: List of similarity metric names

    Returns:
        Dictionary of similarity matrices
    """
    similarity_matrices = {}

    model_ids = list(fingerprints.keys())
    method_types = list(fingerprints[model_ids[0]].keys()) if model_ids else []

    for method_type in method_types:
        similarity_matrices[method_type] = {}

        for metric_name in metrics:
            # Get similarity metric
            similarity_metric = get_similarity_metric(metric_name)

            # Initialize similarity matrix
            n_models = len(model_ids)
            matrix = np.zeros((n_models, n_models))

            # Compute similarities
            for i, model1 in enumerate(model_ids):
                for j, model2 in enumerate(model_ids):
                    fp1 = fingerprints[model1][method_type]["data"]
                    fp2 = fingerprints[model2][method_type]["data"]

                    # Calculate similarity
                    similarity = similarity_metric.compute(fp1, fp2)
                    matrix[i, j] = similarity

            # Store similarity matrix
            similarity_matrices[method_type][metric_name] = {
                "matrix": matrix,
                "models": model_ids,
            }

    return similarity_matrices
