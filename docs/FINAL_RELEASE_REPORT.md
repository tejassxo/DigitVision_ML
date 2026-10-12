# DIGITVISION AI — Final Documentation Release & Scientific Integrity Report

**Release Status:** **APPROVED FOR INSTITUTIONAL SUBMISSION**  
**Release Date:** 2026-10-12  
**Institutional Department:** Department of Computer Science & Engineering (AI & ML)  
**Institution:** Sreyas Institute of Engineering and Technology, Hyderabad  
**Regulation & Course:** B.Tech R22 | CS501PC: Machine Learning Micro Project  
**Authoring Team:**
1. M TEJAS YADAV (Roll No. 24VE1A6695, 45% contribution — Lead Architect & Deep Learning Engineer)
2. K Charan Teja (Roll No. 24VE1A6692, 35% contribution — ML Engineer & Statistical Analyst)
3. Y Akshay Raj (Roll No. 24VE1A66C8, 20% contribution — Full-Stack & Telemetry Engineer)

---

## 1. Executive Summary & Verification Verdict

The DigitVision AI platform has undergone a comprehensive scientific documentation audit, empirical reproducibility check, and institutional formatting review. All code, data assets, model artifacts, telemetry files, and report documents have been synchronized with zero synthetic fabrication.

### Core Release Highlights:
* **Academic Report Finalized:** `docs/DigitVision_AI_Micro_Project_Report_Final.docx` compiled with complete front matter, Course Outcomes (CO1–CO6), Program Outcomes (PO1–PO11 from New POs.pdf), Bloom's Taxonomy mapping, Chapters 1 through 9, 53 tables, 12 embedded figures, and Appendices A–C.
* **Student Team Metadata Aligned:** Front matter and Table 36 (Individual Contributions) synchronized with verified names, roll numbers, percentage contributions (45%, 35%, 20%), and modular engineering responsibilities.
* **Cryptographic Dataset Provenance:** Verified bit-for-bit against upstream distribution via SHA-256 digest (`731c5ac602752760...`), cached locally at `data/raw/mnist.npz` (10.96 MiB), and confirmed under Creative Commons Attribution-Share Alike 3.0 (CC BY-SA 3.0).
* **Partition Accounting Complete:** The 70,000-instance MNIST population is accounted for: 20,000 active train (28.57%), 3,000 validation (4.29%), 37,000 reserved train pool (52.86%), and 10,000 air-gapped test benchmark (14.29%).
* **Empirical Benchmark Accuracy:** DigitVision DeepConvNet achieved **98.31% Test Accuracy**, **0.9831 Macro-F1**, and **9.14 ms Mean CPU Latency** on the full 10,000-sample test benchmark.
* **Confidence Calibration Verified:** Post-hoc Temperature Scaling converged to $T = 0.9170$, reducing Expected Calibration Error (ECE) from 0.0152 to 0.0031.
* **Explainability Grounded:** Grad-CAM heatmaps verified on the final convolutional layer (`conv_cam`), validating focus on anatomical digit strokes.
* **100% Automated Test Passing:** All 35 unit and integration tests pass with zero errors (`python -m pytest`).
* **Zero PowerPoint Generation:** Strictly honored scope constraints; no slide decks or presentations were generated or altered.

---

## 2. Final Deliverables Inventory

| Deliverable Artifact | File Path | Format | Status / Purpose |
| :--- | :--- | :---: | :--- |
| **Final Institutional Report** | `docs/DigitVision_AI_Micro_Project_Report_Final.docx` | DOCX | Authoritative final submission report for faculty and external examination. |
| **Synchronized Master Report** | `ML-Project Documentation.docx` | DOCX | Working repository master document. |
| **Dataset Specification** | `docs/DATASET.md` | Markdown | Version 2.0.0; full provenance, 4-split accounting, epistemic bounds. |
| **Comprehensive Dataset Audit**| `DATASET_AUDIT.md` | Markdown | Version 1.0.0; cryptographic digests, statistical moments, hash proofs. |
| **Baseline Repository Audit** | `docs/FINAL_AUDIT_BASELINE.md` | Markdown | Baseline inventory, initial findings, and identified defects. |
| **Surgical Repair Log** | `docs/FINAL_REPAIR_LOG.md` | Markdown | Complete record of defects, root causes, minimal fixes, and test evidence. |
| **Final Release Report** | `docs/FINAL_RELEASE_REPORT.md` | Markdown | This authoritative document. |
| **Student Viva Master Guide** | `docs/FACULTY_EXPLANATION.md` | Markdown | Student-friendly plain English guide and viva master reference. |
| **Technical Viva Defense Guide**| `docs/VIVA_PREPARATION.md` | Markdown | Comprehensive viva voce preparation guide with technical answers. |
| **Machine-Readable Metadata** | `artifacts/data/dataset_summary.json` | JSON | Cryptographic digest, split moments, and zero-leakage hash proof. |
| **Class Distribution Data** | `artifacts/data/dataset_class_distribution.csv`| CSV | Exact sample counts and percentages for all 10 digits across all 4 splits. |
| **Partition Audit Data** | `artifacts/data/dataset_partitions_audit.csv` | CSV | Partition-level roles, sample sizes, pixel moments, and collision counts. |
| **Publication Figures** | `artifacts/data/*.png` (4 figures) | PNG | 300 DPI figures: class distributions, moments, variance heatmap, hierarchy. |
| **Experiment Telemetry** | `artifacts/experiment_results.csv` | CSV | Official benchmark results across all 7 models. |

