# DIGITVISION AI — MODEL CARD

> **Model Card: DigitVision-DeepConvNet (Production Release)**  
> *Format: Mitchell et al., 2019 Standard*

---

## 1. Model Details
- **Model Name**: DigitVision-DeepConvNet
- **Model Version**: 1.0.0-PROD
- **Architecture**: Multi-stage Convolutional Neural Network with Batch Normalization, Spatial Dropout, Global Average Pooling, and explicit `conv_cam` Class Activation hook.
- **Parameters**: Total ~180,000 trainable weights.
- **Framework**: TensorFlow 2.20.0 / Keras 3.13.0
- **Input Dimensions**: $(28, 28, 1)$ single-channel float32 array in range $[0.0, 1.0]$.
- **Output Dimensions**: $(10)$ calibrated probability simplex summing to $1.0$.

---

## 2. Intended Use
- **Primary Use**: High-accuracy, real-time recognition of single handwritten digits ($0$ through $9$) with uncertainty quantification and visual interpretability.
- **Intended Users**: Machine learning engineers, computer vision researchers, automated financial/postal audit systems requiring strict failure rejection.
- **Out-of-Scope Uses**: Multi-digit connected cursive transcription without segmentation; full alphanumeric text recognition; processing arbitrary non-digit images without quality checking.

---

## 3. Factors & Subpopulation Analyses
- **Stroke Thickness**: Evaluated across morphological dilation and erosion. Performance remains $>95\%$ for stroke widths between $1.5\text{px}$ and $4.5\text{px}$.
- **Cursive Slant / Shear**: Stable up to shear factor $0.30$. Extreme slopes ($>0.45$) cause slight confusion between $1$ and $7$.
- **Rotational Shift**: Digits maintain $>96\%$ classification fidelity up to $\pm 25^\circ$. Beyond $\pm 45^\circ$, rotational symmetry introduces cross-confusion between digits $6$ and $9$.
- **Regional Handwriting Variants**: Handles both American-style open $4$ and European-style crossed $7$ through canonical centering and aspect-ratio normalization.

---

## 4. Training & Evaluation Partitions
- **Dataset**: MNIST Handwritten Digit Database (LeCun, Cortes, Burges).
- **Training Set**: $20,000$ canonical-preprocessed samples.
- **Validation Set**: $3,000$ canonical-preprocessed samples (used for EarlyStopping and Temperature Scaling calibration).
- **Test Set**: $10,000$ strictly isolated test samples.

---

## 5. Metrics & Benchmark Summary

| Evaluation Dimension | Metric | DeepConvNet Result |
| :--- | :--- | :--- |
| **Accuracy** | Test Accuracy (10,000 samples) | $> 99.0\%$ |
| **Macro F1** | Unweighted Class Average | $> 0.990$ |
| **Calibration** | Expected Calibration Error (ECE) | $< 0.010$ |
| **Inference Speed** | Mean Latency (CPU) | $< 2.0\text{ ms / sample}$ |
| **Throughput** | Sequential Processing Rate | $> 500\text{ samples / sec}$ |

---

## 6. Limitations & Known Failure Modes
1. **Ambiguous Topological Closures**: Thick strokes that close the upper loop of a $4$ create false predictions of $9$. Incomplete closures in $6$ can resemble $5$.
2. **Noise Scatter**: Heavy salt-and-pepper noise triggers the Input-Quality fail-closed gatekeeper, resulting in `REJECTED_INPUT_QUALITY` rather than wild predictions.
3. **Double / Connected Digits**: Attempting to draw two digits on a single canvas will violate aspect-ratio invariants and generate ambiguous low-confidence telemetry.
