from PIL import Image, ImageOps, ImageEnhance
import os, uuid
from pathlib import Path
from rembg import remove

BASE = Path(__file__).resolve().parent.parent / "storage"

UPLOAD_DIR = BASE / "uploads"
GENERATED_DIR = BASE / "generated"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

def save_upload_file_temp(upload_file, subfolder='uploads'):
    out_dir = BASE / subfolder
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = os.path.splitext(upload_file.filename)[1] or '.png'
    out_path = UPLOAD_DIR / (str(uuid.uuid4()) + suffix)
    with open(out_path, 'wb') as f:
        f.write(upload_file.file.read())
    return str(out_path)

def remove_background(path):
    img = Image.open(path)
    img_no_bg = remove(img)
    out = GENERATED_DIR / (Path(path).stem + '_nobg.png')
    img_no_bg.save(out)
    return str(out)

def resize_image(path, width=None, height=None):
    img = Image.open(path)
    w,h = img.size
    if width and height:
        new = img.resize((int(width), int(height)), Image.LANCZOS)
    elif width:
        new = ImageOps.contain(img, (int(width), h))
    elif height:
        new = ImageOps.contain(img, (w, int(height)))
    else:
        return path
    out = Path(path).with_name(Path(path).stem + f'_resized.png')
    new.save(out)
    return str(out)

def rotate_image(path, degrees):
    img = Image.open(path)
    new = img.rotate(float(degrees), expand=True)
    out = Path(path).with_name(Path(path).stem + f'_rot{degrees}.png')
    new.save(out)
    return str(out)

def crop_image(path, left, top, right, bottom):
    img = Image.open(path)
    cropped = img.crop((left, top, right, bottom))
    out = Path(path).with_name(Path(path).stem + f'_crop{left}_{top}_{right}_{bottom}.png')
    cropped.save(out)
    return str(out)

def apply_filter(path, filter_type, value=1.0):
    img = Image.open(path)
    if filter_type == 'brightness':
        enhancer = ImageEnhance.Brightness(img)
        new = enhancer.enhance(value)
    elif filter_type == 'contrast':
        enhancer = ImageEnhance.Contrast(img)
        new = enhancer.enhance(value)
    elif filter_type == 'sharpness':
        enhancer = ImageEnhance.Sharpness(img)
        new = enhancer.enhance(value)
    else:
        return path
    out = Path(path).with_name(Path(path).stem + f'_{filter_type}{value}.png')
    new.save(out)
    return str(out)

def overlay_text(path, text, x, y, font_size=20, color=(255,255,255)):
    img = Image.open(path).convert('RGBA')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    draw.text((x, y), text, fill=color, font=font)
    out = Path(path).with_name(Path(path).stem + '_text.png')
    img.save(out)
    return str(out)
