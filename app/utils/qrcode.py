import io
import qrcode
from fastapi.responses import Response


def generate_qr_code(data: str):

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, kind="PNG")

    return Response(content=buffer.getvalue(), media_type="image/png")
