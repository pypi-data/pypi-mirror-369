"""
Metrics Analysis for Fingerprint Similarity

This module provides functionality for analyzing model fingerprint similarity metrics,
including statistical analysis and grouping models by family and type.
"""

import datetime
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Optional, Tuple

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio


@dataclass
class ModelInfo:
    """Model information including ID, family, type, and optional display name."""

    id: str
    family: str
    model_type: str
    display_name: Optional[str] = None


class ModelPairInfo(NamedTuple):
    """Information about a pair of models and their similarity."""

    model1_id: str
    model1_family: str
    model1_type: str
    model2_id: str
    model2_family: str
    model2_type: str
    similarity: float
    model1_display_name: Optional[str] = None
    model2_display_name: Optional[str] = None

    def __str__(self) -> str:
        """String representation of model pair with similarity score."""
        model1_label = self.model1_display_name or self.model1_id
        model2_label = self.model2_display_name or self.model2_id
        return (
            f"{model1_label} ({self.model1_family}/{self.model1_type}) <-> "
            f"{model2_label} ({self.model2_family}/{self.model2_type}): {self.similarity:.4f}"
        )


@dataclass
class SimilarityStats:
    """Statistics for similarity scores."""

    min: float
    max: float
    mean: float
    variance: float
    model_pairs: List[Tuple[str, str]]  # Pairs of model IDs
    scores: List[float]  # Similarity scores corresponding to the pairs
    detailed_pairs: List[ModelPairInfo]  # Detailed information about each pair


