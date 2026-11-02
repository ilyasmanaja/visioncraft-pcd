import numpy as np

def apply_convolution(img: np.ndarray, kernel_type: str = 'sharpen') -> np.ndarray:
    """Konvolusi 2D 3x3 tervektorisasi murni NumPy (eksekusi instan tanpa loop per piksel)."""
    kernels = {
        'identity': np.array([[0, 0, 0],
                              [0, 1, 0],
                              [0, 0, 0]], dtype=np.float32),
        'sharpen': np.array([[ 0, -1,  0],
                             [-1,  5, -1],
                             [ 0, -1,  0]], dtype=np.float32),
        'blur': (1.0 / 9.0) * np.ones((3, 3), dtype=np.float32),
        'gaussian': (1.0 / 16.0) * np.array([[1, 2, 1],
                                             [2, 4, 2],
                                             [1, 2, 1]], dtype=np.float32),
        'ridge': np.array([[-1, -1, -1],
                           [-1,  8, -1],
                           [-1, -1, -1]], dtype=np.float32)
    }

    k = kernels.get(kernel_type, kernels['sharpen'])
    h, w, c = img.shape
    
    # Beri padding tepi 1 piksel
    pad = np.pad(img.astype(np.float32), ((1, 1), (1, 1), (0, 0)), mode='edge')

    # Akumulasi 9 irisan koordinat spasial secara vektor
    output = (
        pad[0:h, 0:w]     * k[0, 0] + pad[0:h, 1:w+1]     * k[0, 1] + pad[0:h, 2:w+2]     * k[0, 2] +
        pad[1:h+1, 0:w]   * k[1, 0] + pad[1:h+1, 1:w+1]   * k[1, 1] + pad[1:h+1, 2:w+2]   * k[1, 2] +
        pad[2:h+2, 0:w]   * k[2, 0] + pad[2:h+2, 1:w+1]   * k[2, 1] + pad[2:h+2, 2:w+2]   * k[2, 2]
    )

    return np.clip(output, 0, 255).astype(np.uint8)

def apply_fourier_transform(img: np.ndarray) -> np.ndarray:
    """Menerapkan 2D Discrete Fourier Transform (FFT) dan memvisualisasikan log magnitude."""
    gray = 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
    
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1.0)
    norm_spectrum = 255.0 * (magnitude_spectrum - np.min(magnitude_spectrum)) / (np.ptp(magnitude_spectrum) + 1e-8)
    spectrum_uint8 = np.clip(norm_spectrum, 0, 255).astype(np.uint8)
    
    return np.stack([spectrum_uint8, spectrum_uint8, spectrum_uint8], axis=-1)