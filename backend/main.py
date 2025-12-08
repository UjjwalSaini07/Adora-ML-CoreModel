from pathlib import Path
from uuid import uuid4
from typing import List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw

from .schemas import (
    CreativeCanvas,
    ValidationResult,
    AutoFixRequest,
    AutoFixResponse,
    RenderRequest,
    RenderResponse,
    RenderedCreative,
    UploadedImage,
    ValidationIssue,
)
from .rules.engine import run_rules
from .models.autofix import hill_climb_autofix
from .models.llm_client import semantic_banned_check
from .models.sd_client import generate_background
from .models.bg_remove import remove_background
from .models.ocr import extract_text
from .models.detection import detect_person_and_objects
from .utils.images import save_with_size_limit, resize_to_fit
from .utils.logging_utils import write_audit_log
from .config import CREATIVE_SIZES, DATA_DIR
from .db import init_db

import io
import time
import base64
import platform
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Retail Media Creative Tool Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
def on_startup():
    init_db()

# ---------- UPLOAD ----------
@app.post("/upload", response_model=UploadedImage)
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    role: str = Form("other"),  # packshot | background | logo | other
):
    """
    Upload packshots/backgrounds/logos.
    - Saves to data/uploads/{user_id}/{image_id}.ext
    - For packshots, auto-remove background.
    - Runs OCR + detection (you can propagate results via canvas.extra on frontend).
    """
    img_id = str(uuid4())
    ext = Path(file.filename).suffix or ".png"
    user_dir = UPLOAD_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    dest = user_dir / f"{img_id}{ext}"

    raw = await file.read()
    img = Image.open(io.BytesIO(raw)).convert("RGBA")

    # background removal for packshots
    if role == "packshot":
        img = remove_background(img) or img

    img.save(dest)
    ocr_lines = extract_text(img)
    detections = detect_person_and_objects(img)
    person_present = any(d["label"] == "person" for d in detections)

    return UploadedImage(id=img_id, role=role, path=str(dest))


# ---------- VALIDATE ----------
@app.post("/validate", response_model=ValidationResult)
def validate(canvas: CreativeCanvas):
    """
    Layout + semantic validation.
    - Rule engine (safe zones, font sizes, packshots).
    - LLM-based banned-phrase semantic check (headline, body, OCR text in extra).
    - Person-detection flag via canvas.extra["person_present"] -> rights warning.
    """
    result = run_rules(canvas)

    texts: List[str] = [tb.text for tb in canvas.text_blocks]
    ocr_lines = canvas.extra.get("ocr_lines")
    if isinstance(ocr_lines, list):
        texts.extend([str(t) for t in ocr_lines])

    warnings = semantic_banned_check(texts)

    # rights warning from detection
    if canvas.extra.get("person_present") == "true":
        warnings.append(
            "Person detected in image – ensure you have usage rights/consent."
        )

    for w in warnings:
        result.issues.append(
            ValidationIssue(
                code="SEMANTIC_WARNING",
                message=w,
                severity="warning",
            )
        )

    result.passed = not any(i.severity == "error" for i in result.issues)
    return result


# ---------- AUTOFIX ----------
@app.post("/autofix", response_model=AutoFixResponse)
def autofix(req: AutoFixRequest):
    """
    Runs hill-climbing layout auto-fix:
    - nudges text blocks + adjusts font sizes
    - keeps only rule-compliant layouts
    - picks best aesthetic score
    """
    fixed_canvas, val, fixes = hill_climb_autofix(req.canvas)
    return AutoFixResponse(canvas=fixed_canvas, applied_fixes=fixes, validation=val)


# ---------- RENDER ----------
def _render_single(canvas: CreativeCanvas, fmt: str) -> Image.Image:
    size = CREATIVE_SIZES.get(fmt, CREATIVE_SIZES["story"])

    # 1) base background
    bg = None
    if canvas.background_image_id:
        bg_path = Path(canvas.background_image_id)
        if bg_path.exists():
            bg = Image.open(bg_path).convert("RGBA")

    if bg is None:
        # try SD background
        bg = generate_background(
            prompt=canvas.extra.get(
                "bg_prompt",
                "clean premium retail promo background, soft gradients, minimal",
            ),
            size=size,
        )
    if bg is None:
        bg = Image.new("RGBA", size, (240, 240, 240, 255))

    img = resize_to_fit(bg.convert("RGBA"), size)
    draw = ImageDraw.Draw(img)

    # 2) draw text blocks
    for tb in canvas.text_blocks:
        # TODO: plug real font if needed; now default PIL font
        draw.text((tb.x, tb.y), tb.text, fill=tb.color)

    pack_map = canvas.extra.get("packshot_paths") or {}
    for pid in canvas.packshot_ids:
        p_path = pack_map.get(pid)
        if not p_path:
            continue
        p = Path(p_path)
        if not p.exists():
            continue
        p_img = Image.open(p).convert("RGBA")
        pw, ph = p_img.size
        x = size[0] - pw - 40
        y = size[1] - ph - 40
        img.alpha_composite(p_img, dest=(x, y))

    return img


@app.post("/render", response_model=RenderResponse)
def render(req: RenderRequest):
    """
    Renders Story / Feed / Banner creatives.
    - Uses optional SD background.
    - Draws text + packshots.
    - Compresses to <500KB.
    - Writes audit log with all rule issues.
    """
    creatives: List[RenderedCreative] = []
    all_issues: List[ValidationIssue] = []

    out_dir = DATA_DIR / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)

    for fmt in req.formats:
        img = _render_single(req.canvas, fmt)
        out_path = out_dir / f"{req.canvas.id}_{fmt}.jpg"
        size_bytes = save_with_size_limit(img, out_path)
        creatives.append(
            RenderedCreative(format=fmt, path=str(out_path), size_bytes=size_bytes)
        )

    # validation for audit
    val = run_rules(req.canvas)
    all_issues.extend(val.issues)
    audit_path = write_audit_log(req.canvas.id, all_issues, fixes=[])

    return RenderResponse(creatives=creatives, audit_log_path=str(audit_path))


# ---------- SIMPLE HEALTH CHECK ----------
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