import numpy as np
from PIL import Image

def apply_geometric_correction(img: np.ndarray, skew_x: float = 0.0, skew_y: float = 0.0) -> np.ndarray:
    """Koreksi geometri / affine shear untuk meluruskan distorsi kemiringan citra."""
    h, w, _ = img.shape
    pil_img = Image.fromarray(img)

    # Matriks transformasi affine terbalik untuk Pillow: (a, b, c, d, e, f)
    # x_in = a*x_out + b*y_out + c
    # y_in = d*x_out + e*y_out + f
    sx = float(skew_x)
    sy = float(skew_y)
    c_offset = -sx * (h / 2.0)
    f_offset = -sy * (w / 2.0)

    corrected = pil_img.transform(
        (w, h),
        Image.Transform.AFFINE,
        (1.0, sx, c_offset, sy, 1.0, f_offset),
        resample=Image.Resampling.BILINEAR
    )
    return np.array(corrected, dtype=np.uint8)