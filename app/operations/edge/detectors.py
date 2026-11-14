import numpy as np

def _to_gray_float(img: np.ndarray) -> np.ndarray:
    """Konversi citra RGB ke grayscale float32."""
    return (0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]).astype(np.float32)

def _to_rgb_uint8(gray: np.ndarray) -> np.ndarray:
    """Konversi kembali matriks 2D grayscale ke 3-kanal RGB uint8."""
    clipped = np.clip(gray, 0, 255).astype(np.uint8)
    return np.stack([clipped, clipped, clipped], axis=-1)

def _convolve2d(gray: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Konvolusi 2D cepat berbasis akumulasi irisan array (tanpa alokasi 4D)."""
    kh, kw = kernel.shape
    h, w = gray.shape
    pad_top = kh // 2
    pad_bottom = kh - 1 - pad_top
    pad_left = kw // 2
    pad_right = kw - 1 - pad_left

    padded = np.pad(gray, ((pad_top, pad_bottom), (pad_left, pad_right)), mode='edge')
    out = np.zeros((h, w), dtype=np.float32)

    for i in range(kh):
        for j in range(kw):
            weight = kernel[i, j]
            if weight != 0.0:
                out += padded[i:i + h, j:j + w] * weight
    return out

# --- 1. 1ST DIFFERENTIAL GRADIENT ---

def apply_sobel(img: np.ndarray) -> np.ndarray:
    gray = _to_gray_float(img)
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    gx = _convolve2d(gray, kx)
    gy = _convolve2d(gray, ky)
    mag = np.hypot(gx, gy)
    return _to_rgb_uint8(mag)

def apply_prewitt(img: np.ndarray) -> np.ndarray:
    gray = _to_gray_float(img)
    kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    gx = _convolve2d(gray, kx)
    gy = _convolve2d(gray, ky)
    mag = np.hypot(gx, gy)
    return _to_rgb_uint8(mag)

def apply_robert(img: np.ndarray) -> np.ndarray:
    gray = _to_gray_float(img)
    kx = np.array([[1, 0], [0, -1]], dtype=np.float32)
    ky = np.array([[0, 1], [-1, 0]], dtype=np.float32)
    gx = _convolve2d(gray, kx)
    gy = _convolve2d(gray, ky)
    mag = np.hypot(gx, gy)
    return _to_rgb_uint8(mag)

# --- 2. 2ND DIFFERENTIAL GRADIENT ---

def apply_laplacian(img: np.ndarray) -> np.ndarray:
    gray = _to_gray_float(img)
    kernel = np.array([[-1, -1, -1],
                       [-1,  8, -1],
                       [-1, -1, -1]], dtype=np.float32)
    res = np.abs(_convolve2d(gray, kernel))
    return _to_rgb_uint8(res)

def apply_log(img: np.ndarray) -> np.ndarray:
    """Laplacian of Gaussian (LoG) menggunakan kernel diskrit 5x5."""
    gray = _to_gray_float(img)
    kernel = np.array([
        [0,  0, -1,  0,  0],
        [0, -1, -2, -1,  0],
        [-1, -2, 16, -2, -1],
        [0, -1, -2, -1,  0],
        [0,  0, -1,  0,  0]
    ], dtype=np.float32)
    res = np.abs(_convolve2d(gray, kernel))
    return _to_rgb_uint8(res)

def apply_canny(img: np.ndarray, low_thresh: int = 50, high_thresh: int = 150) -> np.ndarray:
    """Deteksi tepi Canny cepat murni NumPy (Gaussian -> Sobel -> NMS -> Fast Hysteresis)."""
    gray = _to_gray_float(img)

    # 1. Gaussian Smoothing 5x5
    gauss_k = (1.0 / 159.0) * np.array([
        [2,  4,  5,  4, 2],
        [4,  9, 12,  9, 4],
        [5, 12, 15, 12, 5],
        [4,  9, 12,  9, 4],
        [2,  4,  5,  4, 2]
    ], dtype=np.float32)
    smooth = _convolve2d(gray, gauss_k)

    # 2. Gradien Sobel & Arah Sudut
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    gx = _convolve2d(smooth, kx)
    gy = _convolve2d(smooth, ky)
    mag = np.hypot(gx, gy)
    max_mag = mag.max()
    if max_mag > 0:
        mag *= (255.0 / max_mag)

    angle = np.rad2deg(np.arctan2(gy, gx)) % 180.0

    # 3. Non-Maximum Suppression (Vektorisasi)
    h, w = mag.shape
    nms = np.zeros((h, w), dtype=np.float32)
    pad_m = np.pad(mag, 1, mode='constant')

    dir0 = ((angle < 22.5) | (angle >= 157.5))
    cond0 = (mag >= pad_m[1:h+1, 2:w+2]) & (mag >= pad_m[1:h+1, 0:w])
    nms[dir0 & cond0] = mag[dir0 & cond0]

    dir45 = ((angle >= 22.5) & (angle < 67.5))
    cond45 = (mag >= pad_m[0:h, 2:w+2]) & (mag >= pad_m[2:h+2, 0:w])
    nms[dir45 & cond45] = mag[dir45 & cond45]

    dir90 = ((angle >= 67.5) & (angle < 112.5))
    cond90 = (mag >= pad_m[0:h, 1:w+1]) & (mag >= pad_m[2:h+2, 1:w+1])
    nms[dir90 & cond90] = mag[dir90 & cond90]

    dir135 = ((angle >= 112.5) & (angle < 157.5))
    cond135 = (mag >= pad_m[0:h, 0:w]) & (mag >= pad_m[2:h+2, 2:w+2])
    nms[dir135 & cond135] = mag[dir135 & cond135]

    # 4. Double Thresholding & Fast 8-Neighbor Slice Hysteresis
    low = float(min(low_thresh, high_thresh))
    high = float(max(low_thresh, high_thresh))

    edges = (nms >= high)
    weak = (nms >= low) & (~edges)

    while True:
        p = np.pad(edges, 1, mode='constant')
        neighbor_strong = (
            p[:-2, :-2] | p[:-2, 1:-1] | p[:-2, 2:] |
            p[1:-1, :-2] |               p[1:-1, 2:] |
            p[2:, :-2]  | p[2:, 1:-1]  | p[2:, 2:]
        )
        new_edges = weak & neighbor_strong & (~edges)
        if not np.any(new_edges):
            break
        edges |= new_edges

    return _to_rgb_uint8(edges.astype(np.float32) * 255.0)

# --- 3. COMPASS EDGE DETECTION (KIRSCH 8-DIRECTION) ---

def apply_compass(img: np.ndarray) -> np.ndarray:
    """Deteksi tepi Compass menggunakan 8 kernel arah Kirsch."""
    gray = _to_gray_float(img)
    kirsch_kernels = [
        np.array([[ 5,  5,  5], [-3, 0, -3], [-3, -3, -3]], dtype=np.float32),
        np.array([[ 5,  5, -3], [ 5, 0, -3], [-3, -3, -3]], dtype=np.float32),
        np.array([[ 5, -3, -3], [ 5, 0, -3], [ 5, -3, -3]], dtype=np.float32),
        np.array([[-3, -3, -3], [ 5, 0, -3], [ 5,  5, -3]], dtype=np.float32),
        np.array([[-3, -3, -3], [-3, 0, -3], [ 5,  5,  5]], dtype=np.float32),
        np.array([[-3, -3, -3], [-3, 0,  5], [-3,  5,  5]], dtype=np.float32),
        np.array([[-3, -3,  5], [-3, 0,  5], [-3, -3,  5]], dtype=np.float32),
        np.array([[-3,  5,  5], [-3, 0,  5], [-3, -3, -3]], dtype=np.float32),
    ]
    max_response = np.zeros_like(gray)
    for k in kirsch_kernels:
        np.maximum(max_response, _convolve2d(gray, k), out=max_response)
    return _to_rgb_uint8(max_response)