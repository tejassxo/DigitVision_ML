# DIGITVISION AI — Final Audit Baseline & Initial Repository State

**Document Version:** 1.0.0  
**Audit Date:** 2026-10-12  
**Auditor:** Principal ML Engineer & Scientific Documentation Auditor  
**Repository:** `tejassxo/DigitVision_ML` (c:\Users\tejas\Desktop\ML_project)  
**Host Environment:** Windows 11, Python 3.13.14  
**Audit Mandate:** Establish ground-truth empirical baseline prior to final documentation release.

---

## 1. Executive Baseline Summary

This baseline audit documents the verified initial state of the DigitVision AI repository prior to final institutional release. The repository contains a fully functional, production-ready machine learning system comprising:
1. An empirical dataset pipeline with local cryptographic caching of the MNIST benchmark.
2. A 7-stage canonical preprocessing engine enforcing spatial, contrast, and centering invariants.
3. A 7-model comparative benchmark spanning zero-rule baselines, convex linear models, kernelized SVMs, decision forest ensembles, multi-layer perceptrons, and convolutional neural networks.
4. An explainable AI (XAI) engine generating pixel-level Grad-CAM attribution heatmaps.
5. A confidence calibration module implementing post-hoc Temperature Scaling and Shannon entropy scoring.
6. A real-time asynchronous FastAPI mission control backend serving an interactive HTML5 canvas interface.
7. An institutional academic project report formatted for Sreyas Institute of Engineering and Technology (CSE AI & ML).

---

## 2. Inventory of Inspected Files & Artifacts

| Component / Subsystem | Primary File Path | Verified Status / Baseline State |
| :--- | :--- | :--- |
| **System Configuration** | `src/config.py` | Centralized constants: dataset paths, SHA-256 hash, split sizes, model hyperparameters. |
| **Dataset Ingestion** | `src/data/dataset.py` | `MNISTPipeline` class; offline `.npz` loader, `verify_integrity()`, `get_reserved_pool()`. |
| **Local Cache** | `data/raw/mnist.npz` | 11,490,434 bytes (10.96 MiB); SHA-256: `731c5ac602752760c8e48fbffcf8c3b850d9dc2a2aedcf2cc48468fc17b673d1`. |
| **Canonical Preprocessing** | `src/preprocessing/canonical.py` | 7-stage invariant: grayscale, Otsu binarization, bbox crop, aspect-resize (20x20), CoM centering (28x28), float32 scaling. |
| **Classical Models** | `src/models/classical.py` | Logistic Regression (L-BFGS), SVM-RBF ($C=1.0$), Random Forest ($n=60$). |
| **Deep Architectures** | `src/models/deep.py` | MLP-Deep (256-128), LeNet-5 (5-layer), DigitVision-DeepConvNet (dual-conv, SpatialDropout, Dense head). |
| **Forensics & Intelligence**| `src/intelligence/forensics.py` | Image stroke metrics: ink density, bounding-box occupancy, aspect ratio, centering offset, contrast. |
| **Explainable AI (XAI)** | `src/xai/gradcam.py` | Grad-CAM gradient backpropagation targeting `conv_cam` layer; ReLU filtering; bilinear interpolation. |
| **Experiment Registry** | `experiments/run_experiments.py` | Automated multi-model execution and metrics recording harness. |
| **Tabular Metrics** | `artifacts/experiment_results.csv` | Empirical benchmark matrix across all 7 models on 10,000 isolated test instances. |
| **Full Telemetry JSON** | `experiments/metrics/experiment_results.json` | Detailed epoch logs, per-class metrics, confusion matrices, latency telemetry, robustness metrics. |
| **Audit CSVs & Figures** | `artifacts/data/` | `dataset_summary.json`, class distribution CSV, partition audit CSV, 4 publication PNG figures. |
| **Automated Test Suite** | `tests/` | 35 unit and integration tests across data, preprocessing, models, API, intelligence, and XAI. |
| **Master Verification** | `verify_all.py` | 5-category integrity validator: tests, model artifacts, figures, presentation sync, report sync. |
| **Institutional Report** | `ML-Project Documentation.docx` | 53 tables, 12 embedded figures, 7,300+ words, 53 pages in Microsoft Word. |
| **Student Viva Guide** | `docs/VIVA_PREPARATION.md` | Viva voce defense questions and answers. |

---

## 3. Dataset Baseline Findings

