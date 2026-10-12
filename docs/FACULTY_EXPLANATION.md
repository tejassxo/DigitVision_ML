# DIGITVISION AI — Student-Friendly Faculty Explanation & Viva Master Guide

**Project Title:** DigitVision AI — Explainable, Confidence-Aware Handwritten Digit Intelligence Platform  
**Target Audience:** Students preparing for Faculty Review, Lab Internal Viva, and External Examination  
**College:** Sreyas Institute of Engineering and Technology, Department of CSE (AI & ML)  
**Authors:** M TEJAS YADAV (45%), K Charan Teja (35%), Y Akshay Raj (20%)  

---

## 1. The Big Picture: What is DigitVision AI?

If a faculty member asks you: *"What have you built and why isn't this just another toy MNIST project?"*, here is your answer:

> *"Most student projects simply download MNIST, train a basic 3-line model in a Jupyter Notebook, get 97% accuracy, and stop. But if you try to draw a digit on a real-world web canvas or mobile screen, that toy model fails completely because real human sketches have different stroke thicknesses, off-center positioning, and inverted backgrounds.*  
> 
> *DigitVision AI is an end-to-end, production-grade intelligence platform. We solve the real-world gap by combining four core engineering pillars:*  
> *1. A **7-Stage Canonical Preprocessing Pipeline** that mathematically normalizes any freehand canvas sketch to match MNIST standards.*  
> *2. A **7-Model Benchmark Suite** comparing classical statistical algorithms against Deep CNNs under identical hardware constraints.*  
> *3. **Confidence Intelligence** using post-hoc Temperature Scaling and Shannon Entropy so the model knows when it is uncertain rather than making confident false guesses.*  
> *4. **Explainable AI (Grad-CAM)** that visually reveals exactly which pixels and stroke features triggered the prediction.*  
> *All of this runs in an asynchronous FastAPI mission control backend serving an interactive HTML5 canvas with sub-10 millisecond inference latencies."*

---

## 2. The Dataset Story: Where Does the Data Come From?

* **Origin:** MNIST was created in 1998 by Yann LeCun (NYU) and Corinna Cortes (Google Research). It was formed by combining and modifying two government datasets: **NIST Special Database 3** (handwriting from high school students) and **NIST Special Database 19** (handwriting from U.S. Census Bureau employees).
* **Official License:** Creative Commons Attribution-Share Alike 3.0 (CC BY-SA 3.0).
* **Local Cryptographic Cache:** The dataset is cached locally in our repository at `data/raw/mnist.npz` (10.96 MiB). Its SHA-256 hash is `731c5ac602752760c8e48fbffcf8c3b850d9dc2a2aedcf2cc48468fc17b673d1`. This proves that our project can run completely offline without downloading anything from the internet, and that the data has never been tampered with.

---

## 3. The 4-Split Partition Accounting: Why Didn't We Train on All 60,000 Samples?

When the examiner asks: *"Why do you have 20,000 training samples instead of the full 60,000?"*, explain the mathematical reason:

The complete MNIST population has **70,000 images**:
* **60,000 raw training images**, which we partitioned into:
  1. **Active Training Set (20,000 images / 28.57%):** Used for gradient backpropagation and parameter optimization.
  2. **Validation Set (3,000 images / 4.29%):** Used for monitoring convergence, early stopping, and tuning the calibration temperature.
  3. **Reserved Training Pool (37,000 images / 52.86%):** Kept untouched in our `.npz` file for scalability experiments.
* **10,000 Official Test Benchmark (14.29%):** Strictly air-gapped and isolated. We evaluated all 7 models across all 10,000 test images with zero subsampling.

### Why 20,000 active samples? (The SVM Memory Bottleneck)
* We wanted to benchmark **Support Vector Machines with an RBF Kernel (SVM-RBF)** alongside CNNs.
* Training an RBF SVM requires computing the **Kernel Gram Matrix**, which has space complexity of $\mathcal{O}(N^2)$.
* If you train on all $N = 60,000$ images, the Gram matrix requires:
  $$\frac{60,000 \times 60,000 \times 8 \text{ bytes}}{1024^3} \approx 28.8 \text{ Gigabytes of RAM!}$$
  On standard laboratory CPUs, this causes memory crashing and takes hours to run.
* At $N = 20,000$, the Gram matrix requires only **3.2 GB of RAM**, converging in under 2.5 minutes while still delivering **96.11% test accuracy**.
* This demonstrates disciplined machine learning engineering: balancing statistical power against computational complexity.

---

## 4. The 7-Stage Preprocessing Pipeline: How Drawings Become Tensors

When a user draws a digit on the web canvas, why doesn't it break? Because of our 7-stage invariant pipeline (`src/preprocessing/canonical.py`):