class MetricsAnalyzer:
    """Analyzes model fingerprint similarity metrics."""

    def __init__(self, results_file: str, models_info: List[Dict[str, str]]):
        """
        Initialize the metrics analyzer.

        Args:
            results_file: Path to JSON file containing similarity matrices
            models_info: List of dictionaries with model_id, family, and model_type keys
        """
        self.results_file = results_file
        self.model_info_map = {
            model_data["model_id"]: ModelInfo(
                id=model_data["model_id"],
                family=model_data["family"],
                model_type=model_data["model_type"],
                display_name=model_data.get("display_name"),
            )
            for model_data in models_info
        }

        # Load similarity data
        self.similarity_data = self.load_similarity_data(results_file)

        # Initialize output directory for plots
        self.output_dir = os.path.join(
            os.path.dirname(results_file), "metrics_analysis"
        )
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate timestamp for this analysis run
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def load_similarity_data(self, results_file: str) -> Dict:
        """
        Load similarity data from results file.

        Args:
            results_file: Path to results JSON file

        Returns:
            Dictionary containing similarity matrices
        """
        with open(results_file, "r") as f:
            data = json.load(f)

        return data

    def get_similarity_matrix(
        self, method_type: str, metric_name: str
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Get similarity matrix for a specific method and metric.

        Args:
            method_type: Fingerprinting method type
            metric_name: Similarity metric name

        Returns:
            Tuple of (similarity matrix, list of model IDs)
        """
        sim_data = (
            self.similarity_data["similarity_matrices"]
            .get(method_type, {})
            .get(metric_name, {})
        )

        if not sim_data:
            raise ValueError(
                f"No similarity data found for method '{method_type}' and metric '{metric_name}'"
            )

        matrix = np.array(sim_data["matrix"])
        models = sim_data["models"]

        return matrix, models

    def filter_models_with_info(self, all_models: List[str]) -> List[str]:
        """
        Filter models to only include those with provided info.

        Args:
            all_models: List of all model IDs in the similarity matrix

        Returns:
            Filtered list of model IDs
        """
        return [model_id for model_id in all_models if model_id in self.model_info_map]

    def create_model_pair_info(
        self, model1_id: str, model2_id: str, similarity: float
    ) -> ModelPairInfo:
        """
        Create a ModelPairInfo object for a pair of models.

        Args:
            model1_id: ID of the first model
            model2_id: ID of the second model
            similarity: Similarity score between the models

        Returns:
            ModelPairInfo object
        """
        model1 = self.model_info_map[model1_id]
        model2 = self.model_info_map[model2_id]

        return ModelPairInfo(
            model1_id=model1_id,
            model1_family=model1.family,
            model1_type=model1.model_type,
            model2_id=model2_id,
            model2_family=model2.family,
            model2_type=model2.model_type,
            similarity=similarity,
            model1_display_name=model1.display_name,
            model2_display_name=model2.display_name,
        )

    def analyze_intrafamily_similarity(
        self, method_type: str, metric_name: str
    ) -> Dict[str, SimilarityStats]:
        """
        Analyze similarity within each model family.

        Args:
            method_type: Fingerprinting method type
            metric_name: Similarity metric name

        Returns:
            Dictionary mapping family names to similarity statistics
        """
        matrix, all_models = self.get_similarity_matrix(method_type, metric_name)

        # Filter models to only include those with provided info
        models = self.filter_models_with_info(all_models)

        # Group models by family using defaultdict
        family_models = defaultdict(list)
        for model_id in models:
            family = self.model_info_map[model_id].family
            family_models[family].append(model_id)

        # Compute statistics for each family
        family_stats = {}
        for family, family_model_ids in family_models.items():
            if len(family_model_ids) < 2:
                continue  # Skip families with fewer than 2 models

            # Collect all pairwise similarities
            pairs = []
            scores = []
            detailed_pairs = []

            for i, model1 in enumerate(family_model_ids):
                idx1 = all_models.index(model1)
                for model2 in family_model_ids[i + 1 :]:
                    idx2 = all_models.index(model2)
                    score = matrix[idx1, idx2]
                    pairs.append((model1, model2))
                    scores.append(score)

                    # Create detailed pair info
                    pair_info = self.create_model_pair_info(model1, model2, score)
                    detailed_pairs.append(pair_info)

            # Sort detailed pairs by similarity score (descending)
            detailed_pairs.sort(key=lambda p: p.similarity, reverse=True)

            # Compute statistics
            family_stats[family] = SimilarityStats(
                min=float(np.min(scores)),
                max=float(np.max(scores)),
                mean=float(np.mean(scores)),
                variance=float(np.var(scores)),
                model_pairs=pairs,
                scores=scores,
                detailed_pairs=detailed_pairs,
            )

        return family_stats

    def analyze_interfamily_similarity(
        self, method_type: str, metric_name: str
    ) -> Dict[Tuple[str, str], SimilarityStats]:
        """
        Analyze similarity between pairs of model families.

        Args:
            method_type: Fingerprinting method type
            metric_name: Similarity metric name

        Returns:
            Dictionary mapping family pairs to similarity statistics
        """
        matrix, all_models = self.get_similarity_matrix(method_type, metric_name)

        # Filter models to only include those with provided info
        models = self.filter_models_with_info(all_models)

        # Group models by family using defaultdict
        family_models = defaultdict(list)
        for model_id in models:
            family = self.model_info_map[model_id].family
            family_models[family].append(model_id)

        # Compute statistics for each pair of families
        family_pair_stats = {}
        families = list(family_models.keys())
        for i, family1 in enumerate(families):
            for family2 in families[i + 1 :]:
                # Collect all pairwise similarities between families
                pairs = []
                scores = []
                detailed_pairs = []

                for model1 in family_models[family1]:
                    idx1 = all_models.index(model1)
                    for model2 in family_models[family2]:
                        idx2 = all_models.index(model2)
                        score = matrix[idx1, idx2]
                        pairs.append((model1, model2))
                        scores.append(score)

                        # Create detailed pair info
                        pair_info = self.create_model_pair_info(model1, model2, score)
                        detailed_pairs.append(pair_info)

                if scores:  # Only create stats if there are scores
                    # Sort detailed pairs by similarity score (descending)
                    detailed_pairs.sort(key=lambda p: p.similarity, reverse=True)

                    family_pair_stats[(family1, family2)] = SimilarityStats(
                        min=float(np.min(scores)),
                        max=float(np.max(scores)),
                        mean=float(np.mean(scores)),
                        variance=float(np.var(scores)),
                        model_pairs=pairs,
                        scores=scores,
                        detailed_pairs=detailed_pairs,
                    )

        return family_pair_stats

    def analyze_type_pair_similarity(
        self, method_type: str, metric_name: str
    ) -> Dict[str, SimilarityStats]:
        """
        Analyze similarity for model pairs of different types within the same family.
        Then groups these pairs by their type combination (e.g., "Base-Distilled")
        across different families.

        Args:
            method_type: Fingerprinting method type
            metric_name: Similarity metric name

        Returns:
            Dictionary mapping type pairs to similarity statistics
        """
        matrix, all_models = self.get_similarity_matrix(method_type, metric_name)

        # Filter models to only include those with provided info
        models = self.filter_models_with_info(all_models)

        # Group models by family and type
        family_type_models = defaultdict(list)
        for model_id in models:
            info = self.model_info_map[model_id]
            key = (info.family, info.model_type)
            family_type_models[key].append(model_id)

        # Find all pairs of types within each family first
        # This will collect all the similarity scores for each type pair within each family
        family_type_pairs = defaultdict(
            list
        )  # Maps type pair to list of (family, model1, model2, score)

        # Get all family-type combinations
        family_types = sorted(family_type_models.keys())

        # Iterate through all pairs of family-type combinations
        for i, (family1, type1) in enumerate(family_types):
            for j, (family2, type2) in enumerate(family_types[i + 1 :], i + 1):
                # Only consider pairs within the same family but of different types
                if family1 == family2 and type1 != type2:
                    # Create a canonical type pair key (alphabetical order)
                    type_pair = tuple(sorted([type1, type2]))

                    models1 = family_type_models[(family1, type1)]
                    models2 = family_type_models[(family2, type2)]

                    # For each model pair of this type combination
                    for model1 in models1:
                        idx1 = all_models.index(model1)
                        for model2 in models2:
                            idx2 = all_models.index(model2)
                            score = matrix[idx1, idx2]

                            # Store each pair with its family, models, and score
                            family_type_pairs[type_pair].append(
                                (family1, model1, model2, score)
                            )

        # Now group the pairs by type combination and compute statistics
        type_pair_stats = {}
        for type_pair, pairs_data in family_type_pairs.items():
            # Create a readable key from the type pair
            key = f"{type_pair[0]}-{type_pair[1]}"

            # Collect all pairs and scores
            pairs = []
            scores = []
            detailed_pairs = []

            for family, model1, model2, score in pairs_data:
                pairs.append((model1, model2))
                scores.append(score)

                # Create detailed pair info
                pair_info = self.create_model_pair_info(model1, model2, score)
                detailed_pairs.append(pair_info)

            if scores:  # Only create stats if there are scores
                # Sort detailed pairs by similarity score (descending)
                detailed_pairs.sort(key=lambda p: p.similarity, reverse=True)

                type_pair_stats[key] = SimilarityStats(
                    min=float(np.min(scores)),
                    max=float(np.max(scores)),
                    mean=float(np.mean(scores)),
                    variance=float(np.var(scores)),
                    model_pairs=pairs,
                    scores=scores,
                    detailed_pairs=detailed_pairs,
                )

        return type_pair_stats

    def plot_box_whisker(
        self, stats_data: Dict, title: str, xlabel: str, filename: str
    ) -> str:
        """
        Create an interactive box and whisker plot for similarity statistics.

        Args:
            stats_data: Dictionary mapping categories to SimilarityStats
            title: Plot title
            xlabel: X-axis label
            filename: Output filename

        Returns:
            Path to the saved HTML plot
        """
        # Prepare data for plotting
        plot_data = []
        labels = []

        # Sort categories by mean similarity
        sorted_items = sorted(stats_data.items(), key=lambda x: x[1].mean, reverse=True)

        for category, stats in sorted_items:
            plot_data.append(stats.scores)
            labels.append(f"{category}\n(mean={stats.mean:.3f})")

        # Create interactive plot using Plotly
        fig = go.Figure()

        for i, (label, scores) in enumerate(zip(labels, plot_data)):
            # Add box plot for this category
            fig.add_trace(
                go.Box(
                    y=scores,
                    name=label,
                    boxmean=True,  # Shows the mean as a dashed line
                    boxpoints="outliers",  # Only show outlier points
                )
            )

        # Find min and max values across all scores to set reasonable y-axis bounds
        all_scores = [score for sublist in plot_data for score in sublist]
        y_min = max(0, min(all_scores) - 0.05)  # Add small padding but don't go below 0
        y_max = min(1, max(all_scores) + 0.05)  # Add small padding but don't exceed 1

        # Simple layout with increased size
        fig.update_layout(
            title=title,
            xaxis_title=xlabel,
            yaxis_title="Similarity Score",
            width=1400,  # Increased width
            height=800,  # Increased height
            yaxis=dict(
                range=[y_min, y_max]  # Dynamic range based on actual data
            ),
            xaxis=dict(tickangle=45, automargin=True),
        )

        # Save interactive plot
        html_output_path = os.path.join(
            self.output_dir, f"{filename}_{self.timestamp}.html"
        )
        pio.write_html(
            fig,
            file=html_output_path,
            auto_open=False,
            include_plotlyjs="cdn",
            full_html=True,
            config={"scrollZoom": True, "displayModeBar": True, "responsive": True},
        )

        return html_output_path

    def generate_detailed_pair_report(
        self, stats: SimilarityStats, output_path: str, title: str
    ) -> None:
        """
        Generate a detailed report of model pairs and their similarities.

        Args:
            stats: SimilarityStats object containing detailed pair information
            output_path: Path to save the report
            title: Title for the report
        """
        with open(output_path, "w") as f:
            f.write(f"{title}\n")
            f.write(f"{'-' * len(title)}\n\n")
            f.write(f"Total pairs: {len(stats.detailed_pairs)}\n")
            f.write(f"Min similarity: {stats.min:.4f}\n")
            f.write(f"Max similarity: {stats.max:.4f}\n")
            f.write(f"Mean similarity: {stats.mean:.4f}\n")
            f.write(f"Variance: {stats.variance:.4f}\n\n")

            f.write("Model pairs sorted by similarity (descending):\n")
            f.write("-" * 80 + "\n")

            for i, pair_info in enumerate(stats.detailed_pairs, 1):
                f.write(f"{i}. {pair_info}\n")

    def generate_consolidated_report(
        self,
        stats_dict,
        output_path: str,
        method_type: str,
        metric_name: str,
        report_type: str,
    ) -> str:
        """
        Generate a consolidated report of all pairs for a specific category.

        Args:
            stats_dict: Dictionary mapping group names to SimilarityStats objects
            output_path: Path to save the report
            method_type: Fingerprinting method type
            metric_name: Similarity metric name
            report_type: Type of report (intrafamily, interfamily, type_pair)

        Returns:
            Path to the saved report
        """
        if not stats_dict:
            return None

        title = f"Combined {report_type.title()} Similarity Report ({method_type}, {metric_name})"

        with open(output_path, "w") as f:
            f.write(f"{title}\n")
            f.write(f"{'=' * len(title)}\n\n")

            # Write overview section
            f.write("OVERVIEW\n")
            f.write("--------\n")
            if report_type == "intrafamily":
                f.write(
                    f"{'Family':<20} {'Min':<10} {'Max':<10} {'Mean':<10} {'Variance':<10} {'# Pairs'}\n"
                )
                f.write(f"{'-' * 70}\n")

                for group_name, stats in sorted(
                    stats_dict.items(), key=lambda x: x[1].mean, reverse=True
                ):
                    f.write(
                        f"{group_name:<20} {stats.min:<10.4f} {stats.max:<10.4f} "
                        f"{stats.mean:<10.4f} {stats.variance:<10.4f} {len(stats.model_pairs)}\n"
                    )

            elif report_type == "interfamily":
                f.write(
                    f"{'Family Pair':<30} {'Min':<10} {'Max':<10} {'Mean':<10} {'Variance':<10} {'# Pairs'}\n"
                )
                f.write(f"{'-' * 80}\n")

                for (fam1, fam2), stats in sorted(
                    stats_dict.items(), key=lambda x: x[1].mean, reverse=True
                ):
                    group_name = f"{fam1} vs {fam2}"
                    f.write(
                        f"{group_name:<30} {stats.min:<10.4f} {stats.max:<10.4f} "
                        f"{stats.mean:<10.4f} {stats.variance:<10.4f} {len(stats.model_pairs)}\n"
                    )

            elif report_type == "type_pair":
                f.write(
                    f"{'Type Pair':<40} {'Min':<10} {'Max':<10} {'Mean':<10} {'Variance':<10} {'# Pairs'}\n"
                )
                f.write(f"{'-' * 90}\n")

                for group_name, stats in sorted(
                    stats_dict.items(), key=lambda x: x[1].mean, reverse=True
                ):
                    f.write(
                        f"{group_name:<40} {stats.min:<10.4f} {stats.max:<10.4f} "
                        f"{stats.mean:<10.4f} {stats.variance:<10.4f} {len(stats.model_pairs)}\n"
                    )

            # Write detailed reports for each group
            f.write("\n\nDETAILED REPORTS\n")
            f.write("===============\n\n")

            if report_type == "intrafamily":
                for family, stats in sorted(
                    stats_dict.items(), key=lambda x: x[1].mean, reverse=True
                ):
                    f.write(f"\n{'=' * 80}\n")
                    f.write(
                        f"Intrafamily Similarity: {family} ({method_type}, {metric_name})\n"
                    )
                    f.write(
                        f"{'-' * len(f'Intrafamily Similarity: {family} ({method_type}, {metric_name})')}\n\n"
                    )

                    f.write(f"Total pairs: {len(stats.detailed_pairs)}\n")
                    f.write(f"Min similarity: {stats.min:.4f}\n")
                    f.write(f"Max similarity: {stats.max:.4f}\n")
                    f.write(f"Mean similarity: {stats.mean:.4f}\n")
                    f.write(f"Variance: {stats.variance:.4f}\n\n")

                    f.write("Model pairs sorted by similarity (descending):\n")
                    f.write("-" * 80 + "\n")

                    for i, pair_info in enumerate(stats.detailed_pairs, 1):
                        f.write(f"{i}. {pair_info}\n")

                    f.write("\n")

            elif report_type == "interfamily":
                for (family1, family2), stats in sorted(
                    stats_dict.items(), key=lambda x: x[1].mean, reverse=True
                ):
                    f.write(f"\n{'=' * 80}\n")
                    title = f"Interfamily Similarity: {family1} vs {family2} ({method_type}, {metric_name})"
                    f.write(f"{title}\n")
                    f.write(f"{'-' * len(title)}\n\n")

                    f.write(f"Total pairs: {len(stats.detailed_pairs)}\n")
                    f.write(f"Min similarity: {stats.min:.4f}\n")
                    f.write(f"Max similarity: {stats.max:.4f}\n")
                    f.write(f"Mean similarity: {stats.mean:.4f}\n")
                    f.write(f"Variance: {stats.variance:.4f}\n\n")

                    f.write("Model pairs sorted by similarity (descending):\n")
                    f.write("-" * 80 + "\n")

                    for i, pair_info in enumerate(stats.detailed_pairs, 1):
                        f.write(f"{i}. {pair_info}\n")

                    f.write("\n")

            elif report_type == "type_pair":
                for type_pair, stats in sorted(
                    stats_dict.items(), key=lambda x: x[1].mean, reverse=True
                ):
                    f.write(f"\n{'=' * 80}\n")
                    title = f"Type Pair Similarity: {type_pair} ({method_type}, {metric_name})"
                    f.write(f"{title}\n")
                    f.write(f"{'-' * len(title)}\n\n")

                    f.write(f"Total pairs: {len(stats.detailed_pairs)}\n")
                    f.write(f"Min similarity: {stats.min:.4f}\n")
                    f.write(f"Max similarity: {stats.max:.4f}\n")
                    f.write(f"Mean similarity: {stats.mean:.4f}\n")
                    f.write(f"Variance: {stats.variance:.4f}\n\n")

                    f.write("Model pairs sorted by similarity (descending):\n")
                    f.write("-" * 80 + "\n")

                    for i, pair_info in enumerate(stats.detailed_pairs, 1):
                        f.write(f"{i}. {pair_info}\n")

                    f.write("\n")

        return output_path

    def generate_report(self, method_type: str, metric_name: str) -> Dict:
        """
        Generate a comprehensive analysis report with consolidated detailed reports.

        Args:
            method_type: Fingerprinting method type
            metric_name: Similarity metric name

        Returns:
            Dictionary containing report data and plot paths
        """
        report = {
            "method_type": method_type,
            "metric_name": metric_name,
            "plots": {},
            "detailed_reports": {},
            "intrafamily_stats": {},
            "interfamily_stats": {},
            "type_pair_stats": {},
        }

        # 1. Analyze intrafamily similarity
        intrafamily_stats = self.analyze_intrafamily_similarity(
            method_type, metric_name
        )
        if intrafamily_stats:
            plot_path = self.plot_box_whisker(
                intrafamily_stats,
                f"Intrafamily Similarity ({method_type}, {metric_name})",
                "Model Family",
                f"intrafamily_{method_type}_{metric_name}",
            )
            report["plots"]["intrafamily"] = plot_path

            # Generate a single consolidated report
            report_path = os.path.join(
                self.output_dir,
                f"intrafamily_detailed_{method_type}_{metric_name}_{self.timestamp}.txt",
            )
            consolidated_path = self.generate_consolidated_report(
                intrafamily_stats, report_path, method_type, metric_name, "intrafamily"
            )
            report["detailed_reports"]["intrafamily"] = consolidated_path

            # Sort families by mean similarity
            sorted_families = sorted(
                intrafamily_stats.items(), key=lambda x: x[1].mean, reverse=True
            )

            # Format stats for report
            for family, stats in sorted_families:
                report["intrafamily_stats"][family] = {
                    "min": stats.min,
                    "max": stats.max,
                    "mean": stats.mean,
                    "variance": stats.variance,
                    "num_pairs": len(stats.model_pairs),
                }

        # 2. Analyze interfamily similarity
        interfamily_stats = self.analyze_interfamily_similarity(
            method_type, metric_name
        )
        if interfamily_stats:
            # Convert tuple keys to strings for more readable labels
            labeled_stats = {
                f"{fam1} vs {fam2}": stats
                for (fam1, fam2), stats in interfamily_stats.items()
            }

            plot_path = self.plot_box_whisker(
                labeled_stats,
                f"Interfamily Similarity ({method_type}, {metric_name})",
                "Family Pairs",
                f"interfamily_{method_type}_{metric_name}",
            )
            report["plots"]["interfamily"] = plot_path

            # Generate a single consolidated report
            report_path = os.path.join(
                self.output_dir,
                f"interfamily_detailed_{method_type}_{metric_name}_{self.timestamp}.txt",
            )
            consolidated_path = self.generate_consolidated_report(
                interfamily_stats, report_path, method_type, metric_name, "interfamily"
            )
            report["detailed_reports"]["interfamily"] = consolidated_path

            # Sort family pairs by mean similarity
            sorted_pairs = sorted(
                interfamily_stats.items(), key=lambda x: x[1].mean, reverse=True
            )

            # Format stats for report
            for (family1, family2), stats in sorted_pairs:
                key = f"{family1} vs {family2}"
                report["interfamily_stats"][key] = {
                    "min": stats.min,
                    "max": stats.max,
                    "mean": stats.mean,
                    "variance": stats.variance,
                    "num_pairs": len(stats.model_pairs),
                }

        # 3. Analyze type pair similarity
        type_pair_stats = self.analyze_type_pair_similarity(method_type, metric_name)
        if type_pair_stats:
            plot_path = self.plot_box_whisker(
                type_pair_stats,
                f"Type Pair Similarity ({method_type}, {metric_name})",
                "Model Type Pairs",
                f"type_pair_{method_type}_{metric_name}",
            )
            report["plots"]["type_pair"] = plot_path

            # Generate a single consolidated report
            report_path = os.path.join(
                self.output_dir,
                f"type_pair_detailed_{method_type}_{metric_name}_{self.timestamp}.txt",
            )
            consolidated_path = self.generate_consolidated_report(
                type_pair_stats, report_path, method_type, metric_name, "type_pair"
            )
            report["detailed_reports"]["type_pair"] = consolidated_path

            # Sort type pairs by mean similarity
            sorted_type_pairs = sorted(
                type_pair_stats.items(), key=lambda x: x[1].mean, reverse=True
            )

            # Format stats for report
            for type_pair, stats in sorted_type_pairs:
                report["type_pair_stats"][type_pair] = {
                    "min": stats.min,
                    "max": stats.max,
                    "mean": stats.mean,
                    "variance": stats.variance,
                    "num_pairs": len(stats.model_pairs),
                }

        return report
