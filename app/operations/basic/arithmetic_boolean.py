import numpy as np
from PIL import Image

def align_image_sizes(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """Menyamakan resolusi gambar kedua mengikuti resolusi gambar pertama."""
    h, w = img1.shape[:2]
    if img2.shape[:2] != (h, w):
        pil_img2 = Image.fromarray(img2)
        resized = pil_img2.resize((w, h), Image.Resampling.BILINEAR)
        return np.array(resized, dtype=np.uint8)
    return img2

# --- ARITHMETIC OPERATIONS ---

def apply_add(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """Penjumlahan citra: C = A + B dengan clipping ke 255."""
    img2 = align_image_sizes(img1, img2)
    res = img1.astype(np.int32) + img2.astype(np.int32)
    return np.clip(res, 0, 255).astype(np.uint8)

def apply_subtract(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """Pengurangan citra: C = A - B dengan clipping ke 0."""
    img2 = align_image_sizes(img1, img2)
    res = img1.astype(np.int32) - img2.astype(np.int32)
    return np.clip(res, 0, 255).astype(np.uint8)

def apply_multiply(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """Perkalian citra ternormalisasi: C = (A * B) / 255."""
    img2 = align_image_sizes(img1, img2)
    res = (img1.astype(np.float32) * img2.astype(np.float32)) / 255.0
    return np.clip(res, 0, 255).astype(np.uint8)

def apply_divide(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """Pembagian citra dengan pelindung zero-division: C = (A / (B + 1)) * 255."""
    img2 = align_image_sizes(img1, img2)
    # Tambah epsilon 1 untuk mencegah pembagian dengan nol
    res = (img1.astype(np.float32) / (img2.astype(np.float32) + 1.0)) * 255.0
    return np.clip(res, 0, 255).astype(np.uint8)

# --- BOOLEAN OPERATIONS ---

def apply_not(img: np.ndarray) -> np.ndarray:
    """NOT Bitwise: ~A (ekuivalen dengan 255 - A)."""
    return np.bitwise_not(img)

def apply_and(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """AND Bitwise: A & B."""
    img2 = align_image_sizes(img1, img2)
    return np.bitwise_and(img1, img2)

def apply_or(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """OR Bitwise: A | B."""
    img2 = align_image_sizes(img1, img2)
    return np.bitwise_or(img1, img2)

def apply_xor(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    """XOR Bitwise: A ^ B."""
    img2 = align_image_sizes(img1, img2)
    return np.bitwise_xor(img1, img2)