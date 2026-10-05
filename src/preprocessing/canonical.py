"""
DIGITVISION AI — Canonical Preprocessing Pipeline
==================================================
ARCHITECTURAL INVARIANT:
This module defines the single, authoritative preprocessing pipeline
shared identically between offline training/validation and real-time inference.
No divergent preprocessing logic is permitted elsewhere in the repository.
"""

import base64
import io
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, Optional


def decode_image_input(image_input: Any) -> np.ndarray:
    """
    Decodes various image input formats (base64 string, bytes, PIL Image, or numpy array)
    into a single-channel 2D float32 or uint8 grayscale numpy array.
    """
    if isinstance(image_input, str):
        # Base64 string (handles data URL prefixes like 'data:image/png;base64,...')
        if "," in image_input:
            image_input = image_input.split(",", 1)[1]
        image_bytes = base64.b64decode(image_input)
        pil_img = Image.open(io.BytesIO(image_bytes))
        arr = np.array(pil_img)
    elif isinstance(image_input, bytes):
        pil_img = Image.open(io.BytesIO(image_input))
        arr = np.array(pil_img)
    elif isinstance(image_input, Image.Image):
        arr = np.array(image_input)
    elif isinstance(image_input, np.ndarray):
        arr = image_input.copy()
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    # Handle channel formats
    if arr.ndim == 3:
        if arr.shape[2] == 4:
            # RGBA: If alpha channel carries stroke information
            alpha = arr[:, :, 3]
            rgb = arr[:, :, :3]
            # Convert RGB to grayscale
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            # If alpha is variable and indicates strokes
            if np.max(alpha) > 0 and np.min(alpha) < 255:
                # Modulate grayscale by alpha
                gray = (gray.astype(np.float32) * (alpha.astype(np.float32) / 255.0)).astype(np.uint8)
            arr = gray
        elif arr.shape[2] == 3:
            arr = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        elif arr.shape[2] == 1:
            arr = arr[:, :, 0]

    return arr.astype(np.uint8)


