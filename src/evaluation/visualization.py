"""
DIGITVISION AI — Deep Obsidian Scientific Visualization Engine
==============================================================
Generates publication-quality figures, confusion matrices, reliability curves,
and robustness graphs adhering strictly to the Deep Obsidian visual language:
- Void: #050505, Ground: #0A0A0A, Surface: #121212
- Hairline borders: #262626 / #333333
- Typography: Clean sans-serif / monospace telemetry
- Accent colors: #1DB954 (Green), #FFB000 (Amber), #FF3333 (Red)
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Any, List


# Set global Matplotlib styling for Deep Obsidian
DEEP_OBSIDIAN_STYLE = {
    "figure.facecolor": "#050505",
    "axes.facecolor": "#0A0A0A",
    "axes.edgecolor": "#262626",
    "axes.labelcolor": "#A1A1AA",
    "text.color": "#FFFFFF",
    "xtick.color": "#737373",
    "ytick.color": "#737373",
    "grid.color": "#1A1A1A",
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "font.family": "sans-serif"
}


def apply_deep_obsidian_theme():
    plt.rcParams.update(DEEP_OBSIDIAN_STYLE)


def plot_confusion_matrix(
    cm: np.ndarray,
    model_name: str,
    output_path: str,
    normalize: bool = False
):
    """Plots and saves an Obsidian-styled confusion matrix heatmap."""
    apply_deep_obsidian_theme()
    fig, ax = plt.subplots(figsize=(8, 7), dpi=300)

    if normalize:
        cm_display = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        fmt = '.2f'
    else:
        cm_display = cm
        fmt = 'd'

    # Custom green obsidian colormap
    from matplotlib.colors import LinearSegmentedColormap
    colors = ["#0A0A0A", "#122A1E", "#155734", "#1DB954"]
    cmap = LinearSegmentedColormap.from_list("obsidian_green", colors, N=256)

    sns.heatmap(
        cm_display,
        annot=True,
        fmt=fmt,
        cmap=cmap,
        cbar=True,
        square=True,
        ax=ax,
        linewidths=0.5,
        linecolor="#1A1A1A",
        annot_kws={"size": 9, "weight": "bold", "color": "#FFFFFF"},
        cbar_kws={"shrink": 0.8}
    )

    ax.set_title(f"CONFUSION MATRIX — {model_name.upper()}", fontsize=11, fontweight="bold", pad=15, color="#FFFFFF")
    ax.set_xlabel("PREDICTED DIGIT CLASS", fontsize=9, fontweight="bold", labelpad=10, color="#A1A1AA")
    ax.set_ylabel("TRUE DIGIT CLASS", fontsize=9, fontweight="bold", labelpad=10, color="#A1A1AA")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()


def plot_model_comparison(results: Dict[str, Any], output_path: str):
    """Plots comparative bar charts of Accuracy, F1-Score, and Latency."""
    apply_deep_obsidian_theme()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    models = list(results.keys())
    accuracies = [results[m]["accuracy"] * 100.0 for m in models]
    latencies = [results[m]["latency"]["mean_latency_ms"] for m in models]

    # Bar chart for Accuracy
    bars1 = ax1.barh(models, accuracies, color="#1DB954", height=0.5, edgecolor="#262626", linewidth=1)
    ax1.set_xlim(90.0, 100.0)
    ax1.set_xlabel("TEST ACCURACY (%)", fontsize=9, fontweight="bold", color="#A1A1AA")
    ax1.set_title("TEST ACCURACY COMPARISON", fontsize=11, fontweight="bold", color="#FFFFFF", pad=12)
    ax1.grid(True, axis='x')

    for bar, acc in zip(bars1, accuracies):
        ax1.text(acc + 0.15, bar.get_y() + bar.get_height()/2.0, f"{acc:.2f}%",
                 va='center', ha='left', color='#FFFFFF', fontsize=9, fontweight='bold')

    # Bar chart for Latency
    bars2 = ax2.barh(models, latencies, color="#3B82F6", height=0.5, edgecolor="#262626", linewidth=1)
    ax2.set_xlabel("MEAN INFERENCE LATENCY (MS / SAMPLE)", fontsize=9, fontweight="bold", color="#A1A1AA")
    ax2.set_title("PER-SAMPLE LATENCY PROFILE", fontsize=11, fontweight="bold", color="#FFFFFF", pad=12)
    ax2.grid(True, axis='x')

    for bar, lat in zip(bars2, latencies):
        ax2.text(lat + 0.05, bar.get_y() + bar.get_height()/2.0, f"{lat:.2f} ms",
                 va='center', ha='left', color='#FFFFFF', fontsize=9, fontweight='bold')

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()


def plot_reliability_diagrams(models_data: Dict[str, Any], output_path: str):
    """Plots calibration reliability diagrams (Confidence vs Accuracy) with ECE."""
    apply_deep_obsidian_theme()
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)

    # Perfect calibration reference
    ax.plot([0, 1], [0, 1], linestyle="--", color="#737373", linewidth=1.5, label="Perfect Calibration")

    colors = ["#1DB954", "#3B82F6", "#EC4899", "#EAB308", "#A855F7"]
    for idx, (m_name, m_res) in enumerate(models_data.items()):
        bins = m_res.get("calibration_bins", [])
        if not bins:
            continue
        confs = [b["confidence"] for b in bins if b["sample_count"] > 0]
        accs = [b["accuracy"] for b in bins if b["sample_count"] > 0]
        ece = m_res.get("expected_calibration_error", 0.0)
        c = colors[idx % len(colors)]
        ax.plot(confs, accs, marker="o", markersize=4, linewidth=1.8, color=c,
                label=f"{m_name} (ECE: {ece:.4f})")

    ax.set_title("PROBABILITY CALIBRATION — RELIABILITY DIAGRAM", fontsize=11, fontweight="bold", color="#FFFFFF", pad=15)
    ax.set_xlabel("MEAN PREDICTED CONFIDENCE", fontsize=9, fontweight="bold", color="#A1A1AA")
    ax.set_ylabel("EMPIRICAL ACCURACY", fontsize=9, fontweight="bold", color="#A1A1AA")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True)
    ax.legend(facecolor="#121212", edgecolor="#262626", fontsize=8, loc="lower right")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()


def plot_robustness_curves(robustness_data: Dict[str, Any], output_path: str):
    """Plots robustness degradation curves across 6 corruptions."""
    apply_deep_obsidian_theme()
    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5), dpi=300)
    axes = axes.flatten()

    corr_titles = {
        "gaussian_noise": "Gaussian Additive Noise",
        "rotation": "Rotational Perturbation",
        "affine_shear": "Affine Shear Distortion",
        "stroke_thickness": "Stroke Thickness Alteration",
        "translation": "Centroid Shift / Translation",
        "contrast_attenuation": "Contrast Attenuation"
    }

    colors = ["#1DB954", "#3B82F6", "#EC4899", "#EAB308", "#A855F7"]

    for ax_idx, (corr_key, title) in enumerate(corr_titles.items()):
        ax = axes[ax_idx]
        for m_idx, (m_name, m_res) in enumerate(robustness_data.items()):
            m_corr = m_res.get(corr_key, {})
            if not m_corr:
                continue
            sevs = m_corr.get("severities", [1, 2, 3, 4, 5])
            accs = m_corr.get("accuracies", [])
            ax.plot(sevs, accs, marker="s", markersize=4, linewidth=1.8,
                    color=colors[m_idx % len(colors)], label=m_name)

        ax.set_title(title.upper(), fontsize=10, fontweight="bold", color="#FFFFFF", pad=10)
        ax.set_xlabel("SEVERITY LEVEL (1 -> 5)", fontsize=8, fontweight="bold", color="#A1A1AA")
        ax.set_ylabel("ACCURACY (%)", fontsize=8, fontweight="bold", color="#A1A1AA")
        ax.set_ylim(10.0, 102.0)
        ax.grid(True)
        if ax_idx == 0:
            ax.legend(facecolor="#121212", edgecolor="#262626", fontsize=7, loc="lower left")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
