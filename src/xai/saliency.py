"""
DIGITVISION AI — Pixel Attribution Saliency Maps
=================================================
Calculates input-gradient saliency maps showing which input pixels
had the greatest local impact on the model's confidence for the predicted class.
"""

import base64
import cv2
import numpy as np
import tensorflow as tf
from typing import Tuple, Optional


def compute_pixel_saliency(
    model: tf.keras.Model,
    img_array: np.ndarray,
    target_class: Optional[int] = None
) -> Tuple[np.ndarray, int]:
    """
    Computes vanilla gradient saliency: |d(y_c)/d(x)| for each pixel.

    Args:
        model: Trained Keras/TensorFlow model.
        img_array: 4D numpy array with shape (1, 28, 28, 1).
        target_class: Target digit class.

    Returns:
        saliency_map: 28x28 normalized float32 array in [0.0, 1.0].
        target_class: Analyzed class.
    """
    img_tensor = tf.cast(img_array, tf.float32)

    with tf.GradientTape() as tape:
        tape.watch(img_tensor)
        preds = model(img_tensor, training=False)
        if isinstance(preds, list):
            preds = preds[0]
        if target_class is None:
            target_class = int(tf.argmax(preds[0]))
        loss = preds[:, target_class]

    grads = tape.gradient(loss, img_tensor)
    abs_grads = tf.abs(grads)
    # Take max over channels
    saliency = tf.reduce_max(abs_grads, axis=-1)[0].numpy()

    # Normalize to [0, 1]
    max_val = np.max(saliency)
    if max_val > 1e-7:
        saliency = saliency / max_val
    else:
        saliency = np.zeros_like(saliency)

    return saliency.astype(np.float32), target_class


def render_saliency_overlay(
    original_img: np.ndarray,
    saliency: np.ndarray,
    alpha: float = 0.65
) -> str:
    """
    Renders saliency map overlay as base64 PNG data URL.
    """
    orig_uint8 = (np.clip(original_img, 0.0, 1.0) * 255.0).astype(np.uint8)
    saliency_uint8 = (np.clip(saliency, 0.0, 1.0) * 255.0).astype(np.uint8)

    display_size = (168, 168)
    orig_scaled = cv2.resize(orig_uint8, display_size, interpolation=cv2.INTER_NEAREST)
    saliency_scaled = cv2.resize(saliency_uint8, display_size, interpolation=cv2.INTER_CUBIC)

    # Use COLORMAP_INFERNO for high-contrast attribution
    color_saliency = cv2.applyColorMap(saliency_scaled, cv2.COLORMAP_INFERNO)
    orig_bgr = cv2.cvtColor(orig_scaled, cv2.COLOR_GRAY2BGR)

    blended = cv2.addWeighted(orig_bgr, 1.0 - alpha, color_saliency, alpha, 0)

    success, encoded = cv2.imencode('.png', blended)
    if not success:
        return ""
    b64 = base64.b64encode(encoded).decode('utf-8')
    return f"data:image/png;base64,{b64}"
