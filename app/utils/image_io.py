import base64
import io
import numpy as np
from PIL import Image

def decode_base64_to_cv(data_url: str) -> np.ndarray:
    """Mengonversi Base64 Data URL menjadi numpy ndarray (RGB/uint8)."""
    if ',' in data_url:
        data_url = data_url.split(',')[1]
    image_bytes = base64.b64decode(data_url)
    image = Image.open(io.BytesIO(image_bytes))
    
    # Normalisasi ke format RGB bila berupa RGBA, CMYK, atau palette
    if image.mode != 'RGB':
        image = image.convert('RGB')
        
    return np.array(image, dtype=np.uint8)

def encode_cv_to_base64(image_array: np.ndarray) -> str:
    """Mengonversi numpy ndarray (uint8) menjadi Base64 Data URL PNG."""
    image_array = np.clip(image_array, 0, 255).astype(np.uint8)
    image = Image.fromarray(image_array)
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"