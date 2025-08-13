"""
MCP Server package initialization.
"""

from .server import (
    add_model,
    compare_fp_pairs,
    compute_fingerprint_similarity,
    find_similar_models,
    generate_fingerprint,
    get_fingerprint_vectors,
    get_hardware_profile,
    get_model_template,
    get_similarity_matrix,
    list_models,
    mcp_server,
)

__all__ = [
    "add_model",
    "compare_fp_pairs",
    "compute_fingerprint_similarity",
    "find_similar_models",
    "generate_fingerprint",
    "get_fingerprint_vectors",
    "get_hardware_profile",
    "get_model_template",
    "get_similarity_matrix",
    "list_models",
    "mcp_server",
]