1. **Grayscale Conversion:** Canvas RGBA is converted to single-channel luminance ($Y = 0.299R + 0.587G + 0.114B$).
2. **Background Inversion & Normalization:** Web canvases have white backgrounds and dark strokes; MNIST has black backgrounds ($0.0$) and white strokes ($1.0$). We invert the contrast automatically.
3. **Otsu's Adaptive Thresholding:** Dynamically calculates the optimal binarization threshold separating foreground ink strokes from background noise without manual threshold tuning.
4. **Bounding Box Localization:** Crops the active stroke tightly, eliminating unused canvas borders.
5. **Aspect-Ratio Preserving Scaling:** Resizes the stroke so its maximum dimension is exactly $20$ pixels, preserving the natural width-to-height ratio without squishing or stretching.
6. **Center-of-Mass Centering:** Computes the mathematical center of mass $(\bar{x}, \bar{y})$ using pixel intensity moments and centers it inside a $28 \times 28$ matrix (giving 4-pixel margins, exactly matching native MNIST).
7. **Float32 Normalization:** Scales all pixel values into $[0.0, 1.0]$.

**Critical Invariant:** The exact same pipeline runs during training, batch testing, and live web inference. This completely eliminates **training-serving skew**.

---

## 5. The 7 Models: What They Do and How They Performed

We evaluated 7 distinct models on the identical 10,000-sample test set:

| Model | Type | Test Accuracy | Macro-F1 | CPU Latency | Key Takeaway for Viva |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Dummy Baseline** | Zero-rule | 11.35% | 0.0204 | 0.13 ms | Predicts most frequent class; sets the absolute chance floor. |
| **Logistic Regression** | Linear | 91.49% | 0.9137 | 0.06 ms | Convex baseline with 7,850 weights; fast, but cannot model non-linear stroke loops. |
| **SVM-RBF** | Kernel | 96.11% | 0.9607 | 1.73 ms | Strong non-linear margin classifier; requires 15.8 MB storage for support vectors. |
| **Random Forest** | Bagging Ensemble | 95.48% | 0.9543 | 102.09 ms | 60 decision trees; good accuracy, but slow inference due to traversing 60 trees on 784 dimensions. |
| **MLP-Deep** | Dense Neural Net | 95.91% | 0.9587 | 3.87 ms | 2 hidden layers (256 $\to$ 128); treats pixels as flat vectors, losing 2D spatial arrangement. |
| **LeNet-5** | Historical CNN | 96.25% | 0.9623 | 9.72 ms | Yann LeCun's 1998 classic; introduces 2D convolution weight sharing. |
| **DigitVision DeepConvNet** | Modern CNN | **98.31%** | **0.9831** | **9.14 ms** | **Our champion model; dual conv blocks, SpatialDropout, Global Average Pooling, sub-10ms CPU latency.** |

---

## 6. Unsupervised Clustering (K-Means) in Chapter 3: Why Did We Do It?

If the faculty asks: *"Why did you run K-Means clustering if MNIST is already a supervised, labeled dataset?"*

> *"We used K-Means ($K=10$ clusters in 784-dimensional space) as an **Exploratory Data Analysis (EDA)** technique to discover the intrinsic geometric structure of handwriting without supervisory labels.*  
> 
> *Our analysis revealed that:*  
> *1. Digits with uniform circular shapes like **'0'** and **'1'** form tight, isolated clusters with minimal overlap.*  
> *2. However, digits with multi-stroke cursive variations like **'4' and '9'**, or **'3' and '5'**, have overlapping cluster centroids in pixel space.*  
> *This unsupervised geometric overlap mathematically explains why linear models like Logistic Regression hit a performance ceiling at 91.5%, and why convolutional feature extractors are necessary to separate these subtle anatomical differences."*

---

## 7. Confidence Intelligence: Temperature Scaling & Entropy

### Why Softmax Confidence Lies:
Standard neural networks trained with cross-entropy are notoriously **overconfident**. A model might output a 99% softmax score on a garbage sketch simply because the raw logit scores were large.

### How We Solved It:
1. **Temperature Scaling:**  
   We introduce a scalar temperature parameter $T > 0$ to divide logits before applying softmax:
   $$\hat{p}_i = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}$$
   We optimized $T$ on the validation set using L-BFGS, finding **$T = 0.9170$**. This reduced the **Expected Calibration Error (ECE)** from $0.0152$ down to **$0.0031$**, meaning predicted probabilities now closely reflect true empirical likelihoods.
2. **Shannon Entropy (Uncertainty Metric):**  
   $$H(p) = - \sum_{c=0}^9 p_c \log_2(p_c)$$
   * If the model is 100% confident in one class, $H = 0.0$ bits.
   * If the model is completely confused and guesses equal 10% across all 10 digits, $H = \log_2(10) \approx 3.32$ bits.
   * If an input produces $H > 1.2$ bits or margin $< 0.20$, DigitVision AI automatically flags it as **High Epistemic Uncertainty**, rejecting automated acceptance and alerting the user.