---

## 3. Verified Empirical Benchmark Matrix

The table below summarizes the verified performance metrics across all 7 evaluated models evaluated on the official 10,000-instance air-gapped test set:

| Model Identifier | Architecture Class | Parameters | Test Accuracy | Macro-F1 | Weighted-F1 | Mean Latency (CPU) | Storage Size |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dummy Baseline** | Zero-Rule | 0 | 11.35% | 0.0204 | 0.0231 | 0.13 ms | 0.00 MB |
| **Logistic Regression** | Linear (L-BFGS) | 7,850 | 91.49% | 0.9137 | 0.9148 | 0.06 ms | 0.06 MB |
| **SVM-RBF** | Kernel Classifier | — | 96.11% | 0.9607 | 0.9611 | 1.73 ms | 15.78 MB |
| **Random Forest** | Bagging Ensemble (60) | — | 95.48% | 0.9543 | 0.9547 | 102.09 ms | 26.50 MB |
| **MLP-Deep** | Dense (256-128-10) | 236,682 | 95.91% | 0.9587 | 0.9591 | 3.87 ms | 2.74 MB |
| **LeNet-5** | 5-Layer CNN (1998) | 61,706 | 96.25% | 0.9623 | 0.9625 | 9.72 ms | 0.75 MB |
| **DigitVision DeepConvNet**| Dual-Conv + Dropout | 467,818 | **98.31%** | **0.9831** | **0.9831** | **9.14 ms** | 5.41 MB |

---

## 4. Automated Test Suite Verification

### Pytest Unit & Integration Execution:
```powershell
python -m pytest
```
**Exit Code:** 0  
**Results:**
* `tests\test_api.py`: 3 passed (FastAPI endpoints, health check, prediction format)
* `tests\test_data.py`: 8 passed (SHA-256 verification, reserved pool hygiene, zero leakage, tensor shapes)
* `tests\test_intelligence.py`: 6 passed (stroke density, bounding box, entropy scoring, confidence margin)
* `tests\test_models.py`: 3 passed (model inference, forward pass, logit shapes)
* `tests\test_preprocessing.py`: 12 passed (7-stage pipeline, Otsu binarization, CoM centering, aspect scaling)
* `tests\test_xai.py`: 3 passed (Grad-CAM generation, heatmap bounds, layer hooking)
* **Total: 35 passed, 0 failed in 7.85s**

### Master Integrity Harness Execution:
```powershell
python verify_all.py
```
**Exit Code:** 0  
**Results:**
1. Automated Test Suite: **PASSED (35/35)**
2. Model Weights & Metrics: **PASSED (7/7 models)**
3. Experiment Figures: **PASSED (12 figures)**
4. Presentation Metadata: **PASSED (Read-only consistency verified)**
5. Academic Report Sync: **PASSED (Table 36 & front matter synchronized)**

---

## 5. Unresolved Items & Faculty Actions Required

1. **Continuous Internal Evaluation (CIE) Marks:**  
   In Appendix A (Assessment Rubrics Table / Table 47), the assessment score cells (C1 through C8) have been preserved blank as `Pending Faculty Assessment`. These fields must be completed by the internal evaluation committee.
2. **Signatures & Approvals:**  
   Front-matter signature fields (Certificate, Declaration, Acknowledgement, Evaluation Committee Approval) are prepared with official student and faculty names, ready for physical signing upon printing.
3. **Institutional Page Count Compliance:**  
   The compiled document comprises 53 pages in Microsoft Word due to the complete retention of all 53 institutional tables, NBA CO-PO matrices, Bloom's taxonomy taxonomies, 12 embedded figures, and Appendices A–C. If the department enforces a strict $\le 40$ page ceiling, table padding and line spacing can be condensed without deleting mandatory institutional sections.

---

## 6. Offline Reproduction Protocol

To reproduce the documented empirical findings from scratch on any machine:

### Step 1: Verify Dataset Cryptographic Integrity
```powershell
python -c "from src.data.dataset import MNISTPipeline; p = MNISTPipeline(); print('Integrity:', p.verify_integrity())"
```
*(Expected Output: `Integrity: True`)*

### Step 2: Regenerate Audit Summary Tables & Figures
```powershell
python scripts/generate_dataset_audit_artifacts.py
```
*(Outputs `dataset_summary.json`, class distribution CSV, partition audit CSV, and 4 PNG figures in `artifacts/data/`)*

### Step 3: Run Full Automated Regression Test Suite
```powershell
python -m pytest
```
*(Outputs `35 passed in ~8s`)*

### Step 4: Re-compile Official Academic Word Documentation
```powershell
python scripts/update_academic_documentation.py
```
*(Generates and synchronizes `docs/DigitVision_AI_Micro_Project_Report_Final.docx`)*

### Step 5: Launch Mission Control Web Server
```powershell
uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```
*(Access interactive canvas dashboard at `http://127.0.0.1:8000`)*
