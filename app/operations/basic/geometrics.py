import numpy as np
from PIL import Image

def apply_flipping(img: np.ndarray, mode: str = 'horizontal') -> np.ndarray:
    """Membalik citra secara horizontal, vertical, atau keduanya."""
    if mode == 'horizontal':
        return np.fliplr(img)
    elif mode == 'vertical':
        return np.flipud(img)
    elif mode == 'both':
        return np.flipud(np.fliplr(img))
    return img

def apply_rotation(img: np.ndarray, angle: float = 90.0) -> np.ndarray:
    """Rotasi citra searah jarum jam (clockwise) dengan penyesuaian bounding box."""
    pil_img = Image.fromarray(img)
    # Pillow rotate berlawanan jarum jam, gunakan -angle agar intuitif searah jarum jam
    rotated = pil_img.rotate(-angle, expand=True, resample=Image.Resampling.BILINEAR)
    return np.array(rotated, dtype=np.uint8)

def apply_translation(img: np.ndarray, tx: int = 50, ty: int = 50) -> np.ndarray:
    """Translasi / pergeseran koordinat citra dengan latar belakang hitam."""
    h, w, c = img.shape
    translated = np.zeros_like(img)

    src_x_start = max(0, -tx)
    src_x_end = min(w, w - tx)
    src_y_start = max(0, -ty)
    src_y_end = min(h, h - ty)

    dst_x_start = max(0, tx)
    dst_x_end = min(w, w + tx)
    dst_y_start = max(0, ty)
    dst_y_end = min(h, h + ty)

    if (src_x_end > src_x_start) and (src_y_end > src_y_start):
        translated[dst_y_start:dst_y_end, dst_x_start:dst_x_end] = img[src_y_start:src_y_end, src_x_start:src_x_end]

    return translated

def apply_zooming(img: np.ndarray, scale: float = 1.5) -> np.ndarray:
    """
    Penskalaan ukuran citra (Zoom In / Zoom Out).
    Jika scale > 1 (Zoom in): Memperbesar area tengah citra dengan resolusi tetap 
    agar detail piksel terlihat membesar di layar tanpa mengecil akibat object-contain CSS.
    Jika scale < 1 (Zoom out): Mengecilkan citra dan memberi bingkai latar hitam.
    """
    h, w, c = img.shape
    scale = max(0.1, float(scale))
    pil_img = Image.fromarray(img)

    if scale > 1.0:
        # Potong area tengah sesuai proporsi skala, lalu resize kembali ke resolusi awal
        crop_w = int(w / scale)
        crop_h = int(h / scale)
        x1 = (w - crop_w) // 2
        y1 = (h - crop_h) // 2
        cropped = pil_img.crop((x1, y1, x1 + crop_w, y1 + crop_h))
        zoomed = cropped.resize((w, h), Image.Resampling.NEAREST)
        return np.array(zoomed, dtype=np.uint8)
    elif scale < 1.0:
        # Kecilkan citra lalu tempatkan di tengah kanvas hitam seukuran asli
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        resized = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
        
        canvas = np.zeros((h, w, c), dtype=np.uint8)
        off_x = (w - new_w) // 2
        off_y = (h - new_h) // 2
        canvas[off_y:off_y + new_h, off_x:off_x + new_w] = np.array(resized, dtype=np.uint8)
        return canvas
    else:
        return img

def apply_cropping(img: np.ndarray, x: int = 0, y: int = 0, width: int = 200, height: int = 200) -> np.ndarray:
    """Pemotongan area citra persegi panjang."""
    h, w, _ = img.shape
    x1 = max(0, min(x, w - 1))
    y1 = max(0, min(y, h - 1))
    x2 = max(x1 + 1, min(x + width, w))
    y2 = max(y1 + 1, min(y + height, h))
    return img[y1:y2, x1:x2].copy()