---

## 8. Explainable AI (XAI): How Grad-CAM Works

If the examiner asks: *"How do you prove your CNN isn't just memorizing background noise?"*

> *"We implemented **Gradient-weighted Class Activation Mapping (Grad-CAM)**.*  
> *1. We take the gradient of the predicted class score $y^c$ with respect to the feature maps of our final convolutional layer (`conv_cam`).*  
> *2. We globally average-pool these gradients to compute importance weights $\alpha_k^c$ for each feature channel.*  
> *3. We compute a weighted sum of the feature maps, pass it through a ReLU (to isolate positive evidence), and upsample the resulting $7 \times 7$ activation map back to $28 \times 28$.*  
> 
> *The resulting heatmap proves that the CNN focuses directly on discriminative stroke features—such as the bottom loop of a '6', the crossbar of a '4', or the loop of an '8'—rather than canvas edges or background noise."*

---

## 9. Failure Modes: What Confuses the Model?

From our empirical error analysis on the 10,000 test images, the top confusion pairs are:
1. **Digit 4 misclassified as 9 (18 cases):** Occurs when the human writer closes the upper triangular stroke of '4', making it look like the loop of '9'.
2. **Digit 7 misclassified as 2 (16 cases):** Occurs when a '7' has an exaggerated horizontal bottom serif or hook.
3. **Digit 5 misclassified as 3 (11 cases):** Occurs in fast cursive writing when the upper horizontal bar of '5' detaches or curves like a '3'.

---

## 10. Rapid-Fire Viva Voce Cheat Sheet (Top 15 Questions)

| # | Expected Viva Question | Best 1-Sentence Answer |
| :-: | :--- | :--- |
| **1** | What is the input shape and output classes? | Input is a $(28 \times 28 \times 1)$ normalized float32 tensor; output is a 10-class categorical probability distribution. |
| **2** | What is your champion model and its accuracy? | DigitVision DeepConvNet with 98.31% test accuracy, 0.9831 macro-F1, and 9.14 ms latency on CPU. |
| **3** | How many parameters does DeepConvNet have? | Exactly 467,818 trainable parameters, consuming 5.41 MB of storage. |
| **4** | Why did you choose Adam optimizer? | Adam combines momentum (smoothing gradients) and RMSProp (adaptive per-parameter learning rates) with $\alpha = 0.001$. |
| **5** | What loss function was used? | Sparse Categorical Cross-Entropy (Multinomial Negative Log-Likelihood). |
| **6** | What is the total dataset size? | 70,000 images: 20k active train, 3k validation, 37k reserved raw pool, and 10k air-gapped test set. |
| **7** | What license does MNIST have? | Creative Commons Attribution-Share Alike 3.0 (CC BY-SA 3.0), curated by Yann LeCun and Corinna Cortes. |
| **8** | How did you prove zero data leakage? | MD5 raster hashing across all 70,000 images proved zero duplicates across splits, and `np.shares_memory` proved buffer isolation. |
| **9** | What is Otsu's thresholding? | An unsupervised binarization method that finds the intensity threshold minimizing intra-class variance between ink and background. |
| **10** | What is the purpose of center-of-mass centering? | It calculates the centroid $(\bar{x}, \bar{y})$ of ink pixels and translates the digit so its mass sits in the exact center of the $28 \times 28$ grid. |
| **11** | What is Temperature Scaling? | A post-hoc calibration technique dividing logits by scalar $T=0.9170$, reducing Expected Calibration Error (ECE) to 0.0031. |
| **12** | How do you detect uncertain sketches? | Using Shannon Entropy: sketches with $H(p) > 1.2$ bits or margin $< 0.20$ are flagged as high uncertainty. |
| **13** | Which layer does Grad-CAM hook into? | The final convolutional layer (`conv_cam`), capturing high-level spatial semantic features before dense pooling. |
| **14** | How fast is inference? | 9.14 ms average latency on CPU, enabling real-time interactive drawing at >100 frames per second. |
| **15** | What are the student contributions? | Tejas (45% - Deep Learning & Architecture), Charan (35% - Preprocessing & Classical ML), Akshay (20% - Full-Stack & Telemetry). |

---

## 11. NBA Program Specific Outcomes (PSOs) — Department Alignment & Viva Defense

If an external examiner or faculty review panel asks: *"What are your department's Program Specific Outcomes (PSOs) and how does DigitVision AI specifically address them?"*, here is your structured, comprehensive answer:

### Approved Department PSOs (Department of CSE - AI & ML)