def detect_and_normalize_contrast(gray: np.ndarray) -> np.ndarray:
    """
    Ensures foreground (stroke) is bright (high intensity) and background is dark (0),
    matching the MNIST specification standard.
    """
    # Sample corners (four 4x4 corners) to estimate background intensity
    h, w = gray.shape
    corner_size = max(2, min(h, w) // 10)
    corners = [
        gray[0:corner_size, 0:corner_size],
        gray[0:corner_size, w - corner_size:w],
        gray[h - corner_size:h, 0:corner_size],
        gray[h - corner_size:h, w - corner_size:w]
    ]
    mean_corner_val = np.mean([np.mean(c) for c in corners])

    # If background appears bright (> 127), invert image so background becomes 0
    if mean_corner_val > 127:
        gray = 255 - gray

    return gray


def compute_center_of_mass(img: np.ndarray) -> Tuple[float, float]:
    """
    Calculates the spatial center of mass (centroid) of a 2D grayscale image using moments.
    Returns (x_c, y_c).
    """
    moments = cv2.moments(img.astype(np.float64))
    m00 = moments['m00']
    if m00 < 1e-5:
        # Image is empty or near zero; fallback to geometric center
        return (img.shape[1] / 2.0, img.shape[0] / 2.0)
    cx = moments['m10'] / m00
    cy = moments['m01'] / m00
    return (cx, cy)


def shift_image(img: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """
    Translates an image by (dx, dy) pixels using bilinear interpolation.
    """
    h, w = img.shape
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    shifted = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return shifted


def canonical_preprocess(
    image_input: Any,
    target_size: Tuple[int, int] = (28, 28),
    inner_box_size: int = 20,
    threshold: int = 25,
    use_otsu: bool = False,
    return_tensor: bool = False
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Canonical MNIST-standard preprocessing invariant pipeline:
    1. Decode input into single-channel grayscale (H, W).
    2. Normalize contrast (bright stroke on dark background).
    3. Detect foreground bounding box using Otsu or justified thresholding.
    4. Aspect-ratio preserving resize into an inner box (e.g. 20x20).
    5. Place inside 28x28 black canvas.
    6. Calculate center-of-mass (moments) and translate centroid to frame center (13.5, 13.5).
    7. Normalize intensity to float32 range [0.0, 1.0].
    8. If return_tensor=True, emit shape (1, 28, 28, 1) float32 tensor.

    Returns:
        processed_image: np.ndarray of shape (28, 28) or (1, 28, 28, 1) in [0.0, 1.0], float32.
        metadata: Dict containing diagnostic info (is_empty, bbox, centroid, shifts).
    """
    raw_gray = decode_image_input(image_input)
    norm_gray = detect_and_normalize_contrast(raw_gray)

    metadata: Dict[str, Any] = {
        "raw_shape": raw_gray.shape,
        "is_empty": False,
        "bbox": None,
        "centroid_raw": None,
        "centroid_final": None,
        "dx": 0.0,
        "dy": 0.0,
        "active_pixel_ratio": 0.0,
        "threshold_used": threshold
    }

    # Identify foreground pixels via Otsu or justified thresholding
    if use_otsu:
        # Otsu binarization computes optimal global threshold
        otsu_val, binary = cv2.threshold(norm_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        metadata["threshold_used"] = float(otsu_val)
    else:
        binary = (norm_gray > threshold).astype(np.uint8) * 255

    coords = cv2.findNonZero(binary)

    if coords is None or len(coords) < 8:
        # Canvas has fewer than 8 active pixels: considered empty/blank
        metadata["is_empty"] = True
        if return_tensor:
            blank = np.zeros((1, target_size[1], target_size[0], 1), dtype=np.float32)
        else:
            blank = np.zeros(target_size, dtype=np.float32)
        return blank, metadata

    # Get bounding rectangle of the digit stroke
    x, y, w, h = cv2.boundingRect(coords)
    metadata["bbox"] = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}

    digit_crop = norm_gray[y:y+h, x:x+w]

    # Compute aspect-ratio preserving scale
    # Digit must fit within inner_box_size (default 20x20)
    scale = inner_box_size / max(h, w)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    # Choose interpolation method: INTER_AREA for downsampling, INTER_CUBIC for upsampling
    interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
    resized_digit = cv2.resize(digit_crop, (new_w, new_h), interpolation=interp)

    # Place resized digit into a 28x28 canvas centered geometrically first
    canvas_w, canvas_h = target_size
    canvas = np.zeros((canvas_h, canvas_w), dtype=np.float32)

    start_x = (canvas_w - new_w) // 2
    start_y = (canvas_h - new_h) // 2
    canvas[start_y:start_y+new_h, start_x:start_x+new_w] = resized_digit.astype(np.float32)

    # Compute Center of Mass on canvas
    cx, cy = compute_center_of_mass(canvas)
    metadata["centroid_raw"] = (float(cx), float(cy))

    # Center of 28x28 frame is (13.5, 13.5)
    target_center_x = (canvas_w - 1) / 2.0
    target_center_y = (canvas_h - 1) / 2.0

    shift_x = target_center_x - cx
    shift_y = target_center_y - cy
    metadata["dx"] = float(shift_x)
    metadata["dy"] = float(shift_y)

    # Shift canvas to align center of mass with target center
    centered = shift_image(canvas, shift_x, shift_y)

    # Clip and normalize to [0.0, 1.0]
    final_img = np.clip(centered / 255.0, 0.0, 1.0).astype(np.float32)

    # Final centroid verification
    final_cx, final_cy = compute_center_of_mass((final_img * 255.0).astype(np.uint8))
    metadata["centroid_final"] = (float(final_cx), float(final_cy))
    metadata["active_pixel_ratio"] = float(np.count_nonzero(final_img > 0.05) / (canvas_w * canvas_h))

    if return_tensor:
        final_img = np.expand_dims(final_img, axis=(0, -1))

    return final_img, metadata


def canonical_preprocess_tensor(
    image_input: Any,
    target_size: Tuple[int, int] = (28, 28),
    inner_box_size: int = 20,
    threshold: int = 25,
    use_otsu: bool = False
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Authoritative canonical preprocessing wrapper returning a float32 tensor
    of exact shape (1, 28, 28, 1) normalized to [0.0, 1.0].
    
    Fulfills the core system invariant:
    Raw Image -> Grayscale -> Contrast/background normalization ->
    Otsu / justified thresholding -> Foreground detection -> Bounding box ->
    Aspect-ratio preservation -> Fit into ~20x20 region -> Center of mass ->
    28x28 canvas -> Normalize [0,1] -> float32 tensor -> (1, 28, 28, 1).
    """
    return canonical_preprocess(
        image_input=image_input,
        target_size=target_size,
        inner_box_size=inner_box_size,
        threshold=threshold,
        use_otsu=use_otsu,
        return_tensor=True
    )
