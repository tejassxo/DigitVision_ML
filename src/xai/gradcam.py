"""
DIGITVISION AI — Explainable AI (Grad-CAM)
==========================================
Implements Gradient-weighted Class Activation Mapping (Grad-CAM)
for convolutional neural networks on handwritten digit classifications.
Provides visual explanations highlighting discriminative regions of the digit.
"""

import base64
import io
import cv2
import numpy as np
import tensorflow as tf
from typing import Dict, Any, Tuple, Optional
from PIL import Image


def find_target_conv_layer(model: tf.keras.Model) -> Optional[str]:
    """Finds the last convolutional layer in the given Keras model."""
    for layer in reversed(model.layers):
        if isinstance(layer, (tf.keras.layers.Conv2D, tf.keras.layers.Convolution2D)):
            return layer.name
    return None


def generate_gradcam_heatmap(
    model: tf.keras.Model,
    img_array: np.ndarray,
    target_class: Optional[int] = None,
    layer_name: Optional[str] = None
) -> Tuple[np.ndarray, int]:
    """
    Computes 2D Grad-CAM heatmap for an input image (shape 1, 28, 28, 1).

    Args:
        model: Trained Keras/TensorFlow model.
        img_array: 4D numpy array with shape (1, 28, 28, 1) and values in [0, 1].
        target_class: Target digit class (0-9). If None, uses top predicted class.
        layer_name: Name of target conv layer. If None, auto-detects last Conv2D.

    Returns:
        heatmap: 2D float32 array of shape (28, 28) normalized to [0.0, 1.0].
        class_idx: Target digit class analyzed.
    """
    if layer_name is None:
        layer_name = find_target_conv_layer(model)
        if layer_name is None:
            raise ValueError("No convolutional layer found in model for Grad-CAM.")

    target_layer = model.get_layer(layer_name)

    # In Keras 3, ensure inbound nodes are initialized for Sequential architectures
    try:
        model_out = model.output
    except Exception:
        _ = model(tf.cast(img_array, tf.float32), training=False)
        try:
            model_out = model.output
        except Exception:
            model_out = model.layers[-1].output

    # Sub-model mapping inputs to [conv_output, predictions]
    grad_model = tf.keras.Model(
        inputs=model.inputs,
        outputs=[target_layer.output, model_out]
    )

    with tf.GradientTape() as tape:
        img_tensor = tf.cast(img_array, tf.float32)
        tape.watch(img_tensor)
        conv_outputs, predictions = grad_model(img_tensor, training=False)
        
        # If model outputs a dict or list, unpack
        if isinstance(predictions, list):
            predictions = predictions[0]

        if target_class is None:
            target_class = int(tf.argmax(predictions[0]))

        loss = predictions[:, target_class]

    # Gradient of target score w.r.t. conv feature maps
    grads = tape.gradient(loss, conv_outputs)

    # Global Average Pooling of gradients across spatial dimensions
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Weight feature channels by pooled gradients
    conv_outputs_val = conv_outputs[0]
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs_val), axis=-1)

    # Apply ReLU to focus solely on features that positively contribute to the target class
    heatmap = tf.maximum(heatmap, 0.0)

    # Normalize heatmap
    max_val = tf.reduce_max(heatmap)
    if max_val > 1e-7:
        heatmap = heatmap / max_val
    else:
        heatmap = tf.zeros_like(heatmap)

    heatmap_np = heatmap.numpy()

    # Resize to original 28x28 resolution
    resized_heatmap = cv2.resize(heatmap_np, (28, 28), interpolation=cv2.INTER_CUBIC)
    resized_heatmap = np.clip(resized_heatmap, 0.0, 1.0).astype(np.float32)

    return resized_heatmap, target_class


def render_gradcam_overlay(
    original_img: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.55,
    colormap: int = cv2.COLORMAP_VIRIDIS
) -> str:
    """
    Blends the grayscale digit image with the Grad-CAM heatmap and returns
    a base64 PNG data URL suitable for Deep Obsidian UI rendering.

    Args:
        original_img: Grayscale 28x28 array in [0.0, 1.0].
        heatmap: 28x28 array in [0.0, 1.0].
        alpha: Blend ratio for heatmap.
        colormap: OpenCV colormap (default VIRIDIS).

    Returns:
        Base64 PNG data URL string ('data:image/png;base64,...').
    """
    orig_uint8 = (np.clip(original_img, 0.0, 1.0) * 255.0).astype(np.uint8)
    heatmap_uint8 = (np.clip(heatmap, 0.0, 1.0) * 255.0).astype(np.uint8)

    # Upscale for smooth high-DPI display (e.g. 140x140)
    display_size = (168, 168)
    orig_scaled = cv2.resize(orig_uint8, display_size, interpolation=cv2.INTER_NEAREST)
    heatmap_scaled = cv2.resize(heatmap_uint8, display_size, interpolation=cv2.INTER_CUBIC)

    # Apply colormap to heatmap
    color_heatmap = cv2.applyColorMap(heatmap_scaled, colormap)
    orig_bgr = cv2.cvtColor(orig_scaled, cv2.COLOR_GRAY2BGR)

    # Weighted blend
    blended = cv2.addWeighted(orig_bgr, 1.0 - alpha, color_heatmap, alpha, 0)

    # Encode to PNG base64
    success, encoded_img = cv2.imencode('.png', blended)
    if not success:
        return ""
    b64_str = base64.b64encode(encoded_img).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"
