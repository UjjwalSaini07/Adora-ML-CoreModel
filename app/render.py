from PIL import Image, ImageDraw, ImageFont, __file__ as pil_file
from app.utils import clamp
import io, os

FONT_PATH = "C:/Windows/Fonts/arial.ttf"

if not os.path.exists(FONT_PATH):
    FONT_PATH = os.path.join(os.path.dirname(pil_file), "fonts", "DejaVuSans.ttf")


def render_canvas(base_bg_bytes, packshot_png_bytes, elements,
                  output_format='JPEG', max_kb=500):

    bg = Image.open(io.BytesIO(base_bg_bytes)).convert("RGB")
    pack = Image.open(io.BytesIO(packshot_png_bytes)).convert("RGBA")

    bg.paste(pack, (100, 100), mask=pack)
    draw = ImageDraw.Draw(bg)

    for el in elements:
        x, y, w, h = el["box"]
        font = ImageFont.truetype(FONT_PATH, el["font_px"])
        color = tuple(clamp(c) for c in el["color_rgb"])
        draw.text((x, y), el["text"], font=font, fill=color)

    buf = io.BytesIO()
    quality = 90

    while True:
        buf.seek(0)
        bg.save(buf, format=output_format, quality=quality)
        size_kb = buf.tell() / 1024

        if size_kb <= max_kb or quality <= 20:
            break

        quality -= 5
        buf.truncate(0)

    return buf.getvalue()
