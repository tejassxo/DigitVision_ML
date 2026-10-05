# DIGITVISION AI — Scientific Experiment Protocol

**Document Version:** 1.0.0  
**Phase:** 01 — Data Intelligence & Foundation  
**Classification:** Research Engineering Standard  
**Master Registry:** `experiments/metrics/experiment_results.json`  

---

## 1. Scientific Principles & Purpose

The DIGITVISION AI experiment protocol defines the strict empirical methodology governing data partitioning, model evaluation, and benchmark logging. To guarantee publication-grade integrity and eliminate scientific bias:

1. **No Metric Fabrication:** Every reported metric, accuracy figure, latency measurement, or confusion matrix must originate from executable test runs over real tensors.
2. **Strict Test Set Air-Gap:** The 10,000-instance MNIST test set is completely isolated. It is never used for training, feature transformation fitting, threshold tuning, or model selection.
3. **Deterministic Reproducibility:** All pseudorandom generators (Python `random`, `numpy.random`, TensorFlow/Keras seed, scikit-learn random states) are globally locked to `RANDOM_SEED = 42`.
4. **Single Source of Truth:** All experimental findings are serialized into `experiments/metrics/experiment_results.json`. Presentation slides and documentation pull directly from this verified registry.

---

## 2. Partitioning Protocol

```
TOTAL REPOSITORY: 70,000 Instances
├── Training Split (20,000 Instances)      --> Model parameter optimization (Backprop / Fit)
├── Validation Split (3,000 Instances)     --> Hyperparameter tuning, Early stopping, Model checkpointing
└── Isolated Test Set (10,000 Instances)   --> Final one-time benchmark evaluation ONLY
```

### Partition Constraints
- Normalization parameters must strictly be computed on training data or use the static canonical scaling constant ($255.0$).
- Flattened features must maintain identical coordinate indexing as spatial tensors.

---

## 3. Evaluation Metric Definitions

For each model evaluated on the isolated 10,000-sample test set, the following metrics are computed:

### 3.1 Top-1 Classification Accuracy
$$\text{Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\hat{y}_i = y_i)$$

### 3.2 Macro-Averaged Precision, Recall, and F1-Score
For class $k \in \{0, \dots, 9\}$:
$$\text{Precision}_k = \frac{TP_k}{TP_k + FP_k}, \quad \text{Recall}_k = \frac{TP_k}{TP_k + FN_k}$$
$$\text{F1}_k = 2 \cdot \frac{\text{Precision}_k \cdot \text{Recall}_k}{\text{Precision}_k + \text{Recall}_k}$$
$$\text{Macro-F1} = \frac{1}{10} \sum_{k=0}^9 \text{F1}_k$$

### 3.3 Expected Calibration Error (ECE)
Samples are partitioned into $M=10$ confidence bins $B_m \subset (0, 1]$:
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### 3.4 Inference Latency & Efficiency Profiling
- **Inference Latency:** Mean execution time per single-sample forward pass (milliseconds), measured over 1,000 warm iterations on CPU.
- **Model Storage Footprint:** Serialized disk size of model weights in Megabytes (MB).
- **Trainable Parameters:** Total count of learnable weights and biases.

---

## 4. Benchmark Artifact Hierarchy

```
experiments/
├── models/
│   ├── digitvision_convnet.keras    (Deep ConvNet: 98.22% Test Acc)
│   ├── lenet5.keras                 (Classic LeNet-5: 96.57% Test Acc)
│   ├── svm_rbf.joblib               (SVM RBF: 96.11% Test Acc)
│   ├── random_forest.joblib         (Random Forest: 95.48% Test Acc)
│   └── logistic_regression.joblib   (Multinomial Softmax: 91.49% Test Acc)
├── metrics/
│   └── experiment_results.json      (Master JSON Benchmark Record)
├── figures/
│   ├── accuracy_vs_latency.png      (Pareto frontier visualization)
│   ├── confusion_matrix_all.png     (10x10 normalized confusion matrices)
│   └── calibration_curves.png       (Reliability diagrams and ECE)
└── failures/
    └── failure_analysis.json        (Misclassified samples with Grad-CAM overlays)
```

---

## 5. Phase 01 Baseline Benchmark Results

The following verified results were obtained under the Phase 01 execution protocol on the 10,000 isolated test samples:

| Model Architecture | Model Family | Test Accuracy | Macro F1 | Test Loss | Latency (ms) | Parameters | Model Size (MB) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DigitVision Deep ConvNet** | Deep CNN | **98.22%** | **0.9821** | **0.0632** | 2.15 | 450,250 | 1.81 |
| **LeNet-5 (Modernized)** | Classic CNN | 96.57% | 0.9654 | 0.1145 | 1.24 | 61,770 | 0.28 |
| **Support Vector Machine (RBF)** | Kernel Machine | 96.11% | 0.9609 | N/A | 14.80 | N/A | 19.42 |
| **Random Forest (100 Trees)** | Ensemble | 95.48% | 0.9546 | N/A | 3.42 | N/A | 12.18 |
| **Logistic Regression (Softmax)** | Linear Baseline | 91.49% | 0.9138 | 0.3120 | 0.18 | 7,850 | 0.03 |

---

## 6. Reproducibility Checklist

To reproduce this benchmark from scratch:
1. Environment verification: `python --version` (Python $\ge 3.10$), `pip install -r requirements.txt`.
2. Execute data pipeline and EDA: `python -m src.data.eda`.
3. Verify all 33 unit tests pass: `python -m pytest tests -v`.
4. Inspect benchmark registry: `experiments/metrics/experiment_results.json`.
