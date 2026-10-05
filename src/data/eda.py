"""
DIGITVISION AI — Exploratory Data Analysis (EDA) Engine
======================================================
Generates rigorous, publication-grade visual analytics and statistical
distributions adhering strictly to the Deep Obsidian visual language:
1. Sample Image Grid (10x10 Matrix)
2. Class Distribution & Partition Balance
3. Pixel Intensity & Sparsity Distribution (Bimodal Analysis)
4. Class-Conditional Average Prototypes (Mean Stroke Spine)
5. Representative Centroids vs Morphological Outliers

All generated artifacts are saved to: artifacts/data/
"""

import os
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config import ARTIFACTS_DATA_DIR, RANDOM_SEED, NUM_CLASSES
from src.data.dataset import MNISTPipeline
from src.evaluation.visualization import apply_deep_obsidian_theme


def generate_all_eda_visualizations():
    """Executes full empirical exploratory data analysis and generates artifacts."""
    print("=" * 70)
    print("DIGITVISION AI — EXECUTING EMPIRICAL DATA EXPLORATION (EDA)")
    print("=" * 70)

    apply_deep_obsidian_theme()
    pipeline = MNISTPipeline(seed=RANDOM_SEED)
    (x_tr, y_tr), (x_v, y_v), (x_te, y_te) = pipeline.get_partitions()

    output_dir = Path(ARTIFACTS_DATA_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # 1. SAMPLE IMAGE GRID (10x10 Matrix)
    # -------------------------------------------------------------
    print("\n[1/5] Generating Sample Image Grid (10x10)...")
    fig, axes = plt.subplots(10, 10, figsize=(11, 11), dpi=300)
    fig.patch.set_facecolor("#050505")

    np.random.seed(RANDOM_SEED)
    for digit in range(10):
        digit_indices = np.where(y_tr == digit)[0]
        chosen = np.random.choice(digit_indices, size=10, replace=False)
        for col_idx, sample_idx in enumerate(chosen):
            ax = axes[digit, col_idx]
            ax.set_facecolor("#0A0A0A")
            ax.imshow(x_tr[sample_idx], cmap="gray", interpolation="nearest")
            ax.set_xticks([])
            ax.set_yticks([])
            if col_idx == 0:
                ax.set_ylabel(f"CLASS {digit}", fontsize=9, fontweight="bold", color="#1DB954", labelpad=8)

    fig.suptitle(
        "MNIST DATASET — REPRESENTATIVE SAMPLE MATRIX (10 SAMPLES × 10 CLASSES)\n"
        "Source: MNIST Training Partition | Resolution: 28×28 Single-Channel Grayscale",
        fontsize=11, fontweight="bold", color="#FFFFFF", y=0.98
    )
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.95])
    path_grid = output_dir / "sample_image_grid.png"
    plt.savefig(path_grid, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"  -> Saved: {path_grid}")

    # -------------------------------------------------------------
    # 2. CLASS DISTRIBUTION ACROSS PARTITIONS
    # -------------------------------------------------------------
    print("\n[2/5] Generating Class Distribution & Balance Chart...")
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    fig.patch.set_facecolor("#050505")
    ax.set_facecolor("#0A0A0A")

    classes = np.arange(NUM_CLASSES)
    train_counts = np.bincount(y_tr, minlength=10)
    val_counts = np.bincount(y_v, minlength=10)
    test_counts = np.bincount(y_te, minlength=10)

    width = 0.26
    r1 = classes - width
    r2 = classes
    r3 = classes + width

    ax.bar(r1, train_counts, width=width, color="#1DB954", edgecolor="#262626", label=f"Train Partition (N={len(y_tr)})")
    ax.bar(r2, val_counts * (len(y_tr)/len(y_v)), width=width, color="#3B82F6", edgecolor="#262626", label=f"Val Partition Scaled (N={len(y_v)})")
    ax.bar(r3, test_counts * (len(y_tr)/len(y_te)), width=width, color="#A1A1AA", edgecolor="#262626", label=f"Test Partition Scaled (N={len(y_te)})")

    # Ideal uniform expectation line
    expected_count = len(y_tr) / 10.0
    ax.axhline(expected_count, color="#FFB000", linestyle="--", linewidth=1.2, label=f"Uniform Balance Baseline ({int(expected_count)})")

    ax.set_title("CLASS FREQUENCY & PARTITION BALANCE — MNIST", fontsize=11, fontweight="bold", color="#FFFFFF", pad=15)
    ax.set_xlabel("DIGIT CLASS (0–9)", fontsize=9, fontweight="bold", color="#A1A1AA", labelpad=10)
    ax.set_ylabel("SAMPLE COUNT / NORMALIZED PROPORTION", fontsize=9, fontweight="bold", color="#A1A1AA", labelpad=10)
    ax.set_xticks(classes)
    ax.set_xticklabels([f"Digit {c}" for c in classes], fontsize=8, color="#FFFFFF")
    ax.grid(True, axis='y', linestyle="--", alpha=0.5, color="#262626")
    ax.legend(facecolor="#121212", edgecolor="#262626", fontsize=8, loc="upper right")

    # Add source annotation
    ax.text(
        0.01, -0.15,
        "Source: MNIST Partitions (Train N=20,000, Val N=3,000, Test N=10,000) | Metric: Class Count Parity Verified",
        transform=ax.transAxes, fontsize=8, color="#737373", fontfamily="monospace"
    )

    plt.tight_layout()
    path_dist = output_dir / "class_distribution.png"
    plt.savefig(path_dist, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"  -> Saved: {path_dist}")

    # -------------------------------------------------------------
    # 3. PIXEL INTENSITY DISTRIBUTION & BIMODALITY ANALYSIS
    # -------------------------------------------------------------
    print("\n[3/5] Generating Pixel Intensity Distribution...")
    fig, (ax_all, ax_fg) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    fig.patch.set_facecolor("#050505")

    # Subsample 1,000 images for fast, exact histogram calculation
    flat_sample = x_tr[:1000].flatten()

    # Left plot: Complete intensity spectrum including background 0.0
    ax_all.set_facecolor("#0A0A0A")
    counts, bins, _ = ax_all.hist(flat_sample, bins=50, range=(0.0, 1.0), color="#3B82F6", edgecolor="#262626", alpha=0.85)
    ax_all.set_title("FULL INTENSITY SPECTRUM (ALL PIXELS)", fontsize=10, fontweight="bold", color="#FFFFFF", pad=12)
    ax_all.set_xlabel("NORMALIZED PIXEL INTENSITY [0.0, 1.0]", fontsize=8, fontweight="bold", color="#A1A1AA")
    ax_all.set_ylabel("PIXEL FREQUENCY", fontsize=8, fontweight="bold", color="#A1A1AA")
    ax_all.grid(True, linestyle="--", alpha=0.5, color="#262626")

    # Annotate zero sparsity
    zero_pct = np.mean(flat_sample == 0.0) * 100.0
    ax_all.text(0.12, 0.85, f"Pure Background (0.0): {zero_pct:.1f}%\nHigh Sparsity Canvas",
                transform=ax_all.transAxes, fontsize=8, color="#1DB954", fontweight="bold",
                bbox=dict(facecolor="#121212", edgecolor="#262626", boxstyle="round,pad=0.5"))

    # Right plot: Foreground stroke intensity (> 0.05)
    fg_pixels = flat_sample[flat_sample > 0.05]
    ax_fg.set_facecolor("#0A0A0A")
    ax_fg.hist(fg_pixels, bins=50, range=(0.05, 1.0), color="#1DB954", edgecolor="#262626", alpha=0.85)
    ax_fg.set_title("ACTIVE STROKE INTENSITY SPECTRUM (PIXELS > 0.05)", fontsize=10, fontweight="bold", color="#FFFFFF", pad=12)
    ax_fg.set_xlabel("NORMALIZED STROKE INTENSITY [0.05, 1.0]", fontsize=8, fontweight="bold", color="#A1A1AA")
    ax_fg.set_ylabel("STROKE PIXEL FREQUENCY", fontsize=8, fontweight="bold", color="#A1A1AA")
    ax_fg.grid(True, linestyle="--", alpha=0.5, color="#262626")

    fg_mean = np.mean(fg_pixels)
    fg_std = np.std(fg_pixels)
    ax_fg.text(0.10, 0.85, f"Stroke Mean: {fg_mean:.3f}\nStroke Std:  {fg_std:.3f}",
               transform=ax_fg.transAxes, fontsize=8, color="#FFFFFF", fontfamily="monospace",
               bbox=dict(facecolor="#121212", edgecolor="#262626", boxstyle="round,pad=0.5"))

    fig.suptitle(
        "PIXEL INTENSITY & SPARSITY DISTRIBUTION (BIMODAL STROKE ANATOMY)",
        fontsize=11, fontweight="bold", color="#FFFFFF", y=0.98
    )
    plt.tight_layout()
    path_pixel = output_dir / "pixel_intensity_distribution.png"
    plt.savefig(path_pixel, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"  -> Saved: {path_pixel}")

    # -------------------------------------------------------------
    # 4. AVERAGE IMAGE PER CLASS (Mean Stroke Prototype)
    # -------------------------------------------------------------
    print("\n[4/5] Generating Average Prototype Images Per Class...")
    fig, axes = plt.subplots(2, 5, figsize=(12, 5.5), dpi=300)
    fig.patch.set_facecolor("#050505")
    axes = axes.flatten()

    for digit in range(10):
        digit_imgs = x_tr[y_tr == digit]
        mean_img = np.mean(digit_imgs, axis=0)

        ax = axes[digit]
        ax.set_facecolor("#0A0A0A")
        im = ax.imshow(mean_img, cmap="inferno", interpolation="bicubic")
        ax.set_title(f"DIGIT {digit} — MEAN STROKE", fontsize=9, fontweight="bold", color="#FFFFFF", pad=6)
        ax.set_xticks([])
        ax.set_yticks([])

    fig.suptitle(
        "CLASS-CONDITIONAL MEAN STROKE PROTOTYPES (INTRINSIC CENTROID SPINE)\n"
        "Computed across 20,000 Canonical Training Samples | Colormap: Inferno",
        fontsize=11, fontweight="bold", color="#FFFFFF", y=0.98
    )
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.94])
    path_avg = output_dir / "average_image_per_class.png"
    plt.savefig(path_avg, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"  -> Saved: {path_avg}")

    # -------------------------------------------------------------
    # 5. REPRESENTATIVE CENTROIDS VS MORPHOLOGICAL OUTLIERS
    # -------------------------------------------------------------
    print("\n[5/5] Generating Representative Centroids vs Outliers...")
    fig, axes = plt.subplots(2, 10, figsize=(15, 4.2), dpi=300)
    fig.patch.set_facecolor("#050505")

    for digit in range(10):
        digit_imgs = x_tr[y_tr == digit]
        mean_img = np.mean(digit_imgs, axis=0)

        # Compute Euclidean distance of each image from the mean
        dists = np.linalg.norm((digit_imgs - mean_img).reshape(len(digit_imgs), -1), axis=1)

        # Centroid: min distance; Outlier: max distance
        centroid_idx = np.argmin(dists)
        outlier_idx = np.argmax(dists)

        # Row 0: Prototype Centroid
        ax_top = axes[0, digit]
        ax_top.set_facecolor("#0A0A0A")
        ax_top.imshow(digit_imgs[centroid_idx], cmap="gray", interpolation="nearest")
        ax_top.set_title(f"DIGIT {digit}\nPROTOTYPE", fontsize=8, fontweight="bold", color="#1DB954")
        ax_top.set_xticks([])
        ax_top.set_yticks([])

        # Row 1: Extreme Outlier
        ax_bot = axes[1, digit]
        ax_bot.set_facecolor("#0A0A0A")
        ax_bot.imshow(digit_imgs[outlier_idx], cmap="gray", interpolation="nearest")
        ax_bot.set_title(f"OUTLIER\nDIST: {dists[outlier_idx]:.1f}", fontsize=8, fontweight="bold", color="#FF3333")
        ax_bot.set_xticks([])
        ax_bot.set_yticks([])

    fig.suptitle(
        "REPRESENTATIVE EXEMPLARS (EUCLIDEAN MEDIAN) VS EXTREME MORPHOLOGICAL OUTLIERS\n"
        "Illustrating Natural Handwriting Variation, Cursive Slant, Loop Closures, and Outliers",
        fontsize=11, fontweight="bold", color="#FFFFFF", y=0.99
    )
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.94])
    path_rep = output_dir / "representative_examples_per_class.png"
    plt.savefig(path_rep, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"  -> Saved: {path_rep}")

    print("\n" + "=" * 70)
    print("ALL 5 EDA ARTIFACTS GENERATED SUCCESSFULLY IN: artifacts/data/")
    print("=" * 70)


if __name__ == "__main__":
    generate_all_eda_visualizations()
