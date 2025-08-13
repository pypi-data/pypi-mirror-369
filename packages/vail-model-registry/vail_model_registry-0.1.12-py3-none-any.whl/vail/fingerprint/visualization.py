import colorsys

import matplotlib.colors as mcolors
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cosine


def generate_ipv6_from_vector(vector, method="average"):
    """
    Generate IPv6-style address from a fingerprint vector.

    Args:
        vector: List of float values representing the model fingerprint
        method: "average" (segment averages) or "keypoints" (uses distribution points)

    Returns:
        str: IPv6-style address
    """
    segments = 8  # IPv6 has 8 segments

    if method == "average":
        # Split vector into 8 segments and average each segment
        elements_per_segment = len(vector) // segments
        remainder = len(vector) % segments

        ipv6_segments = []
        start_idx = 0

        for i in range(segments):
            # Add one extra element to early segments if we have a remainder
            extra = 1 if i < remainder else 0
            end_idx = start_idx + elements_per_segment + extra

            # Get elements for this segment
            segment_elements = vector[start_idx:end_idx]

            # Average the values in this segment
            mean_value = sum(segment_elements) / len(segment_elements)

            # Convert to hexadecimal (max value FFFF)
            hex_value = format(int(mean_value * 65535), "04x")
            ipv6_segments.append(hex_value)

            start_idx = end_idx

    elif method == "keypoints":
        # Select key points in the vector
        keypoints = [
            vector[0],  # First element
            vector[len(vector) // 4],  # 25% point
            vector[len(vector) // 2],  # Middle element
            vector[3 * len(vector) // 4],  # 75% point
            max(vector[: len(vector) // 4]),  # Max in first quarter
            max(vector[len(vector) // 4 : len(vector) // 2]),  # Max in second quarter
            max(
                vector[len(vector) // 2 : 3 * len(vector) // 4]
            ),  # Max in third quarter
            max(vector[3 * len(vector) // 4 :]),  # Max in last quarter
        ]

        # Convert to hexadecimal
        ipv6_segments = [format(int(val * 65535), "04x") for val in keypoints]

    else:
        raise ValueError("Method must be 'average' or 'keypoints'")

    # Join with colons to form IPv6 address
    ipv6_address = ":".join(ipv6_segments)
    return ipv6_address


def calculate_similarity(vector1, vector2, method="cosine"):
    """
    Calculate similarity between two fingerprint vectors.

    Args:
        vector1, vector2: Lists of float values representing model fingerprints
        method: Similarity metric to use ("cosine", "euclidean", "correlation", "l1")

    Returns:
        float: Similarity score (0-1 where 1 is identical)
    """
    if method == "cosine":
        # Cosine similarity: 1 - cosine distance (0-1 where 1 is identical)
        similarity = 1 - cosine(vector1, vector2)
    elif method == "euclidean":
        # Euclidean distance normalized to 0-1 range
        distance = np.sqrt(np.sum((np.array(vector1) - np.array(vector2)) ** 2))
        max_possible_distance = np.sqrt(len(vector1))  # Max if all elements differ by 1
        # Handle division by zero if vectors are empty or max_possible_distance is zero
        if max_possible_distance == 0:
            similarity = 1.0 if np.all(np.array(vector1) == np.array(vector2)) else 0.0
        else:
            similarity = 1 - min(distance / max_possible_distance, 1)
    elif method == "correlation":
        # Pearson correlation coefficient (ranges from -1 to 1, so rescale to 0-1)
        correlation = np.corrcoef(vector1, vector2)[0, 1]
        similarity = (correlation + 1) / 2
    elif method == "l1":
        # L1 (Manhattan) distance normalized to 0-1 range
        vec1 = np.array(vector1)
        vec2 = np.array(vector2)
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length for L1 similarity")
        distance = np.sum(np.abs(vec1 - vec2))
        # Assuming vector elements are roughly in [0, 1]
        max_possible_distance = np.sum(vec1) + np.sum(vec2)
        similarity = 1 - (distance / max_possible_distance)
    else:
        raise ValueError("Method must be 'cosine', 'euclidean', 'correlation', or 'l1'")

    return similarity


def adjust_color_by_similarity(base_color, similarity, max_lightness_change=0.4):
    """
    Adjust a color based on similarity to reference model.

    Args:
        base_color: Base color in any matplotlib format (hex, name, RGB)
        similarity: Similarity score (0-1)
        max_lightness_change: Maximum change in lightness (0-1)

    Returns:
        str: Adjusted color in hex format
    """
    # Convert to RGB
    rgb = mcolors.to_rgb(base_color)

    # Convert to HSL (Hue, Saturation, Lightness)
    h, lightness, s = colorsys.rgb_to_hls(*rgb)

    # Adjust lightness based on similarity
    # Lower similarity = lighter color (more different from reference)
    lightness_change = max_lightness_change * (1 - similarity)
    new_lightness = min(1, lightness + lightness_change)

    # Convert back to RGB
    new_rgb = colorsys.hls_to_rgb(h, new_lightness, s)

    # Convert to hex
    hex_color = mcolors.rgb2hex(new_rgb)

    return hex_color


def create_family_fingerprint_visualization(
    vectors,
    model_names,
    families=None,
    reference_indices=None,
    family_colors=None,
    similarity_method="l1",
    save_path=None,
    show_ipv6=True,
    show_similarity=True,
):
    """
    Creates a visualization of fingerprint vectors, grouped and colored by family,
    potentially highlighting reference models and showing similarities.

    Args:
        vectors: List of lists containing fingerprint vectors
        model_names: List of model names corresponding to the vectors
        families: List of family names for each model (optional)
        reference_indices: Dictionary mapping family names to indices of reference models (optional)
        family_colors: Dictionary mapping family names to colors (optional)
        similarity_method: Method for calculating similarity ('cosine', 'l1', 'l2')
        save_path: Path to save the visualization (if None, returns figure or bytes)
        show_ipv6: Whether to show IPv6 identifiers in the title (default True)
        show_similarity: Whether to show similarity scores in the title (default True)
    """
    # If no families provided, try to infer from model names
    if families is None:
        families = []
        for name in model_names:
            # Try to extract family name (everything before the first number or dash)
            import re

            match = re.search(r"^([A-Za-z]+)", name)
            if match:
                families.append(match.group(1))
            else:
                families.append("Unknown")

    # Get unique family names and assign colors if not provided
    unique_families = list(set(families))
    if family_colors is None:
        # Default colors for families
        default_colors = [
            "#7080b0",
            "#3366bb",
            "#485b6f",
            "#6b486b",
            "#a05d56",
            "#2c7fb8",
        ]
        family_colors = {}
        for i, family in enumerate(unique_families):
            family_colors[family] = default_colors[i % len(default_colors)]

    # Set reference models for each family if not provided
    if reference_indices is None:
        reference_indices = {}
        for family in unique_families:
            # Find first model in each family to use as reference
            for i, (name, fam) in enumerate(zip(model_names, families)):
                if fam == family:
                    reference_indices[family] = i
                    break

    # Calculate similarities and assign colors
    colors = []
    similarities = []

    for i, (vector, family) in enumerate(zip(vectors, families)):
        # Get reference vector for this family
        ref_idx = reference_indices.get(family, i)  # Default to self if no reference
        ref_vector = vectors[ref_idx]

        # Calculate similarity to reference
        if i == ref_idx:
            similarity = 1.0  # Reference model is identical to itself
        else:
            similarity = calculate_similarity(
                vector, ref_vector, method=similarity_method
            )

        # Adjust color based on similarity
        base_color = family_colors[family]
        adjusted_color = adjust_color_by_similarity(base_color, similarity)

        colors.append(adjusted_color)
        similarities.append(similarity)

    # Set up the figure
    fig_height = 3 * len(vectors) + 2
    fig, axes = plt.subplots(
        len(vectors) + 1,
        1,
        figsize=(12, fig_height),
        gridspec_kw={"height_ratios": [3] * len(vectors) + [1]},
    )

    # Make axes a list if there's only one plot
    if len(vectors) == 1:
        axes = [axes, fig.add_subplot(2, 1, 2)]

    # Process each vector
    for i, (vector, name, family_specific_color, similarity, family) in enumerate(
        zip(vectors, model_names, colors, similarities, families)
    ):
        ax = axes[i]

        # Vector processing: Use the vector as is, no padding/truncation.
        processed_display_vector = list(vector)

        sqrt_display_values = [np.sqrt(max(0, v)) for v in processed_display_vector]

        min_sqrt_for_opacity = min(sqrt_display_values)
        max_sqrt_for_opacity = max(sqrt_display_values)

        calculated_bar_widths = []  # Store raw calculated widths (opacities)
        total_bar_widths_sum = 0.0

        normalization_denominator_opacity = max_sqrt_for_opacity - min_sqrt_for_opacity

        for current_sqrt_val in sqrt_display_values:
            bar_width_val = 0.0
            # Denominator is guarded by use_direct_opacity_calc
            normalized_sqrt_val = (
                current_sqrt_val - min_sqrt_for_opacity
            ) / normalization_denominator_opacity
            bar_width_val = 0.1 + normalized_sqrt_val * (max_sqrt_for_opacity - 0.1)

            calculated_bar_widths.append(bar_width_val)
            total_bar_widths_sum += bar_width_val

        num_bars_current_vector = len(calculated_bar_widths)
        total_spaces_width = 0.0
        dynamic_spacing_current_vector = 0.0

        if num_bars_current_vector > 0:
            total_spaces_width = total_bar_widths_sum
            if num_bars_current_vector > 1:
                dynamic_spacing_current_vector = total_spaces_width / (
                    num_bars_current_vector - 1
                )

        current_total_dynamic_plot_width = total_bar_widths_sum + total_spaces_width
        effective_plot_width = (
            current_total_dynamic_plot_width
            if current_total_dynamic_plot_width > 1e-9
            else 1.0
        )

        ax.add_patch(
            patches.Rectangle(
                (0, 0),
                effective_plot_width,
                1,
                facecolor="#e9ecf1",
                edgecolor="#cccccc",
                linewidth=1,
                zorder=1,
            )
        )

        current_x_position = 0.0
        for j in range(num_bars_current_vector):
            bar_dynamic_width = calculated_bar_widths[j]  # Use the raw calculated width
            bar_render_alpha = max(
                0, min(1, bar_dynamic_width)
            )  # Clamp only for alpha channel

            ax.add_patch(
                patches.Rectangle(
                    (current_x_position, 0),
                    bar_dynamic_width,  # Width uses raw value
                    1,
                    facecolor=family_specific_color,
                    alpha=bar_render_alpha,  # Alpha is clamped for rendering
                    edgecolor=None,
                    linewidth=0,
                    zorder=2,
                )
            )
            current_x_position += bar_dynamic_width
            if j < num_bars_current_vector - 1:
                current_x_position += dynamic_spacing_current_vector

        ipv6_address = generate_ipv6_from_vector(vector)
        ax.set_xlim(0, effective_plot_width)
        ax.set_ylim(0, 1)

        # Format title with family indicator
        title = f"{name}"
        if i == reference_indices.get(family, -1):
            title += " (Reference)"
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)

        # Add colored family indicator
        family_rect = patches.Rectangle(
            (-5, 0), 4, 1, facecolor=family_colors[family], edgecolor="none", zorder=3
        )
        ax.add_patch(family_rect)

        # Disable axis ticks and labels for the track itself
        ax.set_yticks([])
        ax.set_xticks([])

        # Add information below the plot
        info_text = ""

        # Add similarity score if requested
        if show_similarity and i != reference_indices.get(family, -1):
            ref_name = model_names[reference_indices.get(family, i)]
            info_text += f"Similarity to {ref_name.split()[0]}: {similarity:.3f}    "

        # Add IPv6 address if requested
        if show_ipv6:
            info_text += f"IPv6: {ipv6_address}"

        if info_text:
            # Position text slightly below the track, centered horizontally
            ax.text(
                effective_plot_width / 2,
                -0.1,
                info_text,
                fontsize=8,
                family="monospace",
                ha="center",
                va="top",
                color="#555555",
            )

    # Ensure the legend axis is clear if it was previously ax_pos (it is axes[-1])
    axes[-1].clear()
    axes[-1].axis("off")

    # Add legend for families
    legend_elements = []
    for family, color in family_colors.items():
        legend_elements.append(
            patches.Patch(facecolor=color, edgecolor=None, label=family)
        )

    # Position legend
    fig.legend(
        handles=legend_elements,
        loc="upper right",
        bbox_to_anchor=(0.99, 0.99),
        fontsize=9,
    )

    # Add overall title
    fig.suptitle("Model Fingerprint Comparison", fontsize=16, fontweight="bold", y=0.98)

    # Adjust layout to prevent overlaps, especially at the top for suptitle/legend
    # and add horizontal space between plots
    plt.subplots_adjust(hspace=0.6, top=0.92)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)  # Close the figure after saving to free memory
        return save_path
    else:
        plt.show()


def analyze_fingerprints_by_family(
    vectors, model_names, families=None, similarity_method="cosine"
):
    """
    Analyze fingerprint vectors grouped by family and print insights.

    Args:
        vectors: List of lists containing fingerprint vectors
        model_names: List of model names
        families: List of family names for each model (optional)
        similarity_method: Method for calculating similarity
    """
    # If no families provided, try to infer from model names
    if families is None:
        families = []
        for name in model_names:
            # Try to extract family name (everything before the first number or dash)
            import re

            match = re.search(r"^([A-Za-z]+)", name)
            if match:
                families.append(match.group(1))
            else:
                families.append("Unknown")

    # Group models by family
    family_groups = {}
    for i, (vector, name, family) in enumerate(zip(vectors, model_names, families)):
        if family not in family_groups:
            family_groups[family] = []
        family_groups[family].append((i, vector, name))

    # Analyze each family
    for family, models in family_groups.items():
        print(f"\n=== Family: {family} ===")

        # Choose first model as reference for similarity calculations
        ref_idx, ref_vector, ref_name = models[0]
        print(f"Reference model: {ref_name}")

        # Analyze each model in the family
        for i, (idx, vector, name) in enumerate(models):
            print(f"\n  Model: {name}")

            # Basic statistics
            print(f"    Vector length: {len(vector)}")
            print(f"    Value range: {min(vector):.6f} to {max(vector):.6f}")
            print(f"    Mean value: {np.mean(vector):.6f}")

            # Distribution features
            q1 = np.percentile(vector, 25)
            q3 = np.percentile(vector, 75)
            last_value = vector[-1]
            max_value = max(vector)
            print(f"    Q1/Q3 ratio: {q1 / q3:.4f}")
            print(f"    Last/Max ratio: {last_value / max_value:.4f}")

            # Similarity to reference (skip for reference itself)
            if i > 0:
                similarity = calculate_similarity(
                    vector, ref_vector, method=similarity_method
                )
                print(f"    Similarity to reference: {similarity:.4f}")

            # Generate IPv6 identifiers
            ipv6_avg = generate_ipv6_from_vector(vector, method="average")
            print(f"    IPv6: {ipv6_avg}")

    # Compare families by average fingerprint
    if len(family_groups) > 1:
        print("\n=== Cross-Family Comparison ===")
        family_avg_vectors = {}

        # Calculate average vector for each family
        for family, models in family_groups.items():
            vectors_in_family = [v for _, v, _ in models]
            avg_vector = np.mean(vectors_in_family, axis=0)
            family_avg_vectors[family] = avg_vector

        # Compare each pair of families
        families = list(family_avg_vectors.keys())
        for i in range(len(families)):
            for j in range(i + 1, len(families)):
                fam1, fam2 = families[i], families[j]
                similarity = calculate_similarity(
                    family_avg_vectors[fam1],
                    family_avg_vectors[fam2],
                    method=similarity_method,
                )
                print(f"  {fam1} vs {fam2} similarity: {similarity:.4f}")
