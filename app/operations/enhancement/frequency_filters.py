import numpy as np

def _apply_freq_filter(img: np.ndarray, filter_type: str, d0: float = 40.0, n: int = 2) -> np.ndarray:
    """Menerapkan filter domain frekuensi (ILPF, BLPF, IHPF, BHPF) pada setiap kanal RGB."""
    h, w, c = img.shape
    u = np.arange(h) - h / 2.0
    v = np.arange(w) - w / 2.0
    V, U = np.meshgrid(v, u)
    D = np.sqrt(U**2 + V**2)
    d0 = max(1.0, float(d0))

    if filter_type == 'ilpf':
        H = (D <= d0).astype(np.float32)
    elif filter_type == 'blpf':
        H = 1.0 / (1.0 + (D / d0) ** (2 * int(n)))
    elif filter_type == 'ihpf':
        H = (D > d0).astype(np.float32)
    elif filter_type == 'bhpf':
        H = 1.0 / (1.0 + (d0 / (D + 1e-8)) ** (2 * int(n)))
    else:
        H = np.ones((h, w), dtype=np.float32)

    out_channels = []
    for ch in range(c):
        f = np.fft.fft2(img[:, :, ch].astype(np.float32))
        fshift = np.fft.fftshift(f)
        filtered_shift = fshift * H
        f_ishift = np.fft.ifftshift(filtered_shift)
        img_back = np.real(np.fft.ifft2(f_ishift))
        out_channels.append(np.clip(img_back, 0, 255).astype(np.uint8))

    return np.stack(out_channels, axis=-1)

def apply_ilpf(img: np.ndarray, cutoff: float = 40.0) -> np.ndarray:
    return _apply_freq_filter(img, 'ilpf', d0=cutoff)

def apply_blpf(img: np.ndarray, cutoff: float = 40.0, order: int = 2) -> np.ndarray:
    return _apply_freq_filter(img, 'blpf', d0=cutoff, n=order)

def apply_ihpf(img: np.ndarray, cutoff: float = 30.0) -> np.ndarray:
    return _apply_freq_filter(img, 'ihpf', d0=cutoff)

def apply_bhpf(img: np.ndarray, cutoff: float = 30.0, order: int = 2) -> np.ndarray:
    return _apply_freq_filter(img, 'bhpf', d0=cutoff, n=order)