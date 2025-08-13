import hashlib
import os.path
from collections import defaultdict
from typing import BinaryIO, Dict, Union

import networkx as nx
import numpy as np
import onnx
from onnx import numpy_helper

#####################################################################
# Load and extract ONNX metadata
#####################################################################


def load_onnx_model(onnx_model: Union[str, bytes, BinaryIO]) -> onnx.ModelProto:
    """Load an ONNX model from various input types."""
    if isinstance(onnx_model, str) and os.path.isfile(onnx_model):
        return onnx.load(onnx_model)
    elif isinstance(onnx_model, bytes):
        return onnx.load_model_from_string(onnx_model)
    elif hasattr(onnx_model, "read"):
        if hasattr(onnx_model, "seek"):
            onnx_model.seek(0)
        model_bytes = onnx_model.read()
        return onnx.load_model_from_string(model_bytes)
    else:
        raise ValueError("onnx_model must be a file path, bytes, or file-like object")


def extract_onnx_metadata(model: onnx.ModelProto) -> Dict:
    """Extract metadata from an ONNX model."""
    graph = model.graph
    metadata = {
        "architecture_type": "onnx",
        "producer": model.producer_name
        if hasattr(model, "producer_name")
        else "unknown",
        "model_version": str(model.model_version)
        if hasattr(model, "model_version")
        else "unknown",
        "opset_version": str([opset.version for opset in model.opset_import]),
        "num_nodes": len(graph.node),
        "num_inputs": len(graph.input),
        "num_outputs": len(graph.output),
    }

    # Make a rough estimate of parameter count
    param_count = 0
    for initializer in graph.initializer:
        try:
            tensor = onnx.numpy_helper.to_array(initializer)
            param_count += tensor.size
        except:  # noqa: E722
            pass

    metadata["params_count"] = param_count

    # Look for model family in the model/graph name
    if graph.name:
        parts = graph.name.split("-")
        if len(parts) > 1:
            metadata["model_family"] = parts[0].strip()

    return metadata


def get_tensor_value_info(model, tensor_name):
    """
    Get tensor value info from model initializers, inputs, or outputs.

    Args:
        model: ONNX model
        tensor_name: Name of the tensor to find

    Returns:
        Tensor value or None if not found
    """
    # Check initializers
    for initializer in model.graph.initializer:
        if initializer.name == tensor_name:
            return numpy_helper.to_array(initializer)

    # Check inputs
    for input_tensor in model.graph.input:
        if input_tensor.name == tensor_name:
            return f"Input tensor: {input_tensor.name} (shape info: {input_tensor.type.tensor_type.shape})"

    # Check outputs
    for output_tensor in model.graph.output:
        if output_tensor.name == tensor_name:
            return f"Output tensor: {output_tensor.name} (shape info: {output_tensor.type.tensor_type.shape})"

    return None


#####################################################################
# Generate ONNX fingerprint
#####################################################################


def generate_onnx_fingerprint(model_or_path, size=50) -> np.ndarray:
    """
    Generate a fingerprint from an ONNX model using repeating subgraph analysis.

    Args:
        model_or_path: ONNX model or path to model file
        size: Size parameter for fingerprint matrix (default 50)

    Returns:
        np.ndarray: 2500-dimension fingerprint vector
    """
    try:
        # Find repeating subgraphs
        patterns, model, _, node_to_initializers = find_repeating_subgraphs(
            model_or_path
        )

        # Get weight matrices from subgraphs
        matrices = get_weight_matrices_from_subgraphs(
            model, patterns, node_to_initializers
        )

        # Fold matrices into a single tensor
        tensor_matrix_fingerprint = fold_matrices_from_subgraphs(matrices)

        # Process matrices to get fingerprint vector
        fingerprint_vector = get_top_singular_values_matrix(
            tensor_matrix_fingerprint, size=size, flatten=True
        )

        # Normalize the vector
        if np.any(fingerprint_vector):  # Check if not all zeros
            fingerprint_vector = fingerprint_vector / np.linalg.norm(fingerprint_vector)

        return fingerprint_vector

    except Exception as e:
        print(f"Error generating fingerprint: {e}")
        # Return a zero vector in case of error
        return np.zeros(size * size)


