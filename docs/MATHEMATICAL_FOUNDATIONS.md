# DIGITVISION AI — MATHEMATICAL FOUNDATIONS

> **Rigorous Theoretical Formulations & Derivations**  
> *Spatial Moments, Loss Optimization, Calibration, Information Theory, and Explainability*

---

## 1. Spatial Moments & Canonical Centroid Alignment

Let $\mathbf{I}(x, y) \ge 0$ denote the continuous or discrete intensity of an image at coordinate $(x, y)$.

### 1.1 Spatial Moments Definition
The $(p + q)$-th order 2D continuous spatial moment is defined as:
$$M_{pq} = \iint x^p y^q \mathbf{I}(x, y) \, dx \, dy$$

For a discrete digital image of size $W \times H$:
$$M_{pq} = \sum_{x=0}^{W-1} \sum_{y=0}^{H-1} x^p y^q \mathbf{I}(x, y)$$

- **Zeroth-Order Moment ($M_{00}$)** represents the total integrated mass (intensity):
  $$M_{00} = \sum_{x, y} \mathbf{I}(x, y)$$
- **First-Order Moments ($M_{10}, M_{01}$)** represent the moments of mass with respect to the $y$- and $x$-axes:
  $$M_{10} = \sum_{x, y} x \, \mathbf{I}(x, y), \quad M_{01} = \sum_{x, y} y \, \mathbf{I}(x, y)$$

### 1.2 Center of Mass (Centroid)
The center of mass $(\bar{x}, \bar{y})$ of the digit is given by:
$$\bar{x} = \frac{M_{10}}{M_{00}}, \quad \bar{y} = \frac{M_{01}}{M_{00}}$$

### 1.3 Centering Invariant Translation
Let the desired optical center of the $W \times H$ canvas be:
$$x_c = \frac{W - 1}{2}, \quad y_c = \frac{H - 1}{2}$$
For a $28 \times 28$ grid, $x_c = 13.5, y_c = 13.5$.

The required affine shift vector $(\Delta x, \Delta y)$ is:
$$\Delta x = x_c - \bar{x}, \quad \Delta y = y_c - \bar{y}$$

The affine transformation matrix applied via bilinear interpolation is:
$$\mathbf{M}_{\text{shift}} = \begin{bmatrix} 1 & 0 & \Delta x \\ 0 & 1 & \Delta y \end{bmatrix}$$

---

## 2. Loss Optimization & Multi-Class Cross-Entropy

### 2.1 Categorical Cross-Entropy Loss
Let $y \in \{0, \dots, K-1\}$ be the true ground-truth class, represented by a one-hot vector $\mathbf{y} \in \{0, 1\}^K$.
Let $\mathbf{z} \in \mathbb{R}^K$ be the raw unnormalized logits emitted by the network's final layer.
The softmax probability distribution $\mathbf{p} = \sigma(\mathbf{z})$ is given by:
$$p_i = \frac{\exp(z_i)}{\sum_{j=0}^{K-1} \exp(z_j)}, \quad i \in \{0, \dots, K-1\}$$

The cross-entropy loss $\mathcal{L}_{\text{CE}}$ for a single sample is:
$$\mathcal{L}_{\text{CE}}(\mathbf{y}, \mathbf{p}) = -\sum_{k=0}^{K-1} y_k \log p_k = -\log p_y = -\left( z_y - \log \sum_{j=0}^{K-1} \exp(z_j) \right)$$

### 2.2 Gradient of Cross-Entropy with Respect to Logits
$$\frac{\partial \mathcal{L}_{\text{CE}}}{\partial z_i} = p_i - y_i$$
This demonstrates that the gradient is simply the prediction residual error.

---

## 3. Probability Calibration & Temperature Scaling

Modern deep neural networks, while highly accurate, frequently exhibit overconfidence due to cross-entropy minimization on unregularized parameters (Guo et al., 2017).

### 3.1 Temperature Scaling Formulation
Temperature scaling introduces a single scalar parameter $T > 0$ applied to the logit vector $\mathbf{z}$ before the softmax function:
$$q_i(T) = \frac{\exp(z_i / T)}{\sum_{j=0}^{K-1} \exp(z_j / T)}$$

### 3.2 Invariance of Class Rankings
Because the exponential function is strictly monotonic:
$$\operatorname{argmax}_i q_i(T) = \operatorname{argmax}_i \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)} = \operatorname{argmax}_i \frac{z_i}{T} = \operatorname{argmax}_i z_i$$
Thus, temperature scaling preserves top-1 accuracy while correcting calibration.

