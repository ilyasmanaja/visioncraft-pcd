import numpy as np
from app.operations.basic.colouring import to_grayscale

def apply_thresholding(img: np.ndarray, thresh_val: int = 128) -> np.ndarray:
    """Operasi thresholding biner dengan nilai batas yang dapat disesuaikan."""
    gray = to_grayscale(img)[:, :, 0]
    result = np.where(gray >= thresh_val, 255, 0).astype(np.uint8)
    return np.stack([result, result, result], axis=-1)
