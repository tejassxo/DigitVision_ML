"""
DIGITVISION AI — System Architecture & Workflow Diagram Generator
Generates high-resolution publication-quality workflow diagrams adhering to Deep Obsidian visual guidelines.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_system_workflow_diagram(output_path="experiments/figures/system_workflow.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    fig.patch.set_facecolor("#050505")
    ax.set_facecolor("#050505")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Title
    ax.text(7, 7.5, "DIGITVISION AI — END-TO-END SYSTEM ARCHITECTURE & DATA WORKFLOW",
            ha="center", va="center", color="#FFFFFF", fontsize=15, fontweight="bold", fontfamily="sans-serif")
    ax.text(7, 7.15, "Unified Canonical Preprocessing | Multi-Model Inference | Temperature Calibration | Forensics | Grad-CAM",
            ha="center", va="center", color="#A1A1AA", fontsize=10, fontfamily="sans-serif")

    stages = [
        {"x": 0.5, "y": 3.8, "w": 2.2, "h": 2.5, "title": "1. USER INPUT", "color": "#1DB954",
         "items": ["Interactive Canvas", "Image Upload (PNG/JPG)", "Touch / Stylus Input", "Raw 280x280 RGB/RGBA"]},
        {"x": 3.1, "y": 3.8, "w": 2.4, "h": 2.5, "title": "2. PREPROCESSING", "color": "#1DB954",
         "items": ["Grayscale Conversion", "Otsu Dynamic Threshold", "Bounding Box Detection", "Aspect-Preserved Resize", "Center-of-Mass Alignment", "28x28 Float32 Tensor"]},
        {"x": 5.9, "y": 3.8, "w": 2.4, "h": 2.5, "title": "3. INFERENCE ENGINE", "color": "#1DB954",
         "items": ["DigitVision DeepConvNet", "Classic LeNet-5 (1998)", "Deep MLP Baseline", "SVM-RBF & Random Forest", "Multinomial Logistic Reg.", "Zero-Rule Dummy Baseline"]},
        {"x": 8.7, "y": 3.8, "w": 2.4, "h": 2.5, "title": "4. INTELLIGENCE & XAI", "color": "#1DB954",
         "items": ["Grad-CAM Saliency Maps", "Temperature Scaling (T)", "Shannon Entropy H(p)", "Digit Forensics Metrics", "Quality Assessment", "Robustness Perturbations"]},
        {"x": 11.5, "y": 3.8, "w": 2.0, "h": 2.5, "title": "5. MISSION CONTROL", "color": "#1DB954",
         "items": ["Real-Time Prediction", "Top-3 Probabilities", "Live Heatmap Overlay", "Telemetry & Latency", "Model Comparison Lab", "REST API & Dashboard"]}
    ]

    for stage in stages:
        rect = patches.FancyBboxPatch((stage["x"], stage["y"]), stage["w"], stage["h"],
                                      boxstyle="round,pad=0.1,rounding_size=0.15",
                                      facecolor="#0A0A0A", edgecolor="#262626", linewidth=1.5)
        ax.add_patch(rect)
        # Header bar
        header_rect = patches.FancyBboxPatch((stage["x"], stage["y"] + stage["h"] - 0.45), stage["w"], 0.45,
                                             boxstyle="round,pad=0.05,rounding_size=0.1",
                                             facecolor="#121212", edgecolor="#262626", linewidth=1)
        ax.add_patch(header_rect)
        ax.text(stage["x"] + stage["w"]/2, stage["y"] + stage["h"] - 0.22, stage["title"],
                ha="center", va="center", color=stage["color"], fontsize=9.5, fontweight="bold")
        
        # Bullets
        for idx, item in enumerate(stage["items"]):
            y_pos = stage["y"] + stage["h"] - 0.75 - (idx * 0.28)
            ax.text(stage["x"] + 0.15, y_pos, f"• {item}",
                    ha="left", va="center", color="#FFFFFF" if idx == 0 else "#A1A1AA",
                    fontsize=8, fontfamily="sans-serif")

    # Connectors
    for i in range(len(stages) - 1):
        x_start = stages[i]["x"] + stages[i]["w"] + 0.05
        x_end = stages[i+1]["x"] - 0.05
        y_mid = 5.0
        ax.annotate("", xy=(x_end, y_mid), xytext=(x_start, y_mid),
                    arrowprops=dict(arrowstyle="-|>", color="#1DB954", lw=2, mutation_scale=15))

    # Bottom Invariant Banner
    banner_rect = patches.FancyBboxPatch((0.5, 0.8), 13.0, 2.3,
                                         boxstyle="round,pad=0.1,rounding_size=0.15",
                                         facecolor="#0A0A0A", edgecolor="#262626", linewidth=1.5)
    ax.add_patch(banner_rect)
    ax.text(7, 2.7, "ARCHITECTURAL INVARIANTS & INTEGRITY GUARANTEES",
            ha="center", va="center", color="#FFFFFF", fontsize=11, fontweight="bold")
    
    invariants = [
        ("Identical Preprocessing Invariant", "Zero training/serving skew: exact same canonical pipeline runs in offline training, unit testing, and real-time live canvas inference."),
        ("Strict Partition Isolation", "10,000 NIST test samples are held strictly isolated; zero leakage into threshold estimation, scaling, or early-stopping decisions."),
        ("Explainability Grounding", "Grad-CAM visualizes convolutional activations at 'conv_cam' layer with rectified guided gradients; zero fabricated attention."),
        ("Probability Calibration", "Post-hoc Temperature Scaling optimizes T on validation logits to minimize Expected Calibration Error (ECE) before confidence display.")
    ]

    for idx, (head, desc) in enumerate(invariants):
        bx = 0.8 + (idx % 2) * 6.2
        by = 2.15 if idx < 2 else 1.35
        ax.text(bx, by, f"✔ {head}:", color="#1DB954", fontsize=9, fontweight="bold")
        ax.text(bx, by - 0.35, desc, color="#A1A1AA", fontsize=8, wrap=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor="#050505", edgecolor="none")
    plt.close()
    print(f"Workflow diagram saved to: {output_path}")

if __name__ == "__main__":
    generate_system_workflow_diagram()
