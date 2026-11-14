import numpy as np

def apply_brightness(img: np.ndarray, value: int = 30) -> np.ndarray:
    """Mengatur kecerahan citra: I_out = I_in + value."""
    res = img.astype(np.int32) + int(value)
    return np.clip(res, 0, 255).astype(np.uint8)

def apply_contrast(img: np.ndarray, factor: float = 1.5) -> np.ndarray:
    """Mengatur kontras citra terhadap titik tengah intensitas 128."""
    res = float(factor) * (img.astype(np.float32) - 128.0) + 128.0
    return np.clip(res, 0, 255).astype(np.uint8)

def apply_hist_equalization(img: np.ndarray) -> np.ndarray:
    """Histogram Equalization pada kanal luminansi (YCbCr) agar warna RGB tetap natural."""
    r = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    b = img[:, :, 2].astype(np.float32)

    # Konversi RGB -> YCbCr
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.168736 * r - 0.331264 * g + 0.5 * b + 128.0
    cr = 0.5 * r - 0.418688 * g - 0.081312 * b + 128.0

    # Ekualisasi Histogram pada kanal Y
    y_uint8 = np.clip(y, 0, 255).astype(np.uint8)
    hist, _ = np.histogram(y_uint8.flatten(), bins=256, range=[0, 256])
    cdf = hist.cumsum()
    cdf_m = np.ma.masked_equal(cdf, 0)
    cdf_m = (cdf_m - cdf_m.min()) * 255 / (cdf_m.max() - cdf_m.min() + 1e-8)
    cdf_final = np.ma.filled(cdf_m, 0).astype(np.float32)
    y_eq = cdf_final[y_uint8]

    # Konversi kembali YCbCr -> RGB
    r_out = y_eq + 1.402 * (cr - 128.0)
    g_out = y_eq - 0.344136 * (cb - 128.0) - 0.714136 * (cr - 128.0)
    b_out = y_eq + 1.772 * (cb - 128.0)

    out = np.stack([r_out, g_out, b_out], axis=-1)
    return np.clip(out, 0, 255).astype(np.uint8)