#####################################################################
# Subgraph analysis
#####################################################################


def build_graph_from_onnx(model_path):
    """
    Build a NetworkX graph from an ONNX model.

    Args:
        model_path: Path to the ONNX model file

    Returns:
        model: The loaded ONNX model
        G: NetworkX DiGraph representing the ONNX computation graph
        node_info: Dictionary mapping node names to their operation types
        output_map: Dictionary mapping node names to their output tensors
        node_to_initializers: Dictionary mapping node names to their initializer inputs
    """
    if isinstance(model_path, str):
        model = onnx.load(model_path)
    elif isinstance(model_path, onnx.ModelProto):
        model = model_path
    else:
        raise ValueError("model_path must be a string path or an ONNX ModelProto")
    G = nx.DiGraph()

    # Create a mapping of initializer names
    initializer_names = {init.name for init in model.graph.initializer}

    # Map input/output names to their producing/consuming nodes
    output_to_node = {}
    output_map = {}
    node_to_initializers = {}

    for node in model.graph.node:
        for output in node.output:
            output_to_node[output] = node.name
            output_map[node.name] = node.output

        # Track which initializers are used by this node
        initializer_inputs = [
            input_name for input_name in node.input if input_name in initializer_names
        ]
        if initializer_inputs:
            node_to_initializers[node.name] = initializer_inputs

    # Add nodes and edges to the graph
    node_info = {}
    for node in model.graph.node:
        G.add_node(node.name)
        node_info[node.name] = node.op_type

        # Add edges based on inputs
        for input_name in node.input:
            if input_name in output_to_node:
                G.add_edge(output_to_node[input_name], node.name)

    return model, G, node_info, output_map, node_to_initializers


def get_node_signature(G, node_info, node_name, depth=2):
    """
    Create a signature for a subgraph starting at the given node with a specific depth.
    The signature contains the operation types of all nodes in the subgraph.

    Args:
        G: NetworkX DiGraph of the ONNX computation graph
        node_info: Dictionary mapping node names to their operation types
        node_name: Starting node for the subgraph
        depth: Maximum depth of the subgraph

    Returns:
        A tuple containing the signature of the subgraph
    """
    if depth == 0:
        return (node_info[node_name],)

    signatures = []
    # Get all successors and their signatures
    for succ in sorted(G.successors(node_name)):
        sig = get_node_signature(G, node_info, succ, depth - 1)
        signatures.append(sig)

    # Sort signatures to ensure consistent ordering
    signatures.sort()

    # Combine the current node's operation type with successor signatures
    return (node_info[node_name], tuple(signatures))


def format_subgraph_signature(signature, indent=0):
    """Format a signature tuple into a readable string representation."""
    if not isinstance(signature, tuple):
        return signature

    if len(signature) == 0:
        return ""

    if len(signature) == 1:
        return signature[0]

    op_type = signature[0]
    children = signature[1] if len(signature) > 1 else []

    result = op_type
    if children:
        result += " -> ["
        child_strs = []
        for child in children:
            child_strs.append(format_subgraph_signature(child, indent + 2))

        if child_strs:
            result += ", ".join(child_strs)
        result += "]"

    return result


def contains_all_operations_of_interest(signature, ops_set):
    """Check if a signature contains all specified operations."""
    if not ops_set:
        return True

    # Collect all operation types in this signature
    def collect_ops(sig, collected_ops):
        if isinstance(sig, str):
            collected_ops.add(sig)
            return
        if not sig:
            return
        collected_ops.add(sig[0])
        if len(sig) > 1:
            for child in sig[1]:
                collect_ops(child, collected_ops)

    all_ops_in_subgraph = set()
    collect_ops(signature, all_ops_in_subgraph)
    return ops_set.issubset(all_ops_in_subgraph)


