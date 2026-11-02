from flask import Blueprint, request, jsonify
from app.utils.image_io import decode_base64_to_cv, encode_cv_to_base64
from app.operations.basic.negative import apply_negative
from app.operations.basic.colouring import (
    to_grayscale, to_binary, to_cmy, to_hsv_vis, to_yuv, to_yiq, to_pseudo
)
from app.operations.basic.thresholding import apply_thresholding
from app.operations.basic.geometrics import (
    apply_translation, apply_rotation, apply_zooming, apply_flipping, apply_cropping
)
from app.operations.basic.arithmetic_boolean import (
    apply_add, apply_subtract, apply_multiply, apply_divide,
    apply_not, apply_and, apply_or, apply_xor
)
from app.operations.basic.transforms import (
    apply_convolution, apply_fourier_transform
)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/process', methods=['POST'])
def process_image():
    try:
        data = request.get_json(silent=True)
        if not data or 'image' not in data:
            return jsonify({'ok': False, 'message': 'Payload tidak valid atau gambar tidak ditemukan.'}), 400

        operation = data.get('operation')
        params = data.get('params', {})
        img = decode_base64_to_cv(data['image'])

        img2 = None
        if 'image2' in data and data['image2']:
            img2 = decode_base64_to_cv(data['image2'])

        # 1. Operasi Titik & Warna
        if operation == 'basic.negative':
            result_img = apply_negative(img)
        elif operation == 'basic.colouring.gray':
            result_img = to_grayscale(img)
        elif operation == 'basic.colouring.binary':
            result_img = to_binary(img, threshold=int(params.get('threshold', 128)))
        elif operation == 'basic.colouring.rgb':
            result_img = img
        elif operation == 'basic.colouring.cmy':
            result_img = to_cmy(img)
        elif operation == 'basic.colouring.hsv':
            result_img = to_hsv_vis(img)
        elif operation == 'basic.colouring.yuv':
            result_img = to_yuv(img)
        elif operation == 'basic.colouring.yiq':
            result_img = to_yiq(img)
        elif operation == 'basic.colouring.pseudo':
            result_img = to_pseudo(img)
        elif operation == 'basic.thresholding':
            thresh_val = int(params.get('threshold', 128))
            result_img = apply_thresholding(img, thresh_val=thresh_val)

        # 2. Operasi Geometris
        elif operation == 'basic.geometrics.translation':
            tx = int(params.get('tx', 50))
            ty = int(params.get('ty', 50))
            result_img = apply_translation(img, tx=tx, ty=ty)
        elif operation == 'basic.geometrics.rotation':
            angle = float(params.get('angle', 90))
            result_img = apply_rotation(img, angle=angle)
        elif operation == 'basic.geometrics.zooming':
            scale = float(params.get('scale', 1.5))
            result_img = apply_zooming(img, scale=scale)
        elif operation == 'basic.geometrics.flipping':
            mode = params.get('mode', 'horizontal')
            result_img = apply_flipping(img, mode=mode)
        elif operation == 'basic.geometrics.cropping':
            x = int(params.get('x', 0))
            y = int(params.get('y', 0))
            w = int(params.get('width', 200))
            h = int(params.get('height', 200))
            result_img = apply_cropping(img, x=x, y=y, width=w, height=h)

        # 3. Operasi Aritmatika & Boolean
        elif operation == 'basic.boolean.not':
            result_img = apply_not(img)
        elif operation in ['basic.arithmetic.add', 'basic.arithmetic.subtract', 'basic.arithmetic.multiply', 'basic.arithmetic.divide',
                           'basic.boolean.and', 'basic.boolean.or', 'basic.boolean.xor']:
            if img2 is None:
                return jsonify({'ok': False, 'message': 'Operasi ini membutuhkan gambar kedua.'}), 400
            
            if operation == 'basic.arithmetic.add':
                result_img = apply_add(img, img2)
            elif operation == 'basic.arithmetic.subtract':
                result_img = apply_subtract(img, img2)
            elif operation == 'basic.arithmetic.multiply':
                result_img = apply_multiply(img, img2)
            elif operation == 'basic.arithmetic.divide':
                result_img = apply_divide(img, img2)
            elif operation == 'basic.boolean.and':
                result_img = apply_and(img, img2)
            elif operation == 'basic.boolean.or':
                result_img = apply_or(img, img2)
            elif operation == 'basic.boolean.xor':
                result_img = apply_xor(img, img2)

        # 4. Operasi Konvolusi & Transformasi Fourier
        elif operation == 'basic.convolution':
            kernel_type = params.get('kernel', 'sharpen')
            result_img = apply_convolution(img, kernel_type=kernel_type)
        elif operation == 'basic.fourier':
            result_img = apply_fourier_transform(img)

        else:
            return jsonify({'ok': False, 'message': f'Operasi {operation} belum diimplementasikan.'}), 400

        return jsonify({
            'ok': True,
            'image': encode_cv_to_base64(result_img),
            'message': 'Pemrosesan berhasil.'
        })

    except Exception as e:
        return jsonify({'ok': False, 'message': str(e)}), 500