# DIGITVISION AI

```
██████╗ ██╗ ██████╗ ██╗████████╗██╗   ██╗██╗███████╗██╗ ██████╗ ███╗   ██╗
██╔══██╗██║██╔════╝ ██║╚══██╔══╝██║   ██║██║██╔════╝██║██╔═══██╗████╗  ██║
██║  ██║██║██║  ███╗██║   ██║   ██║   ██║██║███████╗██║██║   ██║██╔██╗ ██║
██║  ██║██║██║   ██║██║   ██║   ╚██╗ ██╔╝██║╚════██║██║██║   ██║██║╚██╗██║
██████╔╝██║╚██████╔╝██║   ██║    ╚████╔╝ ██║███████║██║╚██████╔╝██║ ╚████║
╚═════╝ ╚═╝ ╚═════╝ ╚═╝   ╚═╝     ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

### *Explainable, Confidence-Aware Handwritten Digit Intelligence Platform*

[![Status](https://img.shields.io/badge/STATUS-PRODUCTION--READY-1DB954?style=flat-square&logo=git)](file:///c:/Users/tejas/Desktop/ML_project)
[![Visual Theme](https://img.shields.io/badge/THEME-DEEP--OBSIDIAN-050505?style=flat-square)](file:///c:/Users/tejas/Desktop/ML_project/src/app/static/css/style.css)
[![Invariant](https://img.shields.io/badge/INVARIANT-CANONICAL--CENTERING-3B82F6?style=flat-square)](file:///c:/Users/tejas/Desktop/ML_project/src/preprocessing/canonical.py)
[![Test Suite](https://img.shields.io/badge/TESTS-100%25--PASSING-1DB954?style=flat-square)](file:///c:/Users/tejas/Desktop/ML_project/tests)
[![Python](https://img.shields.io/badge/PYTHON-3.13-white?style=flat-square&logo=python)](file:///c:/Users/tejas/Desktop/ML_project/requirements.txt)

---

## 1. Executive Summary & Core Novelty

**DIGITVISION AI** is an advanced, production-grade computer vision engineering platform designed to eliminate silent machine-learning errors in handwritten digit recognition. Rather than acting as a black-box classifier, DIGITVISION AI couples high-accuracy neural perception with information-theoretic uncertainty calibration, input-quality gating, real-world perturbation benchmarking, and real-time visual explanations (Grad-CAM & Saliency maps).

### The 14 Core Capabilities:
1. **Production Deep ConvNet**: Multi-stage convolutional network with explicit Grad-CAM layer hooks.
2. **Classical ML vs Deep Learning**: Empirically benchmarks DeepConvNet, LeNet-5, SVM (RBF), Random Forest, and Logistic Regression on an isolated 10,000-sample test set.
3. **Canonical Preprocessing Invariant**: Single, shared preprocessor enforcing aspect-ratio preserved scaling into a $20\times 20$ box and spatial moment centroid alignment to $(13.5, 13.5)$.
4. **Confidence-Aware Prediction**: Post-hoc probability calibration via Temperature Scaling ($T$) to prevent overconfidence.
5. **Input-Quality Intelligence**: Pre-inference topological audit measuring stroke density, bounding box coverage, centroid deviation, and speckle noise.
6. **Top-K Prediction Telemetry**: Full probabilistic breakdown of top candidates with confidence bands.
7. **Digit Forensics Telemetry**: Diagnostic payload emitted for every forward pass containing timing, quality scores, entropy, and visual overlays.
8. **Error Intelligence**: Automated mining of top confusion digit pairs (e.g. 4 vs 9, 3 vs 8, 7 vs 1).
9. **High-Confidence Failure Analysis**: Forensic isolation of "silent errors" where model confidence is $\ge 80\%$ yet prediction is incorrect.
10. **Explainable AI (XAI)**: Dual-stream visual attribution featuring Grad-CAM heatmaps at layer `conv_cam` and first-order pixel gradient saliency.
11. **Distribution Shift Benchmarks**: Quantified degradation testing across 6 corruption domains (Gaussian noise, rotation, shear, stroke thickness, translation, contrast attenuation) over 5 severity levels.
12. **Deep Obsidian ML Dashboard**: High-density, professional engineering interface with interactive canvas, live vector presets, and real-time telemetry HUD.
13. **Scientific Experiment Tracking**: Fully reproducible experiment pipeline writing metrics, confusion matrices, and figures to a single source of truth.
14. **Synchronized Presentations**: Automated PowerPoint (`.pptx`) and standalone interactive HTML slide decks synchronized with real empirical data.

---

## 2. Source-of-Truth Hierarchy & Architectural Invariants

When verifying information, the repository strictly enforces the following order:

```
Executed Experiment Artifacts  ->  Executed Source Code  ->  Config Files  ->  Tests  ->  Docs  ->  PPT
```

### Architectural Invariants:
- **Canonical Preprocessing Invariant**: Shared identically between training, validation, and real-time inference.
- **Isolated Evaluation Set**: 10,000 MNIST test samples remain quarantined; never used during training or tuning.
- **Zero Fabrication Policy**: No fabricated metrics, graphs, confusion matrices, or model parameters.
- **Fail-Closed Safety**: Input quality gatekeeper rejects invalid drawings before entering the classifier.

---

## 3. Visual Language: Deep Obsidian

The user interface and scientific figures strictly embody the **Deep Obsidian** engineering aesthetic:

| Token | Hex Value | Application |
| :--- | :--- | :--- |
| **Void** | `#050505` | Master viewport background, canvas container |
| **Ground** | `#0A0A0A` | Card backgrounds, slide stages, figure backgrounds |
| **Surface** | `#121212` | Panels, HUD metrics blocks, table headers |
| **Secondary Surface** | `#161616` | Hover states, active controls, buttons |
| **Borders** | `#262626` / `#333333` | Hairline dividers, precision grid lines |
| **Primary Text** | `#FFFFFF` | Primary headings, large digits, active data |
| **Secondary Text** | `#A1A1AA` | Labels, table descriptions, subtitles |
| **Telemetry Text** | `#737373` | Monospace metadata, timestamps, units |
| **High Confidence** | `#1DB954` | Verified status, accepted decisions, top metrics |
| **Moderate Confidence**| `#FFB000` | Ambiguous runner-up warnings, review status |
| **Error / Low Conf** | `#FF3333` | Quality rejections, out-of-distribution alerts |

