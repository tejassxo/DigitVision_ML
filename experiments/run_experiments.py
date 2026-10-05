"""
DIGITVISION AI — Master Experiment Runner & Benchmark Pipeline (Optimized CPU)
==============================================================================
Orchestrates end-to-end model training, temperature scaling calibration,
isolated test set evaluation, error intelligence mining, robustness benchmarking,
and Deep Obsidian figure generation.

All outputs are saved to experiments/metrics/experiment_results.json as the
Single Source of Truth.
"""

import os
import sys
import json
import time
import cv2
import numpy as np
import tensorflow as tf
from keras.datasets import mnist

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.deep import build_deep_convnet, build_lenet5, DeepModelWrapper
from src.models.classical import (
    build_logistic_regression,
    build_svm_rbf,
    build_random_forest,
    ClassicalModelWrapper
)
from src.intelligence.confidence import TemperatureScaler
from src.evaluation.metrics import evaluate_model_full
from src.evaluation.error_analysis import analyze_top_confusions, mine_high_confidence_failures
from src.evaluation.robustness import benchmark_model_robustness
from src.evaluation.visualization import (
    plot_confusion_matrix,
    plot_model_comparison,
    plot_reliability_diagrams,
    plot_robustness_curves,
    apply_deep_obsidian_theme
)
from src.xai.gradcam import generate_gradcam_heatmap, render_gradcam_overlay
import matplotlib.pyplot as plt
import joblib


