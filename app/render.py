from PIL import Image, ImageDraw, ImageFont
from app.utils import clamp
import io

def render_canvas(base_bg_bytes, packshot_png_bytes, elements, output_format='JPEG', max_kb=500):
    bg = Image.open(io.BytesIO(base_bg_bytes)).convert("RGB")
    pack = Image.open(io.BytesIO(packshot_png_bytes)).convert("RGBA")
    # simple center paste packshot
    bg.paste(pack, (100,100), mask=pack)
    draw = ImageDraw.Draw(bg)
    # draw elements: assume one headline element
    for el in elements:
        x,y,w,h = el["box"]
        font = ImageFont.truetype("DejaVuSans.ttf", el["font_px"])
        draw.text((x,y), el["text"], font=font, fill=el["color_rgb"])
    # compress loop to be <= max_kb
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