---

## 4. Repository Structure

```
ML_project/
├── data/                         # Cached MNIST datasets
├── src/
│   ├── preprocessing/
│   │   ├── canonical.py          # Authoritative canonical preprocessing invariant
│   │   └── __init__.py
│   ├── models/
│   │   ├── deep.py               # DeepConvNet and classic LeNet-5
│   │   ├── classical.py          # SVM-RBF, Random Forest, Logistic Regression
│   │   └── __init__.py
│   ├── intelligence/
│   │   ├── quality.py            # Input-Quality heuristics & pre-flight gatekeeper
│   │   ├── confidence.py         # Temperature scaling, entropy, margin calibration
│   │   ├── forensics.py          # Unified telemetry packager
│   │   └── __init__.py
│   ├── xai/
│   │   ├── gradcam.py            # Grad-CAM heatmap generation & Viridis blending
│   │   ├── saliency.py           # Pixel attribution gradient maps
│   │   └── __init__.py
│   ├── evaluation/
│   │   ├── metrics.py            # Classification reports, ECE, latency profiling
│   │   ├── error_analysis.py     # Top confusions and silent failure mining
│   │   ├── robustness.py         # 6-corruption distribution shift benchmark
│   │   ├── visualization.py      # Deep Obsidian figure plotting engine
│   │   └── __init__.py
│   ├── app/
│   │   ├── server.py             # FastAPI production server & REST API
│   │   └── static/
│   │       ├── index.html        # Interactive Deep Obsidian ML Dashboard
│   │       ├── css/style.css     # Deep Obsidian styling
│   │       └── js/app.js         # Drawing canvas & telemetry controller
│   └── presentation/
│       ├── generate_pptx.py      # Automated PPTX presentation builder
│       ├── DigitVision_AI_Presentation.pptx # Compiled 12-slide deck
│       └── slides.html           # Standalone interactive HTML slide deck
├── experiments/
│   ├── run_experiments.py        # Master pipeline to train, calibrate & evaluate
│   ├── models/                   # Serialized checkpoints (.keras, .joblib)
│   ├── metrics/
│   │   └── experiment_results.json # SINGLE SOURCE OF TRUTH FOR ALL METRICS
│   ├── figures/                  # Publication-quality Deep Obsidian figures
│   └── failures/                 # Mined high-confidence failure cases
├── docs/
│   ├── ARCHITECTURE.md           # System architecture & invariants
│   ├── MATHEMATICAL_FOUNDATIONS.md # Formal proofs, moments, loss & calibration
│   ├── EXPERIMENT_REPORT.md      # Detailed experimental results & findings
│   ├── MODEL_CARD.md             # Production model card (Mitchell et al.)
│   └── API_SPECIFICATION.md      # REST endpoints and schemas
├── tests/
│   ├── test_preprocessing.py     # Centroiding & invariant test suite
│   ├── test_intelligence.py      # Quality score & uncertainty unit tests
│   ├── test_models.py            # Model structure & probability simplex tests
│   ├── test_xai.py               # Grad-CAM & Saliency unit tests
│   └── test_api.py               # REST API test suite
├── verify_all.py                 # Master verification & repository audit harness
├── requirements.txt              # Production dependency lockfile
└── README.md                     # Master documentation
```

