import numpy as np

def apply_gaussian_noise(img: np.ndarray, mean: float = 0.0, sigma: float = 25.0) -> np.ndarray:
    """Menambahkan Gaussian Noise: z ~ N(mean, sigma^2)."""
    rng = np.random.default_rng()
    noise = rng.normal(float(mean), float(sigma), img.shape)
    noisy_img = img.astype(np.float32) + noise
    return np.clip(noisy_img, 0, 255).astype(np.uint8)

def apply_rayleigh_noise(img: np.ndarray, scale: float = 30.0) -> np.ndarray:
    """Menambahkan Rayleigh Noise menggunakan inverse transform: z = scale * sqrt(-2 * ln(1 - U))."""
    rng = np.random.default_rng()
    u = rng.uniform(1e-7, 1.0 - 1e-7, img.shape)
    noise = float(scale) * np.sqrt(-2.0 * np.log(1.0 - u))
    noisy_img = img.astype(np.float32) + noise
    return np.clip(noisy_img, 0, 255).astype(np.uint8)

def apply_erlang_noise(img: np.ndarray, scale: float = 15.0, shape_k: int = 2) -> np.ndarray:
    """Menambahkan Erlang (Gamma) Noise: penjumlahan k variabel acak eksponensial."""
    rng = np.random.default_rng()
    k = max(1, int(shape_k))
    u = rng.uniform(1e-7, 1.0 - 1e-7, (*img.shape, k))
    # z = -scale * sum(ln(1 - U_i))
    noise = -float(scale) * np.sum(np.log(1.0 - u), axis=-1)
    noisy_img = img.astype(np.float32) + noise
    return np.clip(noisy_img, 0, 255).astype(np.uint8)

def apply_exponential_noise(img: np.ndarray, scale: float = 25.0) -> np.ndarray:
    """Menambahkan Exponential Noise: z = -scale * ln(1 - U)."""
    rng = np.random.default_rng()
    u = rng.uniform(1e-7, 1.0 - 1e-7, img.shape)
    noise = -float(scale) * np.log(1.0 - u)
    noisy_img = img.astype(np.float32) + noise
    return np.clip(noisy_img, 0, 255).astype(np.uint8)

def apply_uniform_noise(img: np.ndarray, low: float = -40.0, high: float = 40.0) -> np.ndarray:
    """Menambahkan Uniform Noise pada rentang [low, high]."""
    rng = np.random.default_rng()
    a, b = float(low), float(high)
    if a > b:
        a, b = b, a
    noise = rng.uniform(a, b, img.shape)
    noisy_img = img.astype(np.float32) + noise
    return np.clip(noisy_img, 0, 255).astype(np.uint8)

def apply_impulse_noise(img: np.ndarray, prob: float = 0.05) -> np.ndarray:
    """Menambahkan Impulse Noise (Salt & Pepper) dengan probabilitas total prob."""
    rng = np.random.default_rng()
    p = np.clip(float(prob), 0.0, 1.0)
    output = img.copy()
    
    # Bangkitkan matriks probabilitas 2D (H, W) agar piksel RGB berubah seragam menjadi hitam/putih
    h, w, _ = img.shape
    rand_map = rng.random((h, w))
    
    # Pepper (0) & Salt (255)
    output[rand_map < (p / 2.0)] = 0
    output[rand_map > (1.0 - p / 2.0)] = 255
    return output