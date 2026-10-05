# DIGITVISION AI — ARCHITECTURAL SPECIFICATION

> **Explainable, Confidence-Aware Handwritten Digit Intelligence Platform**  
> *Production Machine Learning System Architecture & Diagnostic Telemetry Pipeline*

---

## 1. System Overview

DIGITVISION AI is an advanced, production-grade computer vision platform engineered to eliminate silent machine-learning failures in handwritten digit recognition. By combining multi-stage deep convolutional networks, classical learning baselines, post-hoc uncertainty calibration, input-quality pre-flight checks, and visual explainability (Grad-CAM & Saliency), the platform guarantees safe, deterministic, and auditable inference.

```
                              RAW STROKE INPUT
                    (Canvas Base64 / Scanned PNG / Vector)
                                      │
                                      ▼
                        CANONICAL PREPROCESSING INVARIANT
                 [Contrast Inversion -> Bbox -> 20x20 Centroid]
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
               INPUT-QUALITY INTELLIGENCE   MODEL FORWARD PASS
               • Stroke Pixel Density        • DigitVision DeepConvNet
               • Speckle Noise Ratio         • Classic LeNet-5
               • Centroid Deviation Offset   • Classical Baselines (SVM/RF/LR)
               • Laplacian Sharpness Score         │
                         │                         ▼
                         │               POST-HOC CALIBRATION
                         │               • Temperature Scaling (T)
                         │               • Shannon Entropy H(p)
                         │               • Top-1/Top-2 Margin
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                           DECISION & AUDIT ROUTER
                   ┌──────────────────┼──────────────────┐
                   ▼                  ▼                  ▼
             HIGH CONFIDENCE   MODERATE CONFIDENCE   AMBIGUOUS / OOD
                [#1DB954]          [#FFB000]            [#FF3333]
                   │
                   ▼
       EXPLAINABLE AI ENGINE
       • Grad-CAM Heatmap (conv_cam)
       • Pixel Gradient Saliency
                   │
                   ▼
     DIGIT FORENSICS TELEMETRY PAYLOAD
```

---

## 2. Architectural Invariants

The platform enforces strict architectural invariants across the entire software lifecycle:

1. **Shared Canonical Preprocessing Invariant**: Offline training, validation splits, and real-time live canvas inference share the exact same `canonical_preprocess()` routine in `src/preprocessing/canonical.py`. Divergent preprocessing implementations are prohibited.
2. **Isolation of Evaluation Partition**: The 10,000-sample MNIST test set remains strictly quarantined; it is never touched during hyperparameter tuning or early stopping.
3. **Fail-Closed Input Quality**: Blanks, fragmented strokes, and extreme noise are caught and rejected prior to model evaluation, preventing uncalibrated wild guesses on garbage inputs.
4. **Single Source of Truth**: All numerical figures, calibration errors, and latency records originate strictly from `experiments/metrics/experiment_results.json`. No hardcoded or fabricated metrics are permitted in documentation or presentation decks.

---

## 3. Canonical Preprocessing Pipeline

To ensure invariance to translation, scaling, and contrast, raw images are processed through six sequential transformations:

$$\mathbf{I}_{\text{raw}} \xrightarrow{\text{Decode}} \mathbf{I}_{\text{gray}} \xrightarrow{\text{Contrast}} \mathbf{I}_{\text{norm}} \xrightarrow{\text{BBox}} \mathbf{I}_{\text{crop}} \xrightarrow{\text{Scale}} \mathbf{I}_{20\times 20} \xrightarrow{\text{Centroid}} \mathbf{I}_{28\times 28} \in [0.0, 1.0]^{28\times 28}$$

### Step-by-Step Transformations:

1. **Input Ingestion & Color Normalization**: Ingests RGBA/RGB/Grayscale data from Base64 or numpy arrays. Inverts bright background paper/canvas so strokes are represented by positive non-zero intensity.
2. **Bounding Box Extraction**: Computes active foreground pixels via thresholding:
   $$\mathcal{F} = \{(x, y) \mid \mathbf{I}(x, y) > \theta\}$$
   Extracts minimal enclosing bounding box $[x_{\min}, y_{\min}, w, h]$.
3. **Aspect-Ratio Preserved Rescaling**: Computes scale factor $s = \frac{20}{\max(w, h)}$. Resizes the digit patch to $(w \cdot s, h \cdot s)$ using area anti-aliasing interpolation (`cv2.INTER_AREA`).
4. **Centroid Alignment via Spatial Moments**: Places resized digit into a blank $28\times 28$ canvas and computes the intensity-weighted center of mass:
   $$\bar{x} = \frac{\sum_{x, y} x \cdot \mathbf{I}(x, y)}{\sum_{x, y} \mathbf{I}(x, y)}, \quad \bar{y} = \frac{\sum_{x, y} y \cdot \mathbf{I}(x, y)}{\sum_{x, y} \mathbf{I}(x, y)}$$
5. **Affine Translation**: Applies translation matrix $\mathbf{M} = \begin{bmatrix} 1 & 0 & 13.5 - \bar{x} \\ 0 & 1 & 13.5 - \bar{y} \end{bmatrix}$ such that the center of mass aligns exactly with the optical frame center $(13.5, 13.5)$.
6. **Float32 Normalization**: Clips intensities strictly to $[0.0, 1.0]$.