---

## 5. Quickstart & Verification

### 5.1 Environment Setup
```powershell
# Install dependencies
python -m pip install -r requirements.txt
```

### 5.2 Execute Full Verification Suite
Verify repository invariants, run all unit tests, and audit the metrics source-of-truth:
```powershell
python verify_all.py
```

### 5.3 Launch the Interactive Deep Obsidian Dashboard
Start the production FastAPI server:
```powershell
python -m uvicorn src.app.server:app --host 127.0.0.1 --port 8000 --reload
```
Navigate in your browser to:
- **Interactive Dashboard**: `http://127.0.0.1:8000`
- **Interactive Presentation Deck**: `http://127.0.0.1:8000/presentation/slides.html`
- **Interactive OpenAPI Docs**: `http://127.0.0.1:8000/docs`

---

## 6. Mathematical Foundations Summary

- **Canonical Centroid Alignment**:
  $$\bar{x} = \frac{\sum x \mathbf{I}(x, y)}{\sum \mathbf{I}(x, y)}, \quad \bar{y} = \frac{\sum y \mathbf{I}(x, y)}{\sum \mathbf{I}(x, y)}, \quad \Delta x = 13.5 - \bar{x}, \quad \Delta y = 13.5 - \bar{y}$$
- **Temperature Scaling Calibration**:
  $$q_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}, \quad \min_{T > 0} \mathcal{L}_{\text{NLL}}(T)$$
- **Shannon Predictive Entropy**:
  $$H(\mathbf{p}) = -\sum_{i=0}^9 p_i \log_2(p_i + \epsilon) \quad \text{[bits]}$$
- **Grad-CAM Feature Attribution**:
  $$\alpha_k^c = \frac{1}{Z} \sum_{i, j} \frac{\partial y^c}{\partial A_{i, j}^k}, \quad L_{\text{Grad-CAM}}^c = \operatorname{ReLU}\left( \sum_k \alpha_k^c A^k \right)$$

---

## 7. Deliverable Verification Evidence

| Deliverable | Artifact Path | Status |
| :--- | :--- | :--- |
| **Working Software** | [`src/app/server.py`](file:///c:/Users/tejas/Desktop/ML_project/src/app/server.py), [`src/app/static/index.html`](file:///c:/Users/tejas/Desktop/ML_project/src/app/static/index.html) | Verified Operational |
| **ML Experiments** | [`experiments/metrics/experiment_results.json`](file:///c:/Users/tejas/Desktop/ML_project/experiments/metrics/experiment_results.json) | Real Measurements |
| **Technical Docs** | [`docs/ARCHITECTURE.md`](file:///c:/Users/tejas/Desktop/ML_project/docs/ARCHITECTURE.md), [`docs/MATHEMATICAL_FOUNDATIONS.md`](file:///c:/Users/tejas/Desktop/ML_project/docs/MATHEMATICAL_FOUNDATIONS.md) | Synchronized |
| **Presentation Deck**| [`src/presentation/DigitVision_AI_Presentation.pptx`](file:///c:/Users/tejas/Desktop/ML_project/src/presentation/DigitVision_AI_Presentation.pptx) | Generated via python-pptx |
| **Verification** | [`tests/`](file:///c:/Users/tejas/Desktop/ML_project/tests), [`verify_all.py`](file:///c:/Users/tejas/Desktop/ML_project/verify_all.py) | 100% Pass Rate |
