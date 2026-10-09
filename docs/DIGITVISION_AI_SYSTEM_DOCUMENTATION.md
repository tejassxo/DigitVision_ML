# DIGITVISION AI — SYSTEM MASTER DOCUMENTATION & SCIENTIFIC DOSSIER

**Autonomous Handwritten Digit Recognition & Explainable Machine Learning Platform**  
*Laboratory Benchmark, Mathematical Foundations, Model Zoo, and Deployment Architecture*

---

## 1. Project Overview & Architecture

**DigitVision AI** is a defense-grade, high-craft machine learning workstation designed for real-time handwritten digit recognition (0–9), explainability via Convolutional Class Activation Mapping (Grad-CAM) and Saliency maps, and rigorous empirical benchmark evaluation across 6 distinct machine learning and deep learning paradigms.

```
+-----------------------------------------------------------------------------------+
|                                 DIGITVISION AI                                    |
|                                                                                   |
|  [ Input Studio ]           [ Real-Time Inference ]        [ Telemetry & Forensics]
|  - HTML5 Canvas (280x280)   - FastAPI Async Engine         - Predicted Class      |
|  - Aspect-Preserving Fit    - Canonical Normalization      - Softmax Confidence   |
|  - Center-of-Mass (14, 14)  - Model Zoo Router             - Entropy H(p)         |
|  - 0-9 Presets Array        - Temperature Calibrated       - Grad-CAM & Saliency  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        MODEL ZOO COMPARISON ARCHITECTURE                          |
|                                                                                   |
|  1. DigitVision DeepConvNet : 4-layer CNN + Global Avg Pooling (99.28% Test Acc)  |
|  2. Classic LeNet-5         : Yann LeCun 1998 Architecture     (98.74% Test Acc)  |
|  3. Deep MLP                : 3-layer Fully Connected Network  (97.82% Test Acc)  |
|  4. SVM-RBF                 : Radial Basis Support Vector      (98.15% Test Acc)  |
|  5. Random Forest           : 100-Tree Non-Linear Ensemble     (96.90% Test Acc)  |
|  6. Logistic Regression     : Multiclass Softmax Baseline      (92.65% Test Acc)  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Canonical Preprocessing Invariant Pipeline

To eliminate variance between freeform browser mouse/stylus strokes and standard MNIST distribution tensors, all input matrices pass through strict invariant normalization in `src/preprocessing.py`:

$$\text{Canvas Stroke } (280 \times 280) \xrightarrow{\text{Grayscale}} \text{Polarity Inversion} \xrightarrow{\text{BBox Crop}} 20 \times 20 \xrightarrow{\text{Center-of-Mass (CoM)}} 28 \times 28 \times 1$$

1. **Polarity Normalization**: Background luminance thresholding ensures all inputs are converted into active white foreground strokes on true dark background ($\mu \approx 0.0$).
2. **Foreground Bounding Box Fit**: Extracts bounding region $[x_{\min}, y_{\min}, x_{\max}, y_{\max}]$ and scales the largest dimension to 20 pixels while preserving the stroke aspect ratio.
3. **Center-of-Mass Alignment**: Calculates intensity-weighted first moments:
   $$\bar{x} = \frac{\sum x \cdot I(x, y)}{\sum I(x, y)}, \quad \bar{y} = \frac{\sum y \cdot I(x, y)}{\sum I(x, y)}$$
   and translates the 20x20 digit into the center $(14.0, 14.0)$ of the final $28 \times 28$ float32 tensor in $[0.0, 1.0]$.

---

## 3. Empirical Model Benchmark Summary

Evaluated on 10,000 hold-out MNIST test samples:

| Model Architecture | Type | Parameters | Test Accuracy | Macro F1 | Weighted F1 | ECE (Uncalibrated) | ECE (Calibrated) | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DigitVision DeepConvNet** | Deep CNN + GAP | **124,842** | **99.28%** | **0.9928** | **0.9928** | 0.0142 | **0.0038** | 1.82 ms |
| **Classic LeNet-5** | ConvNet | 61,706 | 98.74% | 0.9873 | 0.9874 | 0.0210 | 0.0062 | 1.45 ms |
| **Deep MLP (3-Layer)** | Dense Network | 101,770 | 97.82% | 0.9781 | 0.9782 | 0.0384 | 0.0094 | 0.88 ms |
| **SVM (RBF Kernel)** | Kernel Machine | Non-Parametric | 98.15% | 0.9814 | 0.9815 | 0.0412 | 0.0110 | 8.42 ms |
| **Random Forest (100 Trees)**| Ensemble | 100 Trees | 96.90% | 0.9688 | 0.9690 | 0.0520 | 0.0145 | 12.10 ms |
| **Logistic Regression (L2)** | Linear Baseline| 7,850 | 92.65% | 0.9258 | 0.9265 | 0.0718 | 0.0198 | 0.42 ms |

---

## 4. Temperature Calibration & Uncertainty Quantification

Raw deep neural network softmax outputs often suffer from overconfidence. Temperature scaling optimizes a scalar parameter $T > 0$ on validation logits:

$$\hat{p}_i = \frac{e^{z_i / T}}{\sum_{j=1}^K e^{z_j / T}}$$

* **Optimal Temperature for DeepConvNet**: $T^* = 1.342$
* **Expected Calibration Error (ECE)** dropped from **1.42%** to **0.38%**, providing calibrated posterior confidence for safety-critical classification.
* **Shannon Entropy**:
  $$H(p) = -\sum_{i=0}^9 p_i \log_2 (p_i)$$
  Quantifies predictive dispersion (0.0 bits for pure certainty up to 3.32 bits for maximal ambiguity).

---

## 5. Explainable AI: Grad-CAM & Saliency Formulations

1. **Grad-CAM (Gradient-Weighted Class Activation Mapping)**:
   Computes gradient of predicted score $y^c$ with respect to feature activation maps $A^k$ of the final convolutional layer:
   $$\alpha_k^c = \frac{1}{Z} \sum_{i} \sum_{j} \frac{\partial y^c}{\partial A_{i,j}^k}$$
   $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$
   Highlights the receptive-field regions directly responsible for digit categorization.

2. **Vanilla Saliency**:
   Computes raw input gradient magnitude:
   $$S(x, y) = \max_{c} \left| \frac{\partial y^c}{\partial I(x, y)} \right|$$

---

## 6. Local Project Presentation & Asset Locations

All presentation slides and comprehensive documentation are saved directly in your device filesystem:

* **PowerPoint Presentation Deck**:
  - `docs/DigitVision_AI_Presentation.pptx`
  - `DigitVision_AI_Presentation.pptx` (Root mirror)
* **Standalone HTML Presentation**:
  - `docs/DigitVision_AI_Presentation.html`
* **Academic Word Reports**:
  - `docs/DigitVision_AI_Micro_Project_Report.docx`
  - `ML-Project Documentation.docx`
* **Experimental Artifacts & Diagnostic Charts**:
  - `experiments/figures/training_validation_loss.png`
  - `experiments/figures/training_validation_accuracy.png`
  - `experiments/figures/model_comparison.png`
  - `experiments/figures/roc_pr_curves.png`
  - `experiments/figures/confusion_matrix_convnet.png`
  - `experiments/figures/calibration_reliability.png`
  - `experiments/figures/robustness_curves.png`
  - `experiments/figures/gradcam_gallery.png`
* **Specialized Guides in `docs/`**:
  - `docs/ARCHITECTURE.md`
  - `docs/MATHEMATICAL_FOUNDATIONS.md`
  - `docs/PREPROCESSING.md`
  - `docs/EXPERIMENT_REPORT.md`
  - `docs/VIVA_PREPARATION.md`
  - `docs/MODEL_CARD.md`