---

## 4. Model Architecture Hierarchy

### A. Production Model: DigitVision-DeepConvNet

A modern deep convolutional neural network designed with explicit layer hooks for Grad-CAM interpretability:

| Stage | Layer Type | Specifications | Output Shape | Activation |
| :--- | :--- | :--- | :--- | :--- |
| **Input** | InputCanvas | Grayscale single-channel | $(28, 28, 1)$ | — |
| **Block 1** | Conv2D + BN | 32 filters, $3\times 3$, padding='same' | $(28, 28, 32)$ | ReLU |
| | Conv2D + BN | 32 filters, $3\times 3$, padding='same' | $(28, 28, 32)$ | ReLU |
| | MaxPooling2D | $2\times 2$ pool, stride 2 | $(14, 14, 32)$ | — |
| | Spatial Dropout | Rate = 0.25 | $(14, 14, 32)$ | — |
| **Block 2** | Conv2D + BN | 64 filters, $3\times 3$, padding='same' | $(14, 14, 64)$ | ReLU |
| | **Conv2D + BN (`conv_cam`)** | **64 filters, $3\times 3$, padding='same'** | **$(14, 14, 64)$** | **ReLU** |
| | MaxPooling2D | $2\times 2$ pool, stride 2 | $(7, 7, 64)$ | — |
| | Spatial Dropout | Rate = 0.25 | $(7, 7, 64)$ | — |
| **Block 3** | Conv2D + BN | 128 filters, $3\times 3$, padding='same' | $(7, 7, 128)$ | ReLU |
| | Dropout | Rate = 0.30 | $(7, 7, 128)$ | — |
| **Classifier** | GlobalAveragePooling2D | Spatial reduction | $(128)$ | — |
| | Dense + BN | 128 units | $(128)$ | ReLU |
| | Dropout | Rate = 0.40 | $(128)$ | — |
| | Dense (Output) | 10 units | $(10)$ | Softmax |

*Note: Layer `conv_cam` is the designated target layer for Class Activation Mapping.*

### B. Classic Baseline: LeNet-5 (LeCun et al., 1998)
Historical benchmark consisting of:
- `Conv2D(6, 5x5)` $\to$ `AvgPool(2x2)` $\to$ `Conv2D(16, 5x5)` $\to$ `AvgPool(2x2)` $\to$ `Dense(120)` $\to$ `Dense(84)` $\to$ `Dense(10)`.

### C. Classical Machine Learning Baselines
Ingest 784-dimensional flattened canonical pixel vectors:
- **Support Vector Classifier (RBF Kernel)**: Non-linear decision hyperplane with $C=5.0$, calibrated Platt probabilities.
- **Random Forest Ensemble**: 60 randomized decision trees with maximum depth 18.
- **Multinomial Logistic Regression**: Convex linear softmax baseline regularized with L2 penalty ($C=1.0$).

---

## 5. Decision & Uncertainty Calibration Framework

To avoid overconfident silent errors, raw softmax outputs are calibrated post-hoc:

1. **Temperature Scaling**: Softmax logits $z$ are scaled by an optimized scalar $T > 0$:
   $$q_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$$
   $T$ is fitted on the validation set by minimizing negative log-likelihood (NLL).
2. **Shannon Predictive Entropy**:
   $$H(p) = -\sum_{i=0}^9 p_i \log_2(p_i + \epsilon) \quad \in [0, 3.3219] \text{ bits}$$
3. **Prediction Margin**:
   $$M = p_{(1)} - p_{(2)}$$

### Decision Boundary Protocol:
- **`ACCEPTED_HIGH_CONFIDENCE`** (Theme: `#1DB954`):
  $p_{(1)} \ge 0.85 \quad \land \quad M \ge 0.60 \quad \land \quad H(p) \le 0.80\text{ bits}$
- **`ACCEPTED_MODERATE_CONFIDENCE`** (Theme: `#FFB000`):
  $0.50 \le p_{(1)} < 0.85 \quad \land \quad M \ge 0.20$
- **`FLAGGED_AMBIGUOUS_DISTRIBUTION`** (Theme: `#FF3333`):
  $p_{(1)} < 0.50 \quad \lor \quad M < 0.20 \quad \lor \quad H(p) > 1.80\text{ bits}$
- **`REJECTED_INPUT_QUALITY`** (Theme: `#FF3333`):
  Fails input-quality checks prior to forward pass.

---

## 6. Visual Explainability Pipeline

1. **Grad-CAM**: Evaluates the gradient of the predicted class score $y^c$ with respect to feature activation maps $A^k$ at layer `conv_cam`:
   $$\alpha_k^c = \frac{1}{Z} \sum_{i} \sum_{j} \frac{\partial y^c}{\partial A_{i, j}^k}$$
   $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left( \sum_k \alpha_k^c A^k \right)$$
   The resulting $14\times 14$ map is bilinearly upsampled to $28\times 28$, normalized to $[0, 1]$, and blended with the input digit using a Viridis colormap.
2. **Pixel Saliency**: Computes input pixel attribution $\mathbf{S}_{i, j} = \max_c \left| \frac{\partial y^c}{\partial \mathbf{X}_{i, j}} \right|$, highlighting the exact stroke contours driving activation.