def find_repeating_subgraphs(
    model_or_path,
    min_depth=2,
    max_depth=4,
    min_occurrences=2,
    operations_of_interest=None,
):
    """
    Find repeated subgraph patterns in an ONNX model.

    Args:
        model_path: Path to the ONNX model
        min_depth: Minimum depth for subgraph patterns
        max_depth: Maximum depth for subgraph patterns
        min_occurrences: Minimum number of occurrences to consider a subgraph as repeating
        operations_of_interest: Set of operation types to filter for (if None, include all operations)

    Returns:
        A dictionary mapping pattern hashes to (subgraph: DiGraph, nodes: list) tuples
        The original ONNX model
        The output tensor map
        The node to initializers map
    """
    model, G, node_info, output_map, node_to_initializers = build_graph_from_onnx(
        model_or_path
    )

    # Find all repeated patterns at different depths
    all_patterns = {}

    for depth in range(min_depth, max_depth + 1):
        pattern_to_nodes = defaultdict(list)

        # Get the signature for each node in the graph
        for node in G.nodes():
            try:
                signature = get_node_signature(G, node_info, node, depth)

                # Skip patterns that don't contain ALL operations of interest
                if operations_of_interest and not contains_all_operations_of_interest(
                    signature, operations_of_interest
                ):
                    continue

                # Extract the subgraph starting from this node
                subgraph = nx.dfs_tree(G, node, depth_limit=depth)

                # Use a hash of the signature as the dictionary key
                sig_hash = hashlib.md5(str(signature).encode()).hexdigest()
                pattern_to_nodes[sig_hash].append((node, subgraph))
            except (KeyError, nx.NetworkXError):
                pass

        # Filter for repeated patterns and add to results
        for sig_hash, nodes_and_graphs in pattern_to_nodes.items():
            if len(nodes_and_graphs) >= min_occurrences:
                # Store the first subgraph as the pattern template
                first_pattern_graph = nodes_and_graphs[0][1]
                all_subgraphs = [graph for _, graph in nodes_and_graphs]
                root_nodes = [node for node, _ in nodes_and_graphs]

                # Add node operation types to the pattern graph
                for n in first_pattern_graph.nodes():
                    if n in node_info:
                        first_pattern_graph.nodes[n]["op_type"] = node_info[n]

                all_patterns[sig_hash] = (
                    first_pattern_graph,
                    root_nodes,
                    all_subgraphs,
                )

    return all_patterns, model, output_map, node_to_initializers


def build_initializer_map(model):
    """
    Create a dictionary mapping initializer names to their TensorProto values.

    Args:
        model: ONNX ModelProto object

    Returns:
        Dictionary mapping initializer names to TensorProto objects
    """
    return {init.name: init for init in model.graph.initializer}


def extract_pattern_initializers(pattern_graph, node_to_initializers, initializer_map):
    """
    Extract initializers used by nodes in a pattern graph, segmented by dimensions.

    Args:
        pattern_graph: NetworkX DiGraph representing the pattern
        node_to_initializers: Dictionary mapping nodes to their initializer names
        initializer_map: Dictionary mapping initializer names to TensorProto objects

    Returns:
        Dictionary containing:
            'constants': List of 0-D initializers (scalar constants)
            'vectors': List of 1-D initializers (bias vectors)
            'matrices': List of tuples (tensor, shape) for 2-D+ initializers
    """
    initializers = {
        "constants": [],
        "vectors": [],
        "matrices": [],  # Will store (tensor, shape) tuples
    }

    for node in pattern_graph.nodes():
        if node in node_to_initializers:
            for init_name in node_to_initializers[node]:
                if init_name in initializer_map:
                    tensor = initializer_map[init_name]
                    dims = len(tensor.dims)

                    if dims == 0:
                        initializers["constants"].append(tensor)
                    elif dims == 1:
                        initializers["vectors"].append(tensor)
                    else:
                        initializers["matrices"].append((tensor, tensor.dims))

    # Sort matrices by total size (product of dimensions) in descending order
    initializers["matrices"].sort(key=lambda x: np.prod(x[1]), reverse=True)
    return initializers


def get_weight_matrices_from_subgraphs(model, patterns, node_to_initializers):
    """Extract weight matrices from repeating subgraph patterns."""
    all_matrices = []
    initializer_map = build_initializer_map(model)

    for pattern_hash, (pattern_graph, _, all_subgraphs) in patterns.items():
        # Extract initializers from each subgraph
        for subgraph in all_subgraphs:
            subgraph_initializers = extract_pattern_initializers(
                subgraph, node_to_initializers, initializer_map
            )
            all_matrices.extend(subgraph_initializers["matrices"])

    # Get largest group of matrices with matching shapes
    matrices = process_matrices_by_shape(all_matrices)

    return matrices


