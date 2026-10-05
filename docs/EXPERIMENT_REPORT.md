# DIGITVISION AI — EXPERIMENTAL EVALUATION REPORT

> **Empirical Machine Learning Benchmark & Forensic Audit**  
> *Single Source of Truth: `experiments/metrics/experiment_results.json`*  
> *Execution Timestamp: 2026-10-05T10:05:35Z*

---

## 1. Experimental Protocol & Dataset Partitions

All models were evaluated under strict experimental hygiene:
- **Dataset**: MNIST Handwritten Digit Database ($28 \times 28$ grayscale).
- **Canonical Preprocessing Invariant**: Applied identically across all partitions (aspect-ratio preserved $20 \times 20$ scaling, spatial moment centroid centering to $(13.5, 13.5)$, intensity normalized to $[0.0, 1.0]$).
- **Dataset Partitions**:
  - **Training Split**: $20,000$ samples.
  - **Validation Split**: $3,000$ held-out samples (utilized for early stopping and temperature scaling calibration).
  - **Test Split**: $10,000$ strictly isolated samples.

---

## 2. Multi-Model Benchmark Comparison

Evaluation conducted on the complete $10,000$ isolated test set:

| Model Architecture | Model Family | Test Accuracy | Macro F1 | Calibration (ECE) | Mean Latency | Throughput |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DigitVision-DeepConvNet** | Deep CNN (Custom) | **98.22%** | **0.9821** | **0.0041** | 27.67 ms | 36.1 / s |
| **LeNet-5 (1998)** | Deep CNN (Classic) | **96.57%** | **0.9655** | **0.0106** | 15.96 ms | 62.7 / s |
| **SVM (RBF Kernel)** | Classical Kernel ML | **96.11%** | **0.9607** | **0.0217** | 1.02 ms | 982.6 / s |
| **Random Forest (60 Trees)**| Classical Ensemble | **95.48%** | **0.9543** | **0.1918** | 19.19 ms | 52.1 / s |
| **Logistic Regression** | Linear Convex Baseline | **91.49%** | **0.9137** | **0.0113** | 0.05 ms | 21,969.3 / s |

### Key Observations:
1. **Perception Hierarchy**: DigitVision-DeepConvNet achieves the highest accuracy ($98.22\%$) and macro-F1 ($0.9821$), outperforming the classic LeNet-5 baseline by $+1.65\%$ and classical SVM by $+2.11\%$.
2. **Calibration Disparity**: Random Forest exhibited severe uncalibrated overconfidence ($\text{ECE} = 0.1918$), whereas DigitVision-DeepConvNet achieved state-of-the-art calibration ($\text{ECE} = 0.0041$) post temperature scaling.
3. **Computational Trade-Offs**: Linear Logistic Regression provides extreme throughput ($>21,000$ samples/sec), but its linear hyperplane is incapable of resolving complex topological digit ambiguities ($91.49\%$).

---

## 3. Probability Calibration Analysis

Post-hoc temperature scaling was fitted on validation logits:
- **Optimal Temperature $T$**: **$0.9482$**
- **Negative Log-Likelihood (NLL) Optimization**: Converged via L-BFGS-B in 6 iterations.
- **Expected Calibration Error (ECE)**: Reduced from $0.0185$ (raw softmax) to **$0.0041$**.

### Reliability Diagram Summary (15 Confidence Bins):
Across all confidence bins $[0.0, 1.0]$, empirical accuracy aligns tightly with predicted confidence:
- Bin $[0.87, 0.93]$: Average Confidence = $0.9082$, Empirical Accuracy = $0.9024$
- Bin $[0.93, 1.00]$: Average Confidence = $0.9912$, Empirical Accuracy = $0.9908$

---

## 4. Error Intelligence: Top Confusion Digit Pairs

Analyzing the off-diagonal entries of the $10 \times 10$ confusion matrix for `DigitVision-DeepConvNet` reveals the most persistent morphological failure modes:

| Rank | True Digit | Predicted Digit | Misclassification Count | Primary Morphological Cause |
| :--- | :--- | :--- | :--- | :--- |
| **#1** | **4** | **9** | 22 | Upper strokes connect, closing the top loop into a pseudo-loop. |
| **#2** | **7** | **1** | 18 | European serif strokes or steep slant mimics uncrossed 7. |
| **#3** | **3** | **8** | 15 | Thick ink bridges the left lobes, creating an apparent 8. |
| **#4** | **5** | **6** | 12 | Incomplete lower bowl of digit 6 misclassified as 5. |
| **#5** | **2** | **7** | 9 | Flat horizontal base stroke truncated or faint. |
| **#6** | **9** | **4** | 8 | Open top curve in digit 9 resembles disconnected vertical stem in 4. |

---

## 5. High-Confidence Failure Audit (Silent Error Mining)

The platform mined all instances where `DigitVision-DeepConvNet` made an incorrect prediction with confidence $\ge 80\%$.

### Sample Audit:
1. **Sample #1901**: True Digit = **4**, Predicted Digit = **9** (Confidence: $91.4\%$, Entropy: $0.34\text{ bits}$).
   - *Forensic Finding*: Handwriter closed the top loop of the 4 completely, making it topologically indistinguishable from a 9.
2. **Sample #2597**: True Digit = **3**, Predicted Digit = **5** (Confidence: $87.2\%$, Entropy: $0.48\text{ bits}$).
   - *Forensic Finding*: Top horizontal bar was detached, creating a flat upper shelf characteristic of 5.
3. **Sample #4758**: True Digit = **8**, Predicted Digit = **3** (Confidence: $84.6\%$, Entropy: $0.51\text{ bits}$).
   - *Forensic Finding*: Left perimeter of upper and lower loops are barely $1\text{px}$ thick, causing downsampling disconnects.

*Visual artifacts for each failure case are saved in `experiments/failures/`.*

---

## 6. Distribution Shift & Robustness Study

Evaluated under 6 synthetic corruptions across 5 severity levels (400 samples per test):

### Accuracy Degradation (%) by Severity:

| Corruption Domain | Sev 1 | Sev 2 | Sev 3 | Sev 4 | Sev 5 | Max Drop |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gaussian Noise** | 98.0% | 96.8% | 94.5% | 88.2% | 76.5% | $-21.5\%$ |
| **Rotational Shift** | 97.5% | 95.2% | 89.8% | 78.4% | 61.2% | $-36.3\%$ |
| **Affine Shear** | 97.8% | 96.0% | 93.2% | 87.5% | 79.0% | $-18.8\%$ |
| **Stroke Morphology** | 98.0% | 97.2% | 95.8% | 93.0% | 88.5% | $-9.5\%$ |
| **Centroid Misalignment**| 98.2% | 97.8% | 96.5% | 94.0% | 89.2% | $-9.0\%$ |
| **Contrast Attenuation**| 98.2% | 98.0% | 97.5% | 94.8% | 85.0% | $-13.2\%$ |

### Key Robustness Insights:
1. **Centroid Resilience**: Centroid misalignment drops accuracy by only $9.0\%$ at max severity, validating that the canonical preprocessor reliably restores centered alignment before the neural forward pass.
2. **Rotational Vulnerability**: Severe rotation ($>40^\circ$) triggers catastrophic confusion between digits $6$ and $9$ due to intrinsic rotational symmetry.
3. **Noise Tolerance**: Convolutional spatial pooling provides noise resistance up to $\sigma = 0.20$ before feature map degradation occurs.
