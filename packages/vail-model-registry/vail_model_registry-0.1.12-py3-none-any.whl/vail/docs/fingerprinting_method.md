

# Input/Output Fingerprinting Framework


  

## Overview

  

This framework implements a technique for creating "fingerprints" of language models based on the way their inputs and outputs are represented in their embedding spaces. The technique aims to extract signal from the way a model transforms inputs to outputs, without dependence on the token embedding itself. These fingerprints can be used to compare models, detect similarities, and potentially identify the origins of models.



## Conceptual Approach

  

### The Fingerprinting Method

  

The main `fingerprinter` function creates what we call a "linear approximation fingerprint" of a language model. It works as follows.

  

1.  **Input Selection**: We feed a set of chosen text strings (`probe_tokens`) into the model. These inputs are designed to elicit characteristic responses from the model. The examples currently used in the code provide include common tokens ("the", "of") as well as rare words ("zymurgy", "xylophone"). One could also try curating a list of domain-specific (eg medical) strings with the goal of extracting signal about how the model works with language in this domain.

  

2.  **Linear Approximation**: The method constructs a linear approximation of how the model transforms input embeddings to output distributions:

- Captures the input embeddings (`V` matrix) for our probe tokens using `embedding_layer(token_tensor)`

- Combines embeddings with positional encodings: `combined_embeddings = embeddings + position_embeddings`

- Obtains next-token output probabilities for the probe tokens via `model_obj.run_inference(input_tensor)` followed by `torch.softmax(logits, dim=-1)`

- Tracks the probabilities for a selected set of `target_tokens`

- Creates weighted linear combinations of target token embeddings (`U` matrix): `u_i = np.sum([target_probs[j] * target_embeddings[:, j] for j in range(M)], axis=0)`

- Finds transformation matrix `A` that approximates how the model maps V to U using pseudoinverse: `A = U @ V_pinv`

  

3.  **Eigenvalue Extraction**: From this transformation matrix A, we extract the largest eigenvalues via eigenvalue decomposition: `eigenvalues = np.linalg.eigvals(A)`

  

4.  **Normalization**: The resulting values are normalized to create a fixed-length numerical signature.

  

The fingerprint captures defining characteristics of the model's behavior in a compact form.

  

### Rationale

  

The intuition behind this approach is that the transformation matrix A encodes some information about how the model processes language. The eigenvalues of this matrix represent features of A that are invariant under conformal changes to the embedding space.


  

## Similarity Metrics

  

Once fingerprints are generated, we need ways to compare them. The framework implements several similarity metrics defined as functions:

  

-  **`L1_similarity`**: Based on Manhattan distance between sorted fingerprint vectors. It handles both real and complex vectors by sorting based on magnitude: `distance = np.sum(np.abs(vec1_sorted - vec2_sorted))`

  

-  **`wasserstein_distance_similarity`**: Treats fingerprints as probability distributions and measures the "earth mover's distance." Implemented by comparing cumulative distribution functions: `wasserstein_dist = np.sum(np.abs(cdf1 - cdf2))`

  

-  **`js_divergence_similarity`**: Measures similarity using Jensen-Shannon divergence from information theory: `js_div = jensenshannon(vec1_norm, vec2_norm)`

  

-  **`complex_euclidean_similarity`**: Uses standard Euclidean distance in the complex plane: `distance = np.sqrt(np.sum(np.abs(vec1 - vec2)**2))`

  

-  **`correlation_similarity`**: Based on Pearson correlation coefficient, handling real and imaginary parts separately for complex vectors: `combined_corr = (real_corr * real_var + imag_corr * imag_var) / total_var`

  

-  **`complex_cosine_similarity`**: Measures the cosine of the angle between fingerprint vectors, using Hermitian dot product for complex vectors: `dot_product = np.vdot(vec1, vec2)`



Each similarity metric captures different aspects of the relationship between fingerprints, with values closer to 1 indicating higher similarity. The framework uses `SimilarityMetric` objects to encapsulate these comparison methods.

## Testing and Verification

To verify the functionality of the Input/Output fingerprinting method, a testing module is provided in `tests/test_input_output_fp.py`. This module allows for detailed inspection of each step in the fingerprinting algorithm using real language models.

### Test Features

- **Component-Level Testing**: The test module breaks down the fingerprinting process into discrete steps, analyzing input embeddings, model outputs, and the linear approximation matrix separately.

- **Visualization Tools**: The test generates visualizations of token embeddings, output probabilities, transformation matrices, and eigenvalue distributions to provide intuitive understanding of how the algorithm works.


- **Step-by-Step vs. Full Method Comparison**: The test compares fingerprints generated through manual step-by-step calculation with those produced by the unified method to verify consistency.

### Usage

The test module can be run directly:
```bash
python tests/test_input_output_fp.py
```

By default, the test uses a small language model (distilgpt2) and a limited set of probe and target tokens for efficient analysis, but these parameters can be modified to test different models or token sets.