def analyze_onnx_subgraphs(
    model_path,
    min_depth=2,
    max_depth=4,
    min_occurrences=2,
    operations_of_interest=None,
    extract_tensors=False,
    show_initializers=False,
):
    """
    Analyze an ONNX model and print information about repeated subgraph patterns.
    Optionally extract tensor values from the most frequent pattern.

    Args:
        model_path: Path to the ONNX model
        min_depth: Minimum depth for subgraph patterns
        max_depth: Maximum depth for subgraph patterns
        min_occurrences: Minimum number of occurrences to consider a subgraph as repeating
        operations_of_interest: Set of operation types to include (e.g., {"Add", "MatMul", "Softmax"})
                               If None, all operations are considered
        extract_tensors: Whether to extract tensor values from the most frequent pattern
        show_initializers: Whether to show which nodes have weights in the initializers
    """
    print(f"Analyzing ONNX model: {model_path}")
    print(
        f"Looking for repeated subgraph patterns (depth {min_depth}-{max_depth}, min occurrences: {min_occurrences})"
    )

    if operations_of_interest:
        print(
            f"Filtering for subgraphs containing ALL of these operations: {', '.join(sorted(operations_of_interest))}"
        )

    repeating_patterns, model, output_map, node_to_initializers = (
        find_repeating_subgraphs(
            model_path,
            min_depth=min_depth,
            max_depth=max_depth,
            min_occurrences=min_occurrences,
            operations_of_interest=operations_of_interest,
        )
    )

    if not repeating_patterns:
        print("No repeated subgraph patterns found matching the criteria.")
        return

    # Sort patterns by number of occurrences
    sorted_patterns = sorted(
        repeating_patterns.items(), key=lambda x: len(x[1][1]), reverse=True
    )

    print(f"Found {len(sorted_patterns)} repeated subgraph patterns:")
    print("=" * 80)

    pattern_hashes = []

    tensor_fingerprint = None

    # Print information about each pattern
    for i, (pattern_hash, (pattern_graph, root_nodes, all_subgraphs)) in enumerate(
        sorted_patterns, 1
    ):
        print(f"\nPattern {i}: {len(root_nodes)} occurrences")
        print(f"Pattern Hash: {pattern_hash}")
        print(
            f"Root Nodes for This Pattern ({len(root_nodes)}): {', '.join(root_nodes)}"
        )

        initializer_map = build_initializer_map(model)
        pattern_initializers = extract_pattern_initializers(
            pattern_graph, node_to_initializers, initializer_map
        )
        print("Initializers within The First Occurrence of This Repeating Pattern:")
        if pattern_initializers["constants"]:
            print(f"- constants: {len(pattern_initializers['constants'])}")
        if pattern_initializers["vectors"]:
            print(f"- vectors: {len(pattern_initializers['vectors'])}")
        if pattern_initializers["matrices"]:
            print(f"- matrices: {len(pattern_initializers['matrices'])}")

        # Process matrices against tensor fingerprint
        if pattern_initializers["matrices"]:
            for matrix in pattern_initializers["matrices"]:
                if tensor_fingerprint is None:
                    # Initialize fingerprint with first matrix
                    tensor_fingerprint = onnx.numpy_helper.to_array(matrix)
                else:
                    # Convert both to numpy arrays and check dimensions match before multiplying
                    matrix_np = onnx.numpy_helper.to_array(matrix)
                    tensor_np = (
                        tensor_fingerprint
                        if isinstance(tensor_fingerprint, np.ndarray)
                        else onnx.numpy_helper.to_array(tensor_fingerprint)
                    )

                    if tensor_np.shape[1] == matrix_np.shape[0]:
                        check_matrix_values(tensor_np, "Tensor")
                        check_matrix_values(matrix_np, "Matrix")
                        tensor_fingerprint = np.matmul(tensor_np, matrix_np)
                        if not check_matrix_values(tensor_fingerprint, "Result"):
                            # Maybe normalize or take other corrective action
                            tensor_fingerprint = np.nan_to_num(tensor_fingerprint, 0)
                    else:
                        print(
                            f"Warning: Matrix dimensions don't match for multiplication. Tensor fingerprint shape: {tensor_np.shape}, Matrix shape: {matrix_np.shape}"
                        )
        # Print tensor fingerprint dimensions if it exists
        if tensor_fingerprint is not None:
            if isinstance(tensor_fingerprint, np.ndarray):
                print(f"Tensor Fingerprint Dimensions: {tensor_fingerprint.shape}")
            else:
                print(
                    f"Tensor Fingerprint Dimensions: {onnx.numpy_helper.to_array(tensor_fingerprint).shape}"
                )

        # Get signature for pattern graph root and format it
        root_node = list(pattern_graph.nodes())[0]  # Get first node as root
        pattern_signature = get_node_signature(
            pattern_graph,
            nx.get_node_attributes(pattern_graph, "op_type"),
            root_node,
            depth=15,
        )
        print(
            f"Repeating Pattern Signature: {format_subgraph_signature(pattern_signature)}"
        )

        # Track pattern hash
        pattern_hashes.append(pattern_hash)

    singular_matrix = get_top_singular_values_matrix(tensor_fingerprint)
    print(f"Singular Matrix: {singular_matrix}")

    print(f"All Repeating Pattern Hashes: {pattern_hashes}")