1. **Curator & Origin:** Modified National Institute of Standards and Technology (MNIST), curated by Yann LeCun and Corinna Cortes (1998) from NIST Special Database 3 and Special Database 19.
2. **Official License:** Creative Commons Attribution-Share Alike 3.0 (CC BY-SA 3.0).
3. **Local Cache Integrity:** Bit-for-bit identical to upstream Google Cloud mirror (`https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz`). Local SHA-256 verified: `731c5ac602752760c8e48fbffcf8c3b850d9dc2a2aedcf2cc48468fc17b673d1`.
4. **Partition Allocation (70,000 Total):**
   - Active Training Set: 20,000 samples (28.57% of corpus; 33.33% of 60k training pool).
   - Validation Set: 3,000 samples (4.29% of corpus; 5.00% of 60k training pool).
   - Reserved Training Pool: 37,000 samples (52.86% of corpus; 61.67% of 60k training pool).
   - Isolated Test Benchmark: 10,000 samples (14.29% of corpus; 100.0% of official test pool).
5. **Leakage & Duplication Verification:** MD5 raster hashes confirmed 0 internal duplicates and 0 cross-split leakage instances. `np.shares_memory` confirmed non-overlapping RAM allocations.

---

## 4. Empirical Model Benchmark Baseline

| Model Identifier | Architecture | Parameters | Test Accuracy | Macro-F1 | Mean Latency (CPU) | Storage Footprint |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **EXP_01_DUMMY_BASELINE** | Most Frequent Class | 0 | 11.35% | 0.0204 | 0.13 ms | 0.00 MB |
| **EXP_02_LOGISTIC_REGRESSION**| Multinomial (L-BFGS) | 7,850 | 91.49% | 0.9137 | 0.06 ms | 0.06 MB |
| **EXP_03_SVM_RBF** | RBF Kernel ($C=1.0$) | — | 96.11% | 0.9607 | 1.73 ms | 15.78 MB |
| **EXP_04_RANDOM_FOREST** | 60 Trees (Ensemble) | — | 95.48% | 0.9543 | 102.09 ms | 26.50 MB |
| **EXP_05_MLP_DEEP** | Dense (256-128-10) | 236,682 | 95.91% | 0.9587 | 3.87 ms | 2.74 MB |
| **EXP_06_LENET_5** | 5-Layer CNN (1998) | 61,706 | 96.25% | 0.9623 | 9.72 ms | 0.75 MB |
| **EXP_07_DIGITVISION_DEEPCONVNET** | Dual-Conv + Dropout | 467,818 | **98.31%** | **0.9831** | **9.14 ms** | 5.41 MB |

*Calibration Metric:* Post-hoc Temperature Scaling converged to $T = 0.9170$, reducing Expected Calibration Error (ECE) from 0.0152 to 0.0031.

---

## 5. Baseline Defects & Inconsistencies Identified

1. **Table 36 (Individual Contributions) Placeholder Contamination:**
   - In `ML-Project Documentation.docx`, Table 36 contained outdated placeholder names (`G. Tejaswi`, `K. Rahul`, `V. Ananya`, `22VE1A6704`) and old roll numbers instead of the official team: M TEJAS YADAV (45%), K Charan Teja (35%), and Y Akshay Raj (20%).
2. **Missing Final Release Document:**
   - The required deliverable `docs/DigitVision_AI_Micro_Project_Report_Final.docx` had not yet been compiled or synchronized.
3. **Viva Preparation Guide Discrepancies:**
   - In `docs/VIVA_PREPARATION.md`, the temperature parameter was stated as $T = 3.972$ (incorrect; empirical truth is $T = 0.9170$).
   - Sample split proportions were listed as percentages of a 33,000 sub-total rather than explicitly accounting for the full 70,000-instance corpus.
   - Saliency and robustness answers lacked verified empirical metrics from the active JSON telemetry.
4. **Epistemic Scope Clarification Required:**
   - Documentation claimed hash checks proved absence of duplication without clarifying that raster byte hashes prove absence of identical rasters and memory leakage, but cannot rule out semantic/perceptual near-duplicates in human handwriting.
5. **Required Deliverable Documents Missing:**
   - `docs/FINAL_AUDIT_BASELINE.md`, `docs/FINAL_REPAIR_LOG.md`, `docs/FINAL_RELEASE_REPORT.md`, and `docs/FACULTY_EXPLANATION.md` were not yet authored.

---

## 6. Baseline Verification Verdict

The core machine learning algorithms, dataset assets, pre-trained weights, and FastAPI application are empirically sound, fully functional, and pass all 35 automated tests. The remaining work is strictly confined to documentation synchronization, defect remediation in metadata tables, and the generation of authoritative academic documentation without touching presentation slides or retraining models.
