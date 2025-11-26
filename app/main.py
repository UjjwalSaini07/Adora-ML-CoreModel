import io
import time
import base64
import platform
from PIL import Image
from fastapi import FastAPI, File, UploadFile

from app.vision import remove_background_bytes, ocr_image_bytes, run_yolo_bytes, yolo_model
from app.autofix import hill_climb_autofix, simple_rules_fn
from app.render import render_canvas
from app.utils import normalize_text, detect_banned_phrases

app = FastAPI()

@app.post("/upload")
async def upload(packshot: UploadFile = File(...)):
    img_bytes = await packshot.read()
    clean = remove_background_bytes(img_bytes)
    return {"clean_bytes": len(clean)}

@app.post("/validate")
async def validate(packshot: UploadFile = File(...)):
    img_bytes = await packshot.read()
    ocr = ocr_image_bytes(img_bytes)
    yolo = run_yolo_bytes(img_bytes)

    banned = detect_banned_phrases(ocr["text"])

    return {
        "text": ocr["text"],
        "detections": yolo,
        "banned_phrases": banned
    }

@app.post("/autofix")
async def autofix(packshot: UploadFile = File(...)):
    img_bytes = await packshot.read()
    clean = remove_background_bytes(img_bytes)
    img = Image.open(io.BytesIO(clean)).convert("RGB")

    initial = {
        "box": (50, 48, 400, 40),
        "font_px": 18,
        "color_rgb": (220, 220, 220),
        "text": "Sample Headline",
        "format": "Story"
    }

    best, results = hill_climb_autofix(initial, img, simple_rules_fn)
    return {"best_candidate": best, "audit": results}

@app.post("/render")
async def render(packshot: UploadFile = File(...), background: UploadFile = File(...)):
    p = await packshot.read()
    b = await background.read()

    elements = [{
        "box": (50, 320, 400, 40),
        "font_px": 24,
        "color_rgb": (0, 0, 0),
        "text": "Rendered Headline"
    }]

    final_img = render_canvas(b, p, elements)
    encoded = base64.b64encode(final_img).decode("utf-8")
    return {
        "status": "success",
        "image_base64": encoded
    }
    # return {"render_size": len(final_img)}

@app.get("/health", tags=["Health Check"])
def health_check():
    status = {
        "status": "OK",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "python_version": platform.python_version(),
        "system": platform.system(),
        "machine": platform.machine(),
        "components": {}
    }

    # YOLO
    try:
        _ = yolo_model.names
        status["components"]["yolov8"] = "Loaded ✓"
    except:
        status["components"]["yolov8"] = "Failed ✗"

    # ONNX Runtime
    try:
        import onnxruntime
        status["components"]["onnxruntime"] = f"Available ✓ (v{onnxruntime.__version__})"
    except:
        status["components"]["onnxruntime"] = "Missing ✗"

    # OCR
    try:
        import pytesseract
        status["components"]["pytesseract"] = f"Available ✓ (v{pytesseract.get_tesseract_version()})"
    except:
        status["components"]["pytesseract"] = "Missing ✗"

    # rembg
    try:
        import rembg
        status["components"]["rembg"] = f"Available ✓ (v{rembg.__version__})"
    except:
        status["components"]["rembg"] = "Missing ✗"

    # Pillow
    try:
        from PIL import Image
        status["components"]["Pillow"] = "Available ✓"
    except:
        status["components"]["Pillow"] = "Missing ✗"

    return status
