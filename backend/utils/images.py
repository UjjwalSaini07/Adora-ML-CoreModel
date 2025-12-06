from pathlib import Path
from typing import Tuple
from PIL import Image
import io

from ..config import MAX_FILE_SIZE_BYTES

def load_image(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")

def save_with_size_limit(img: Image.Image, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    quality = 95
    fmt = "JPEG" if dest.suffix.lower() in [".jpg", ".jpeg"] else "PNG"
    while quality >= 30:
        buf = io.BytesIO()
        if fmt == "JPEG":
            img.convert("RGB").save(buf, format=fmt, quality=quality, optimize=True)
        else:
            img.save(buf, format=fmt, optimize=True)
        size = buf.tell()
        if size <= MAX_FILE_SIZE_BYTES:
            with open(dest, "wb") as f:
                f.write(buf.getvalue())
            return size
        quality -= 10
    # Fallback: save whatever we have
    with open(dest, "wb") as f:
        f.write(buf.getvalue())
    return size

def resize_to_fit(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
    return img.resize(size, Image.LANCZOS)