def compare_models_by_weights(
    model_path_1,
    model_path_2,
    min_depth=2,
    max_depth=4,
    min_occurrences=2,
    operations_of_interest=None,
):
    """
    Compare two ONNX models based on the weights in their repeating subgraph patterns.
    """
    print(f"\nComparing model weights:\n{model_path_1}\n{model_path_2}\n")

    svd_fingerprint_1 = generate_onnx_fingerprint(model_path_1)
    svd_fingerprint_2 = generate_onnx_fingerprint(model_path_2)

    # Calculate and print cosine similarity
    if svd_fingerprint_1 is not None and svd_fingerprint_2 is not None:
        flat_matrix_1 = svd_fingerprint_1.flatten()
        flat_matrix_2 = svd_fingerprint_2.flatten()
        cosine_sim = np.dot(flat_matrix_1, flat_matrix_2) / (
            np.linalg.norm(flat_matrix_1) * np.linalg.norm(flat_matrix_2)
        )
        print(f"Cosine similarity between singular value matrices: {cosine_sim}")

    return svd_fingerprint_1, svd_fingerprint_2


def compare_models_by_subgraphs(
    model_path_1,
    model_path_2,
    min_depth=2,
    max_depth=4,
    min_occurrences=2,
    operations_of_interest=None,
):
    """
    Compare two ONNX models based on their shared subgraph patterns.

    Args:
        model_path_1: Path to first ONNX model
        model_path_2: Path to second ONNX model
        min_depth: Minimum depth for subgraph patterns
        max_depth: Maximum depth for subgraph patterns
        min_occurrences: Minimum occurrences to consider a pattern
        operations_of_interest: Set of operation types to include

    Returns:
        float: Similarity score between 0 and 1, where 1 means identical subgraph patterns
    """
    print(f"\nComparing models:\n{model_path_1}\n{model_path_2}\n")

    # Get subgraph patterns for both models
    patterns_1, _, _, _ = find_repeating_subgraphs(
        model_path_1,
        min_depth=min_depth,
        max_depth=max_depth,
        min_occurrences=min_occurrences,
        operations_of_interest=operations_of_interest,
    )

    patterns_2, _, _, _ = find_repeating_subgraphs(
        model_path_2,
        min_depth=min_depth,
        max_depth=max_depth,
        min_occurrences=min_occurrences,
        operations_of_interest=operations_of_interest,
    )

    if not patterns_1 or not patterns_2:
        print("One or both models have no repeated subgraph patterns matching criteria")
        return 0.0

    # Get signatures for all patterns in both models
    signatures_1 = set()
    signatures_2 = set()

    for pattern_hash, (pattern_graph, _, all_subgraphs) in patterns_1.items():
        root_node = list(pattern_graph.nodes())[0]
        signature = get_node_signature(
            pattern_graph,
            nx.get_node_attributes(pattern_graph, "op_type"),
            root_node,
            depth=15,
        )
        signatures_1.add(signature)

    for pattern_hash, (pattern_graph, _, all_subgraphs) in patterns_2.items():
        root_node = list(pattern_graph.nodes())[0]
        signature = get_node_signature(
            pattern_graph,
            nx.get_node_attributes(pattern_graph, "op_type"),
            root_node,
            depth=15,
        )
        signatures_2.add(signature)

    # Calculate similarity using Jaccard index
    intersection = len(signatures_1.intersection(signatures_2))
    union = len(signatures_1.union(signatures_2))
    similarity = intersection / union if union > 0 else 0.0

    print(f"Number of patterns in model 1: {len(signatures_1)}")
    print(f"Number of patterns in model 2: {len(signatures_2)}")
    print(f"Number of shared patterns: {intersection}")
    print(f"Similarity score: {similarity:.3f}")

    return similarity


