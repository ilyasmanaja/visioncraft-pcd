import numpy as np
from PIL import Image

def to_grayscale(img: np.ndarray) -> np.ndarray:
    """Konversi ke Grayscale menggunakan bobot luminansi ITU-R 601-2."""
    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2]
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    gray_uint8 = np.clip(gray, 0, 255).astype(np.uint8)
    return np.stack([gray_uint8, gray_uint8, gray_uint8], axis=-1)

def to_binary(img: np.ndarray, threshold: int = 128) -> np.ndarray:
    """Konversi ke Citra Biner (Black & White)."""
    gray = to_grayscale(img)[:, :, 0]
    binary = np.where(gray >= threshold, 255, 0).astype(np.uint8)
    return np.stack([binary, binary, binary], axis=-1)

def to_cmy(img: np.ndarray) -> np.ndarray:
    """Konversi RGB ke representasi CMY (Cyan, Magenta, Yellow)."""
    # CMY = 255 - RGB
    return 255 - img

def to_hsv_vis(img: np.ndarray) -> np.ndarray:
    """Konversi RGB ke HSV dan visualisasikan sebagai RGB channel."""
    pil_img = Image.fromarray(img, mode='RGB').convert('HSV')
    return np.array(pil_img, dtype=np.uint8)

def to_yuv(img: np.ndarray) -> np.ndarray:
    """Konversi ke YUV standar analog PAL."""
    r = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    b = img[:, :, 2].astype(np.float32)

    y = 0.299 * r + 0.587 * g + 0.114 * b
    u = -0.14713 * r - 0.28886 * g + 0.436 * b + 128
    v = 0.615 * r - 0.51499 * g - 0.10001 * b + 128

    yuv = np.stack([y, u, v], axis=-1)
    return np.clip(yuv, 0, 255).astype(np.uint8)

def to_yiq(img: np.ndarray) -> np.ndarray:
    """Konversi ke YIQ standar NTSC."""
    r = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    b = img[:, :, 2].astype(np.float32)

    y = 0.299 * r + 0.587 * g + 0.114 * b
    i = 0.596 * r - 0.274 * g - 0.322 * b + 128
    q = 0.211 * r - 0.523 * g + 0.312 * b + 128

    yiq = np.stack([y, i, q], axis=-1)
    return np.clip(yiq, 0, 255).astype(np.uint8)

def to_pseudo(img: np.ndarray) -> np.ndarray:
    """Pseudo-coloring (False Coloring) berbasis level intensitas grayscale."""
    gray = to_grayscale(img)[:, :, 0]
    
    # Pemetaan colormap tiruan (Jet-like: Blue -> Green -> Red)
    r = np.clip(1.5 * gray - 128, 0, 255).astype(np.uint8)
    g = np.clip(255 - np.abs(2 * gray - 255), 0, 255).astype(np.uint8)
    b = np.clip(255 - 1.5 * gray, 0, 255).astype(np.uint8)
    
    return np.stack([r, g, b], axis=-1)