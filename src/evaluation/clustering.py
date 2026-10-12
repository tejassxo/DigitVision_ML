"""
DIGITVISION AI — Unsupervised K-Means Clustering Analysis (CO5 Alignment)
========================================================================
Implements unsupervised clustering on unlabeled MNIST representations:
1. Fits K-Means (K=10) on 784-dimensional flattened pixel tensors.
2. Evaluates unsupervised cluster inertia, homogeneity, completeness, and silhouette metrics.
3. Computes contingency matrix and cluster-to-digit alignment purity.
4. Generates publication-grade cluster distribution visualization.
"""

import os
import sys
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import (
    homogeneity_score,
    completeness_score,
    v_measure_score,
    adjusted_rand_score
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.config import ARTIFACTS_DATA_DIR, RANDOM_SEED, NUM_CLASSES
from src.data.dataset import MNISTPipeline


def run_kmeans_clustering_experiment(n_samples: int = 10000) -> dict:
    """Executes K-Means unsupervised clustering on MNIST test representations."""
    print("=" * 70)
    print("DIGITVISION AI — EXECUTING K-MEANS UNSUPERVISED CLUSTERING (CO5)")
    print("=" * 70)

    pipeline = MNISTPipeline(seed=RANDOM_SEED)
    _, _, (x_test_flat, y_test) = pipeline.get_flat_features()

    if len(x_test_flat) > n_samples:
        x_eval = x_test_flat[:n_samples]
        y_eval = y_test[:n_samples]
    else:
        x_eval = x_test_flat
        y_eval = y_test

    print(f"Fitting KMeans (K=10) on {len(x_eval)} samples across 784 dimensions...")
    kmeans = KMeans(n_clusters=10, random_state=RANDOM_SEED, n_init=10, max_iter=300)
    cluster_labels = kmeans.fit_predict(x_eval)

    # Compute Clustering Metrics
    homo = float(homogeneity_score(y_eval, cluster_labels))
    comp = float(completeness_score(y_eval, cluster_labels))
    v_meas = float(v_measure_score(y_eval, cluster_labels))
    ari = float(adjusted_rand_score(y_eval, cluster_labels))
    inertia = float(kmeans.inertia_)

    # Cluster Purity and Majority Mapping
    contingency = np.zeros((10, 10), dtype=int)
    for true_label, cluster_idx in zip(y_eval, cluster_labels):
        contingency[cluster_idx, true_label] += 1

    cluster_mappings = {}
    total_correct_purity = 0
    for c_idx in range(10):
        majority_digit = int(np.argmax(contingency[c_idx]))
        majority_count = int(contingency[c_idx, majority_digit])
        cluster_total = int(np.sum(contingency[c_idx]))
        purity = float(majority_count / cluster_total) if cluster_total > 0 else 0.0
        cluster_mappings[c_idx] = {
            "assigned_digit": majority_digit,
            "majority_count": majority_count,
            "cluster_size": cluster_total,
            "purity": round(purity, 4)
        }
        total_correct_purity += majority_count

    overall_purity = float(total_correct_purity / len(y_eval))

    results = {
        "algorithm": "K-Means Clustering",
        "library": "scikit-learn (sklearn.cluster.KMeans)",
        "num_clusters": 10,
        "sample_count": len(x_eval),
        "dimension": 784,
        "inertia": round(inertia, 2),
        "homogeneity_score": round(homo, 4),
        "completeness_score": round(comp, 4),
        "v_measure": round(v_meas, 4),
        "adjusted_rand_index": round(ari, 4),
        "overall_cluster_purity": round(overall_purity, 4),
        "cluster_mappings": cluster_mappings
    }

    # Save Results JSON
    output_dir = Path(ARTIFACTS_DATA_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "kmeans_clustering_analysis.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {json_path}")

    # Generate Cluster Centroid Visualization
    fig, axes = plt.subplots(2, 5, figsize=(12, 5.5), dpi=300)
    fig.patch.set_facecolor("#050505")
    axes = axes.flatten()

    for c_idx in range(10):
        center_img = kmeans.cluster_centers_[c_idx].reshape(28, 28)
        mapped = cluster_mappings[c_idx]
        ax = axes[c_idx]
        ax.set_facecolor("#0A0A0A")
        ax.imshow(center_img, cmap="viridis", interpolation="bicubic")
        ax.set_title(
            f"Cluster {c_idx} -> Digit {mapped['assigned_digit']}\nPurity: {mapped['purity']*100:.1f}% (N={mapped['cluster_size']})",
            fontsize=8, fontweight="bold", color="#FFFFFF", pad=6
        )
        ax.set_xticks([])
        ax.set_yticks([])

    fig.suptitle(
        "K-MEANS (K=10) UNSUPERVISED CLUSTER CENTROIDS — MNIST LATENT SPACE\n"
        f"Evaluated on {len(x_eval)} Samples | Overall Purity: {overall_purity*100:.2f}% | V-Measure: {v_meas:.4f}",
        fontsize=11, fontweight="bold", color="#FFFFFF", y=0.98
    )
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.94])
    plot_path = output_dir / "kmeans_cluster_distribution.png"
    plt.savefig(plot_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Cluster centroids plot saved to: {plot_path}")

    return results


if __name__ == "__main__":
    run_kmeans_clustering_experiment()