#####################################################################
# Matrix operations
#####################################################################


def check_matrix_values(matrix, name="Matrix"):
    """Debug helper to check matrix for invalid values."""
    if not np.all(np.isfinite(matrix)):
        print(f"{name} contains invalid values:")
        print(f"NaN count: {np.isnan(matrix).sum()}")
        print(f"Inf count: {np.isinf(matrix).sum()}")
        print(f"Max value: {np.nanmax(np.abs(matrix))}")
        print(f"Min value: {np.nanmin(np.abs(matrix[matrix != 0]))}")
    return np.all(np.isfinite(matrix))


def safe_matrix_multiply(matrix1, matrix2):
    """
    Safely multiply two matrices while avoiding overflow.

    Args:
        matrix1, matrix2: numpy arrays to multiply
    Returns:
        Result of matrix multiplication with overflow protection
    """
    # Skip if either matrix is 1D
    if matrix1.ndim == 1 or matrix2.ndim == 1:
        return matrix1

    # Convert to float64 for better precision
    matrix1 = matrix1.astype(np.float64)
    matrix2 = matrix2.astype(np.float64)

    # Normalize matrices by their max absolute values
    max1 = np.max(np.abs(matrix1))
    max2 = np.max(np.abs(matrix2))

    if max1 > 0 and max2 > 0:
        matrix1_normalized = matrix1 / max1
        matrix2_normalized = matrix2 / max2

        # Perform multiplication with normalized matrices
        result = np.matmul(matrix1_normalized, matrix2_normalized)

        # Scale result back (take log to avoid overflow)
        log_scale = np.log(max1) + np.log(max2)
        if log_scale < np.log(np.finfo(np.float64).max):
            result *= np.exp(log_scale)
        else:
            print(
                "Warning: Result scaling would cause overflow, keeping normalized result"
            )
    else:
        result = np.matmul(matrix1, matrix2)

    return result


def process_matrices_by_shape(matrices):
    """
    Group matrices by shape and return the largest group.

    Args:
        matrices: List of (tensor, shape) tuples

    Returns:
        List of tensors with matching shapes, or empty list if no matches found
    """
    if not matrices:
        return []

    # Group matrices by shape
    shape_groups = {}
    for tensor, shape in matrices:
        shape_key = tuple(shape)
        if shape_key not in shape_groups:
            shape_groups[shape_key] = []
        shape_groups[shape_key].append(tensor)

    # Find the group with the most matrices
    largest_group = max(
        shape_groups.items(), key=lambda x: len(x[1]), default=(None, [])
    )
    return largest_group[1]


def fold_matrices_from_subgraphs(matrices):
    """Fold a list of matrices into a single matrix by multiplying them together."""
    tensor_fingerprint = None
    for matrix in matrices:
        if tensor_fingerprint is None:
            matrix_np = onnx.numpy_helper.to_array(matrix)
            if matrix_np.ndim > 1:  # Only use 2D+ matrices
                tensor_fingerprint = matrix_np
        else:
            matrix_np = onnx.numpy_helper.to_array(matrix)
            if matrix_np.ndim > 1:  # Only use 2D+ matrices
                if tensor_fingerprint.shape[1] == matrix_np.shape[0]:
                    try:
                        tensor_fingerprint = safe_matrix_multiply(
                            tensor_fingerprint, matrix_np
                        )
                        if np.max(np.abs(tensor_fingerprint)) > 1e10:
                            tensor_fingerprint = tensor_fingerprint / np.max(
                                np.abs(tensor_fingerprint)
                            )
                        tensor_fingerprint = np.nan_to_num(tensor_fingerprint, 0)
                    except Exception as e:
                        print(f"Warning: Matrix multiplication failed: {e}")
                        continue
    return tensor_fingerprint


