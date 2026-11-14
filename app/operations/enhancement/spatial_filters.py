import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

def _convolve_3x3(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Helper konvolusi 3x3 vektorisasi."""
    h, w, _ = img.shape
    pad = np.pad(img.astype(np.float32), ((1, 1), (1, 1), (0, 0)), mode='edge')
    out = (
        pad[0:h, 0:w]     * kernel[0, 0] + pad[0:h, 1:w+1]     * kernel[0, 1] + pad[0:h, 2:w+2]     * kernel[0, 2] +
        pad[1:h+1, 0:w]   * kernel[1, 0] + pad[1:h+1, 1:w+1]   * kernel[1, 1] + pad[1:h+1, 2:w+2]   * kernel[1, 2] +
        pad[2:h+2, 0:w]   * kernel[2, 0] + pad[2:h+2, 1:w+1]   * kernel[2, 1] + pad[2:h+2, 2:w+2]   * kernel[2, 2]
    )
    return out

def apply_lowpass_spatial(img: np.ndarray) -> np.ndarray:
    """Spatial Lowpass Filtering (Mean/Averaging Filter 3x3)."""
    kernel = np.ones((3, 3), dtype=np.float32) / 9.0
    out = _convolve_3x3(img, kernel)
    return np.clip(out, 0, 255).astype(np.uint8)

def apply_median_spatial(img: np.ndarray, ksize: int = 3) -> np.ndarray:
    """Spatial Median Filtering tervektorisasi menggunakan sliding_window_view."""
    k = int(ksize) if int(ksize) % 2 == 1 else int(ksize) + 1
    pad_w = k // 2
    padded = np.pad(img, ((pad_w, pad_w), (pad_w, pad_w), (0, 0)), mode='edge')
    # Bentuk view (H, W, C, k, k) lalu ambil median di sumbu kernel
    windows = sliding_window_view(padded, (k, k), axis=(0, 1))
    median_img = np.median(windows, axis=(-2, -1))
    return median_img.astype(np.uint8)

def apply_highpass_spatial(img: np.ndarray) -> np.ndarray:
    """Spatial Highpass Filtering (Deteksi detail frekuensi tinggi / Laplacian tajam)."""
    kernel = np.array([[-1, -1, -1],
                       [-1,  8, -1],
                       [-1, -1, -1]], dtype=np.float32)
    out = _convolve_3x3(img, kernel)
    return np.clip(out, 0, 255).astype(np.uint8)

def apply_highboost_spatial(img: np.ndarray, boost_a: float = 1.5) -> np.ndarray:
    """Spatial Highboost Filtering: I_hb = A * I_orig - I_lowpass."""
    lowpass = _convolve_3x3(img, np.ones((3, 3), dtype=np.float32) / 9.0)
    mask = img.astype(np.float32) - lowpass
    out = img.astype(np.float32) + (float(boost_a) - 1.0) * mask
    return np.clip(out, 0, 255).astype(np.uint8)