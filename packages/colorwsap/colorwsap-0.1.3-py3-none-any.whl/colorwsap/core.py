import cv2
import numpy as np

COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "grey": (128, 128, 128),
    "silver": (192, 192, 192),
    "maroon": (128, 0, 0),
    "olive": (128, 128, 0),
    "purple": (128, 0, 128),
    "teal": (0, 128, 128),
    "navy": (0, 0, 128),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
}

def color2rgb(color):
    if isinstance(color, str):
        color = color.lower()
        if color in COLOR_MAP:
            return COLOR_MAP[color]
        raise ValueError(f"Unknown color name '{color}'")
    if isinstance(color, (tuple, list)) and len(color) == 3:
        return tuple(color)
    raise ValueError("Color must be a name str or RGB tuple/list of 3 ints")

def swap_color(input_path, color, output_path, alpha_thresh=1):
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if img is None or img.ndim != 3 or img.shape[2] not in (3, 4):
        raise ValueError("Input PNG missing or not suitable")

    # Ensure image has alpha channel
    if img.shape[2] == 3:
        bgr = img
        alpha = np.full(bgr.shape[:2], 255, dtype=np.uint8)
        img = np.dstack([bgr, alpha])

    b, g, r, a = cv2.split(img)

    # Mask of non-transparent pixels (alpha > threshold)
    mask = a > alpha_thresh

    rgb = color2rgb(color)

    out = img.copy()

    # Change color only where mask is True
    out[..., 0][mask] = rgb[2]  # B channel (opencv uses BGR)
    out[..., 1][mask] = rgb[1]  # G channel
    out[..., 2][mask] = rgb[0]  # R channel

    # Alpha remains unchanged to preserve transparency

    cv2.imwrite(output_path, out)
