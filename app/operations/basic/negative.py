import numpy as np

def apply_negative(img: np.ndarray) -> np.ndarray:
    """Membuat citra negatif: s = 255 - r."""
    return 255 - img