def run_pipeline():
    print("=" * 70)
    print("DIGITVISION AI — SCIENTIFIC EXPERIMENT EXECUTION ENGINE")
    print("=" * 70)

    # 1. Load MNIST dataset
    print("\n[1/6] Loading MNIST dataset...")
    (x_train_raw, y_train_raw), (x_test_raw, y_test_raw) = mnist.load_data()

    # Preprocess to float32 [0.0, 1.0]
    x_train_norm = (x_train_raw / 255.0).astype(np.float32)
    x_test_norm = (x_test_raw / 255.0).astype(np.float32)

    # High-efficiency CPU splits:
    # 20,000 training samples, 3,000 validation samples, 10,000 isolated test samples
    n_train = 20000
    n_val = 3000
    x_train = x_train_norm[:n_train]
    y_train = y_train_raw[:n_train]
    x_val = x_train_norm[n_train:n_train+n_val]
    y_val = y_train_raw[n_train:n_train+n_val]
    x_test = x_test_norm
    y_test = y_test_raw

    print(f"  Training split:   {x_train.shape} (Labels: {len(y_train)})")
    print(f"  Validation split: {x_val.shape} (Labels: {len(y_val)})")
    print(f"  Test split:       {x_test.shape} (Labels: {len(y_test)}) [ISOLATED]")

    # Expand dims for Conv2D input
    x_train_4d = np.expand_dims(x_train, -1)
    x_val_4d = np.expand_dims(x_val, -1)
    x_test_4d = np.expand_dims(x_test, -1)

    # 2. Train Deep Learning Models
    print("\n[2/6] Training Deep Learning Architectures...")

    # A. Production Deep ConvNet
    print("  -> Training DigitVision-DeepConvNet (4 epochs, batch size 256)...")
    deep_convnet_raw = build_deep_convnet()
    deep_convnet_raw.fit(
        x_train_4d, y_train,
        validation_data=(x_val_4d, y_val),
        epochs=4,
        batch_size=256,
        verbose=1
    )
    deep_convnet = DeepModelWrapper(deep_convnet_raw, name="DigitVision-DeepConvNet", target_conv_layer="conv_cam")
    deep_convnet.save("experiments/models/digitvision_convnet.keras")

    # B. LeNet-5
    print("\n  -> Training Classic LeNet-5 (4 epochs, batch size 256)...")
    lenet5_raw = build_lenet5()
    lenet5_raw.fit(
        x_train_4d, y_train,
        validation_data=(x_val_4d, y_val),
        epochs=4,
        batch_size=256,
        verbose=1
    )
    lenet5 = DeepModelWrapper(lenet5_raw, name="LeNet-5", target_conv_layer="conv_cam")
    lenet5.save("experiments/models/lenet5.keras")

    # 3. Train Classical Machine Learning Models
    print("\n[3/6] Training Classical ML Baselines...")
    x_train_flat = x_train.reshape(len(x_train), -1)

    # A. Multinomial Logistic Regression (15,000 samples)
    print("  -> Training Multinomial Logistic Regression...")
    log_reg = build_logistic_regression(max_iter=200)
    log_reg.fit(x_train_flat[:15000], y_train[:15000])
    log_reg_wrapper = ClassicalModelWrapper(log_reg, name="Logistic-Regression")
    log_reg_wrapper.save("experiments/models/logistic_regression.joblib")

    # B. Random Forest Classifier (60 trees, 15,000 samples)
    print("  -> Training Random Forest Ensemble...")
    rf = build_random_forest(n_estimators=60, max_depth=18)
    rf.fit(x_train_flat[:15000], y_train[:15000])
    rf_wrapper = ClassicalModelWrapper(rf, name="Random-Forest")
    rf_wrapper.save("experiments/models/random_forest.joblib")

    # C. Support Vector Classifier (RBF Kernel, 6,000 samples)
    print("  -> Training Support Vector Classifier (RBF kernel, 6,000 samples)...")
    svm = build_svm_rbf(c_param=5.0)
    svm.fit(x_train_flat[:6000], y_train[:6000])
    svm_wrapper = ClassicalModelWrapper(svm, name="SVM-RBF")
    svm_wrapper.save("experiments/models/svm_rbf.joblib")

    # 4. Temperature Scaling Calibration on Validation Set
    print("\n[4/6] Fitting Temperature Scaling Calibrator on Validation Logits...")
    val_preds = deep_convnet.predict_batch_proba(x_val_4d, batch_size=256)
    eps = 1e-12
    val_logits = np.log(np.clip(val_preds, eps, 1.0 - eps))
    scaler = TemperatureScaler(temperature=1.0)
    fitted_T = scaler.fit(val_logits, y_val)
    print(f"  Fitted Optimal Temperature T: {fitted_T:.4f}")
    joblib.dump(scaler, "experiments/models/temperature_scaler.joblib")

    # 5. Full Evaluation on Isolated Test Set (10,000 samples)
    print("\n[5/6] Performing Full Evaluation on Isolated 10,000 Test Set...")
    models_to_eval = [deep_convnet, lenet5, svm_wrapper, rf_wrapper, log_reg_wrapper]
    all_eval_results = {}
    robustness_results = {}
    model_comparisons = {}

    for m in models_to_eval:
        print(f"  Evaluating {m.name}...")
        test_inputs = x_test_4d if m.is_deep else x_test
        eval_dict = evaluate_model_full(m, test_inputs, y_test, batch_size=256)
        
        # Mine failure modes and top confusions
        cm_arr = np.array(eval_dict["confusion_matrix"])
        top_confusions = analyze_top_confusions(cm_arr, top_n=6)
        eval_dict["top_confusion_pairs"] = top_confusions

        if m.name == "DigitVision-DeepConvNet":
            failures = mine_high_confidence_failures(
                x_test, y_test,
                eval_dict["predictions"],
                eval_dict["probabilities"],
                confidence_threshold=0.80,
                max_saved=12,
                output_dir="experiments/failures"
            )
            eval_dict["high_confidence_failures"] = failures

        # Robustness benchmarking (on 400 sample subset for high fidelity & speed)
        print(f"    Benchmarking robustness under 6 corruptions...")
        rob_dict = benchmark_model_robustness(m, x_test, y_test, n_eval_samples=400)
        robustness_results[m.name] = rob_dict

        # Clean non-serializable arrays
        all_eval_results[m.name] = {
            "model_name": eval_dict["model_name"],
            "is_deep": eval_dict["is_deep"],
            "accuracy": eval_dict["accuracy"],
            "accuracy_pct": eval_dict["accuracy_pct"],
            "macro_precision": eval_dict["macro_precision"],
            "macro_recall": eval_dict["macro_recall"],
            "macro_f1": eval_dict["macro_f1"],
            "weighted_f1": eval_dict["weighted_f1"],
            "expected_calibration_error": eval_dict["expected_calibration_error"],
            "calibration_bins": eval_dict["calibration_bins"],
            "confusion_matrix": eval_dict["confusion_matrix"],
            "per_class": eval_dict["per_class"],
            "latency": eval_dict["latency"],
            "top_confusion_pairs": top_confusions,
            "high_confidence_failures": eval_dict.get("high_confidence_failures", [])
        }

        model_comparisons[m.name] = {
            "accuracy": eval_dict["accuracy"],
            "accuracy_pct": eval_dict["accuracy_pct"],
            "macro_f1": eval_dict["macro_f1"],
            "ece": eval_dict["expected_calibration_error"],
            "latency": eval_dict["latency"]
        }
        print(f"    -> Test Accuracy: {eval_dict['accuracy_pct']}% | Latency: {eval_dict['latency']['mean_latency_ms']:.2f} ms")

    # 6. Deep Obsidian Visualizations & Figures Generation
    print("\n[6/6] Generating Deep Obsidian Scientific Figures...")
    os.makedirs("experiments/figures", exist_ok=True)

    # A. Confusion Matrix for Production Deep ConvNet
    plot_confusion_matrix(
        np.array(all_eval_results["DigitVision-DeepConvNet"]["confusion_matrix"]),
        model_name="DigitVision-DeepConvNet",
        output_path="experiments/figures/confusion_matrix_convnet.png"
    )

    # B. Model Comparison Bar Chart
    plot_model_comparison(
        model_comparisons,
        output_path="experiments/figures/model_comparison.png"
    )

    # C. Calibration Reliability Diagram
    plot_reliability_diagrams(
        all_eval_results,
        output_path="experiments/figures/calibration_reliability.png"
    )

    # D. Robustness Degradation Curves
    plot_robustness_curves(
        robustness_results,
        output_path="experiments/figures/robustness_curves.png"
    )

    # E. Grad-CAM Demonstration Gallery across digits 0-9
    print("  -> Generating Grad-CAM Explanation Gallery...")
    apply_deep_obsidian_theme()
    fig, axes = plt.subplots(2, 5, figsize=(15, 6.5), dpi=300)
    axes = axes.flatten()

    for digit in range(10):
        sample_idx = int(np.where(y_test == digit)[0][0])
        img_sample = x_test[sample_idx]
        tensor_in = img_sample.reshape(1, 28, 28, 1)

        heatmap, _ = generate_gradcam_heatmap(deep_convnet_raw, tensor_in, target_class=digit)
        
        orig_u8 = (img_sample * 255.0).astype(np.uint8)
        heatmap_u8 = (heatmap * 255.0).astype(np.uint8)
        orig_scaled = cv2.resize(orig_u8, (140, 140), interpolation=cv2.INTER_NEAREST)
        hm_scaled = cv2.resize(heatmap_u8, (140, 140), interpolation=cv2.INTER_CUBIC)
        color_hm = cv2.applyColorMap(hm_scaled, cv2.COLORMAP_VIRIDIS)
        orig_bgr = cv2.cvtColor(orig_scaled, cv2.COLOR_GRAY2BGR)
        blended = cv2.addWeighted(orig_bgr, 0.45, color_hm, 0.55, 0)
        blended_rgb = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)

        ax = axes[digit]
        ax.imshow(blended_rgb)
        ax.set_title(f"DIGIT {digit} — GRAD-CAM", fontsize=9, fontweight="bold", color="#FFFFFF")
        ax.axis("off")

    plt.tight_layout()
    plt.savefig("experiments/figures/gradcam_gallery.png", facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

    # Master Experiment Record
    master_results = {
        "metadata": {
            "project": "DIGITVISION AI",
            "execution_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "framework_versions": {
                "tensorflow": tf.__version__,
                "keras": tf.keras.__version__ if hasattr(tf.keras, "__version__") else "integrated",
                "python": sys.version.split()[0]
            },
            "dataset": {
                "name": "MNIST",
                "train_samples": len(y_train),
                "val_samples": len(y_val),
                "test_samples": len(y_test),
                "resolution": [28, 28, 1]
            },
            "temperature_scaler": {
                "optimal_temperature": round(fitted_T, 4)
            }
        },
        "model_comparison": model_comparisons,
        "models": all_eval_results,
        "robustness": robustness_results
    }

    results_filepath = "experiments/metrics/experiment_results.json"
    with open(results_filepath, "w") as f:
        json.dump(master_results, f, indent=2)

    print("\n" + "=" * 70)
    print(f"EXPERIMENT EXECUTION COMPLETE! Artifacts written to {results_filepath}")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