### 3.3 Optimization Objective
$T$ is learned on a held-out validation set $\mathcal{D}_{\text{val}} = \{(\mathbf{x}_n, y_n)\}_{n=1}^{N_{\text{val}}}$ by minimizing the Negative Log-Likelihood (NLL):
$$\min_{T > 0} \mathcal{L}_{\text{NLL}}(T) = -\frac{1}{N_{\text{val}}} \sum_{n=1}^{N_{\text{val}}} \log q_{y_n}^{(n)}(T) = -\frac{1}{N_{\text{val}}} \sum_{n=1}^{N_{\text{val}}} \left[ \frac{z_{y_n}^{(n)}}{T} - \log \sum_{j=0}^{K-1} \exp\left(\frac{z_j^{(n)}}{T}\right) \right]$$
Optimized using the L-BFGS-B algorithm with parameter bounds $T \in [0.05, 10.0]$.

---

## 4. Uncertainty & Information Theory Metrics

### 4.1 Shannon Entropy
The predictive uncertainty of the distribution $\mathbf{p}$ over $K=10$ classes is quantified by Shannon entropy:
$$H(\mathbf{p}) = -\sum_{i=0}^{K-1} p_i \log_2(p_i + \epsilon) \quad \text{[bits]}$$
- **Minimum Entropy**: $H(\mathbf{p}) = 0$ bits when the model is 100% deterministic on a single class.
- **Maximum Entropy**: $H(\mathbf{p}) = \log_2(10) \approx 3.3219$ bits for a uniform distribution.

### 4.2 Normalized Entropy
$$\bar{H}(\mathbf{p}) = \frac{H(\mathbf{p})}{\log_2(K)} \in [0.0, 1.0]$$

### 4.3 Prediction Margin
Let $p_{(1)}$ and $p_{(2)}$ denote the highest and second-highest probabilities:
$$p_{(1)} = \max_i p_i, \quad p_{(2)} = \max_{j \neq \operatorname{argmax} p} p_j$$
The margin of confidence is:
$$M = p_{(1)} - p_{(2)} \in [0.0, 1.0]$$
A large margin ($M > 0.60$) indicates a distinct winner; a small margin ($M < 0.20$) signifies high decision boundary ambiguity.

---

## 5. Expected Calibration Error (ECE)

To quantitatively evaluate whether predicted probabilities reflect empirical ground-truth likelihoods, predictions are partitioned into $M$ equally spaced confidence bins:
$$B_m = \left\{ n \in \{1, \dots, N\} \;\middle|\; \hat{p}_n \in \left( \frac{m-1}{M}, \frac{m}{M} \right] \right\}$$

### 5.1 Bin Accuracy and Confidence
$$\operatorname{acc}(B_m) = \frac{1}{|B_m|} \sum_{n \in B_m} \mathbf{1}(\hat{y}_n = y_n)$$
$$\operatorname{conf}(B_m) = \frac{1}{|B_m|} \sum_{n \in B_m} \hat{p}_n$$

### 5.2 Expected Calibration Error (ECE)
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \operatorname{acc}(B_m) - \operatorname{conf}(B_m) \right|$$

---

## 6. Explainable AI: Grad-CAM Derivation

Gradient-Weighted Class Activation Mapping (Selvaraju et al., 2017) produces visual explanations by computing class-specific feature importance weights.

Let $A^k \in \mathbb{R}^{U \times V}$ denote the $k$-th feature map activation of convolutional layer `conv_cam`.
Let $y^c$ denote the unnormalized class score (pre-softmax) for target class $c$.

### 6.1 Importance Weight $\alpha_k^c$
The importance weight of feature map $k$ for class $c$ is computed by global average pooling of gradients:
$$\alpha_k^c = \frac{1}{Z} \sum_{i=1}^U \sum_{j=1}^V \frac{\partial y^c}{\partial A_{i, j}^k}$$
where $Z = U \times V$ is the spatial area of the feature map.

### 6.2 Heatmap Aggregation & Rectification
The class activation map $L_{\text{Grad-CAM}}^c$ is computed via a linear combination followed by a Rectified Linear Unit (ReLU):
$$L_{\text{Grad-CAM}}^c = \operatorname{ReLU}\left( \sum_k \alpha_k^c A^k \right)$$
The ReLU operation ensures the heatmap focuses strictly on features whose presence increases class score $y^c$, suppressing negative or contradictory activations.

### 6.3 Bilinear Upsampling & Normalization
$$\hat{L}^c(x, y) = \frac{L^c(x, y) - \min L^c}{\max L^c - \min L^c + \epsilon}, \quad (x, y) \in [0, 28) \times [0, 28)$$
