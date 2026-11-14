from flask import Blueprint, request, jsonify
from app.utils.image_io import decode_base64_to_cv, encode_cv_to_base64
from app.operations.basic.negative import apply_negative
from app.operations.basic.colouring import (
    to_grayscale,
    to_binary,
    to_cmy,
    to_hsv_vis,
    to_yuv,
    to_yiq,
    to_pseudo,
)
from app.operations.basic.thresholding import apply_thresholding
from app.operations.basic.geometrics import (
    apply_translation,
    apply_rotation,
    apply_zooming,
    apply_flipping,
    apply_cropping,
)
from app.operations.basic.arithmetic_boolean import (
    apply_add,
    apply_subtract,
    apply_multiply,
    apply_divide,
    apply_not,
    apply_and,
    apply_or,
    apply_xor,
)
from app.operations.basic.transforms import apply_convolution, apply_fourier_transform
from app.operations.enhancement.intensity import (
    apply_brightness,
    apply_contrast,
    apply_hist_equalization,
)
from app.operations.enhancement.spatial_filters import (
    apply_lowpass_spatial,
    apply_median_spatial,
    apply_highpass_spatial,
    apply_highboost_spatial,
)
from app.operations.enhancement.frequency_filters import (
    apply_ilpf,
    apply_blpf,
    apply_ihpf,
    apply_bhpf,
)
from app.operations.enhancement.geometric_correction import apply_geometric_correction
from app.operations.noise.generators import (
    apply_gaussian_noise,
    apply_rayleigh_noise,
    apply_erlang_noise,
    apply_exponential_noise,
    apply_uniform_noise,
    apply_impulse_noise,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/process", methods=["POST"])
def process_image():
    try:
        data = request.get_json(silent=True)
        if not data or "image" not in data:
            return (
                jsonify(
                    {
                        "ok": False,
                        "message": "Payload tidak valid atau gambar tidak ditemukan.",
                    }
                ),
                400,
            )

        operation = data.get("operation")
        params = data.get("params", {})
        img = decode_base64_to_cv(data["image"])

        img2 = None
        if "image2" in data and data["image2"]:
            img2 = decode_base64_to_cv(data["image2"])

        # 1. Operasi Titik & Warna
        if operation == "basic.negative":
            result_img = apply_negative(img)
        elif operation == "basic.colouring.gray":
            result_img = to_grayscale(img)
        elif operation == "basic.colouring.binary":
            result_img = to_binary(img, threshold=int(params.get("threshold", 128)))
        elif operation == "basic.colouring.rgb":
            result_img = img
        elif operation == "basic.colouring.cmy":
            result_img = to_cmy(img)
        elif operation == "basic.colouring.hsv":
            result_img = to_hsv_vis(img)
        elif operation == "basic.colouring.yuv":
            result_img = to_yuv(img)
        elif operation == "basic.colouring.yiq":
            result_img = to_yiq(img)
        elif operation == "basic.colouring.pseudo":
            result_img = to_pseudo(img)
        elif operation == "basic.thresholding":
            thresh_val = int(params.get("threshold", 128))
            result_img = apply_thresholding(img, thresh_val=thresh_val)

        # 2. Operasi Geometris
        elif operation == "basic.geometrics.translation":
            tx = int(params.get("tx", 50))
            ty = int(params.get("ty", 50))
            result_img = apply_translation(img, tx=tx, ty=ty)
        elif operation == "basic.geometrics.rotation":
            angle = float(params.get("angle", 90))
            result_img = apply_rotation(img, angle=angle)
        elif operation == "basic.geometrics.zooming":
            scale = float(params.get("scale", 1.5))
            result_img = apply_zooming(img, scale=scale)
        elif operation == "basic.geometrics.flipping":
            mode = params.get("mode", "horizontal")
            result_img = apply_flipping(img, mode=mode)
        elif operation == "basic.geometrics.cropping":
            x = int(params.get("x", 0))
            y = int(params.get("y", 0))
            w = int(params.get("width", 200))
            h = int(params.get("height", 200))
            result_img = apply_cropping(img, x=x, y=y, width=w, height=h)

        # 3. Operasi Aritmatika & Boolean
        elif operation == "basic.boolean.not":
            result_img = apply_not(img)
        elif operation in [
            "basic.arithmetic.add",
            "basic.arithmetic.subtract",
            "basic.arithmetic.multiply",
            "basic.arithmetic.divide",
            "basic.boolean.and",
            "basic.boolean.or",
            "basic.boolean.xor",
        ]:
            if img2 is None:
                return (
                    jsonify(
                        {
                            "ok": False,
                            "message": "Operasi ini membutuhkan gambar kedua.",
                        }
                    ),
                    400,
                )

            if operation == "basic.arithmetic.add":
                result_img = apply_add(img, img2)
            elif operation == "basic.arithmetic.subtract":
                result_img = apply_subtract(img, img2)
            elif operation == "basic.arithmetic.multiply":
                result_img = apply_multiply(img, img2)
            elif operation == "basic.arithmetic.divide":
                result_img = apply_divide(img, img2)
            elif operation == "basic.boolean.and":
                result_img = apply_and(img, img2)
            elif operation == "basic.boolean.or":
                result_img = apply_or(img, img2)
            elif operation == "basic.boolean.xor":
                result_img = apply_xor(img, img2)

        # 4. Operasi Konvolusi & Transformasi Fourier
        elif operation == "basic.convolution":
            kernel_type = params.get("kernel", "sharpen")
            result_img = apply_convolution(img, kernel_type=kernel_type)
        elif operation == "basic.fourier":
            result_img = apply_fourier_transform(img)
        # 5. Routing Menu Enhancement
        elif operation == "enhancement.brightness":
            result_img = apply_brightness(img, value=int(params.get("value", 30)))
        elif operation == "enhancement.contrast":
            result_img = apply_contrast(img, factor=float(params.get("factor", 1.5)))
        elif operation == "enhancement.hist_eq":
            result_img = apply_hist_equalization(img)
        elif operation == "enhancement.smoothing.lowpass":
            result_img = apply_lowpass_spatial(img)
        elif operation == "enhancement.smoothing.median":
            result_img = apply_median_spatial(img, ksize=int(params.get("ksize", 3)))
        elif operation == "enhancement.smoothing.ilpf":
            result_img = apply_ilpf(img, cutoff=float(params.get("cutoff", 40)))
        elif operation == "enhancement.smoothing.blpf":
            result_img = apply_blpf(
                img,
                cutoff=float(params.get("cutoff", 40)),
                order=int(params.get("order", 2)),
            )
        elif operation == "enhancement.sharpening.highpass":
            result_img = apply_highpass_spatial(img)
        elif operation == "enhancement.sharpening.highboost":
            result_img = apply_highboost_spatial(
                img, boost_a=float(params.get("boost_a", 1.5))
            )
        elif operation == "enhancement.sharpening.ihpf":
            result_img = apply_ihpf(img, cutoff=float(params.get("cutoff", 30)))
        elif operation == "enhancement.sharpening.bhpf":
            result_img = apply_bhpf(
                img,
                cutoff=float(params.get("cutoff", 30)),
                order=int(params.get("order", 2)),
            )
        elif operation == "enhancement.geom_correction":
            result_img = apply_geometric_correction(
                img,
                skew_x=float(params.get("skew_x", 0.15)),
                skew_y=float(params.get("skew_y", 0.0)),
            )

        # 6. Routing Menu Noise
        elif operation == "noise.gaussian":
            result_img = apply_gaussian_noise(
                img,
                mean=float(params.get("mean", 0.0)),
                sigma=float(params.get("sigma", 25.0)),
            )
        elif operation == "noise.rayleigh":
            result_img = apply_rayleigh_noise(
                img, scale=float(params.get("scale", 30.0))
            )
        elif operation == "noise.erlang":
            result_img = apply_erlang_noise(
                img,
                scale=float(params.get("scale", 15.0)),
                shape_k=int(params.get("shape_k", 2)),
            )
        elif operation == "noise.exponential":
            result_img = apply_exponential_noise(
                img, scale=float(params.get("scale", 25.0))
            )
        elif operation == "noise.uniform":
            result_img = apply_uniform_noise(
                img,
                low=float(params.get("low", -40.0)),
                high=float(params.get("high", 40.0)),
            )
        elif operation == "noise.impulse":
            result_img = apply_impulse_noise(img, prob=float(params.get("prob", 0.05)))
        else:
            return (
                jsonify(
                    {
                        "ok": False,
                        "message": f"Operasi {operation} belum diimplementasikan.",
                    }
                ),
                400,
            )

        return jsonify(
            {
                "ok": True,
                "image": encode_cv_to_base64(result_img),
                "message": "Pemrosesan berhasil.",
            }
        )

    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500
