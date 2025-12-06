from typing import Optional
from PIL import Image
import io
try:
    from rembg import remove
except Exception:
    remove = None

def remove_background(image: Image.Image) -> Optional[Image.Image]:
    if remove is None:
        return image  # gracefully degrade
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    out = remove(buf.getvalue())
    return Image.open(io.BytesIO(out)).convert("RGBA")