| Outcome | Official Department Statement | Correlation Level with DigitVision AI |
| :---: | :--- | :---: |
| **PSO1** | **Apply programming skills and mathematical concepts to design, develop, and optimize AI and machine learning solutions for real-world problems.** | **Level 3 (High / Substantial)**<br>*(Average: 2.83 across COs)* |
| **PSO2** | **Demonstrate competency in Deep Learning, and Data Analytics tools and technologies to build intelligent systems and pursue careers in industry, research, or higher education.** | **Level 3 (High / Substantial)**<br>*(Average: 2.67 across COs)* |

---

### How DigitVision AI Fulfills PSO1 (Level 3 — Substantial):
1. **Mathematical Concepts Applied:**
   - **Statistical Pixel Moments:** Computed mean pixel intensity ($\mu = 0.1307$), standard deviation ($\sigma = 0.3081$), and variance across 70,000 images (`compute_dataset_statistics()`).
   - **Center-of-Mass Spatial Moments:** Calculated translation coordinates $(\bar{x}, \bar{y})$ using raw image moments $M_{10}/M_{00}$ and $M_{01}/M_{00}$ to center digits into a $28 \times 28$ matrix.
   - **Convex & Kernel Optimization:** Formulated convex L2-regularized multinomial logistic regression via L-BFGS, and bounded RBF Support Vector Machine Kernel Gram matrix complexity ($\mathcal{O}(N^2)$ space bounding at $N=20,000$ to prevent RAM thrashing).
   - **Loss Minimization & Post-Hoc Calibration:** Optimized categorical cross-entropy loss, and derived scalar temperature scaling ($T = 0.9170$) via validation log-likelihood to minimize Expected Calibration Error (ECE) from $0.0152$ down to $0.0031$.
2. **Programming Skills Demonstrated:**
   - Engineered modular, reproducible Python 3.13 architecture utilizing NumPy vectorized operations, SciPy, OpenCV adaptive thresholding (Otsu method), scikit-learn classifiers, and Keras 3 multi-backend engine.
   - Validated code integrity with **35/35 automated unit tests** (`pytest`) ensuring zero data leakage, buffer isolation, and sub-millisecond tensor preprocessing.
3. **Real-World Problem Solved:**
   - Tackled the severe **interactive domain shift** (varying stroke widths, off-center sketches, inverted contrasts) that causes ordinary MNIST models to fail when humans draw on live screens, providing a reliable OCR backbone for automated postal sortation and banking cheque recognition.

---

### How DigitVision AI Fulfills PSO2 (Level 3 — Substantial):
1. **Deep Learning Competency:**
   - **Custom Architecture Design:** Designed and trained **DigitVision DeepConvNet** (dual $3 \times 3$ convolutional blocks, Batch Normalization, SpatialDropout $p=0.25$, and Global Average Pooling) achieving **98.31% test accuracy** and **0.9831 Macro-F1** on the 10,000-sample air-gapped test set.
   - **Architectural Benchmarking:** Compared modern deep CNNs against classical baselines and historical **LeNet-5 (1998)** to isolate the impact of modern regularizers.
   - **Explainable AI (Grad-CAM):** Implemented Gradient-weighted Class Activation Mapping hooked directly to the final `conv_cam` feature maps, visually attributing predictions to actual stroke anatomy.
2. **Data Analytics Tools & Technologies:**
   - **Exploratory Data Analysis (EDA):** Analyzed 70,000 image tensors, stroke spine density, and class distributions across all 4 data partitions.
   - **Unsupervised Geometry (K-Means Clustering):** Applied $K=10$ K-Means clustering in 784-dimensional space, discovering an overall cluster purity of $58.87\%$ and diagnosing intrinsic morphological overlap between classes (e.g., '4' vs '9').
   - **Uncertainty Analytics:** Computed Shannon Entropy ($H(p)$) and margin confidence to detect ambiguous out-of-distribution inputs.
3. **Intelligent Systems & Career Preparation:**
   - Delivered a complete, production-grade intelligence platform: asynchronous FastAPI backend, sub-10 ms CPU inference latency, interactive drawing canvas HUD, and real-time telemetry console.
   - Developed defense-grade software engineering habits (git versioning, cryptographic data verification, reproducible benchmarks) equipping team members for demanding roles in AI research, data analytics, and software engineering.

---

### Quick Faculty Viva Q&A on PSOs:
* **Q: Which PSO is mapped to your DeepConvNet model?**  
  * **A:** Both PSO1 and PSO2. PSO1 because DeepConvNet represents the mathematical formulation and programming optimization of an AI solution for real-world digit recognition; PSO2 because it demonstrates deep learning competency (CNN architecture, Grad-CAM XAI) and data analytics tooling.
* **Q: What data analytics tools did you use for PSO2?**  
  * **A:** We used NumPy, SciPy, Matplotlib, and scikit-learn to perform statistical moment profiling, bimodal pixel histogram analysis, unsupervised K-Means cluster geometry, confusion matrix error diagnostics, and Expected Calibration Error (ECE) reliability diagrams.