def get_top_singular_values_matrix(matrix, size=50, flatten=False):
    """
    Extract top singular values from a matrix and reshape into a size x size matrix.
    Includes error handling and matrix conditioning checks.

    Args:
        matrix: Input matrix (numpy array)
        size: Size of the output matrix (default 50)
        flatten: Whether to return a flattened 1D array instead of a 2D matrix

    Returns:
        size x size matrix containing the largest singular values, padded with zeros
    """
    try:
        # Check for invalid values
        if not np.all(np.isfinite(matrix)):
            print("Warning: Matrix contains NaN or Inf values")
            # Replace invalid values with 0
            matrix = np.nan_to_num(matrix, 0)

        # Try SVD with more robust algorithm
        singular_values = np.linalg.svd(matrix, compute_uv=False, hermitian=False)

    except np.linalg.LinAlgError:
        try:
            # Attempt with conditioning
            matrix = matrix.astype(np.float64)  # Ensure double precision
            # Add small amount of noise to help convergence
            noise = np.random.normal(0, 1e-10, matrix.shape)
            matrix = matrix + noise
            singular_values = np.linalg.svd(matrix, compute_uv=False, hermitian=False)
        except np.linalg.LinAlgError as e:
            print(f"SVD failed to converge: {e}")
            # Return zeros if all attempts fail
            return np.zeros((size, size))

    # Initialize result array
    result = np.zeros(size * size, dtype=np.float64)

    # Ensure we don't try to copy more values than we have space for
    n_values = min(len(singular_values), size * size)

    # Flatten singular values and copy them
    flat_singular_values = singular_values.flatten()[:n_values]
    result[: len(flat_singular_values)] = flat_singular_values

    # Reshape to size x size matrix
    if flatten:
        return result
    else:
        return result.reshape((size, size))


#####################################################################
# Example usage (for testing purposes)
#####################################################################

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Find repeated subgraph patterns in an ONNX model"
    )
    parser.add_argument("model_path", type=str, help="Path to the ONNX model file")
    parser.add_argument(
        "--min-depth", type=int, default=2, help="Minimum depth for subgraph patterns"
    )
    parser.add_argument(
        "--max-depth", type=int, default=4, help="Maximum depth for subgraph patterns"
    )
    parser.add_argument(
        "--min-occurrences",
        type=int,
        default=2,
        help="Minimum occurrences to consider a pattern as repeating",
    )
    parser.add_argument(
        "--operations",
        nargs="+",
        help="List of operation types to include (e.g., Add MatMul Softmax)",
    )
    parser.add_argument(
        "--extract-tensors",
        action="store_true",
        help="Extract tensor values from the most frequent pattern",
    )
    parser.add_argument(
        "--show-initializers",
        action="store_true",
        help="Show which nodes have weights in initializers",
    )
    parser.add_argument(
        "--compare-models",
        action="store_true",
        help="Compare two models by their subgraph patterns",
    )
    parser.add_argument(
        "--model-path-2", type=str, help="Path to the second ONNX model file"
    )

    args = parser.parse_args()

    # Convert operations list to a set if provided
    operations_of_interest = set(args.operations) if args.operations else None

    if args.compare_models:
        compare_models_by_subgraphs(
            args.model_path,
            args.model_path_2,
            min_depth=args.min_depth,
            max_depth=args.max_depth,
            min_occurrences=args.min_occurrences,
            operations_of_interest=operations_of_interest,
        )
        compare_models_by_weights(
            args.model_path,
            args.model_path_2,
            min_depth=args.min_depth,
            max_depth=args.max_depth,
            min_occurrences=args.min_occurrences,
            operations_of_interest=operations_of_interest,
        )

    else:
        analyze_onnx_subgraphs(
            args.model_path,
            min_depth=args.min_depth,
            max_depth=args.max_depth,
            min_occurrences=args.min_occurrences,
            operations_of_interest=operations_of_interest,
            extract_tensors=args.extract_tensors,
            show_initializers=args.show_initializers,
        )
