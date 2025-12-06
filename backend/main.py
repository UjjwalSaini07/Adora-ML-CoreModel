from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (
    CreativeCanvas,
    ValidationResult,
    AutoFixRequest,
    AutoFixResponse,
    RenderRequest,
    RenderResponse,
    RenderedCreative,
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
from pathlib import Path
from PIL import Image

app = FastAPI(title="Retail Media Creative Tool Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/validate", response_model=ValidationResult)
def validate(canvas: CreativeCanvas):
    # TODO: wire real image paths and load them; here we just run layout rules.
    result = run_rules(canvas)

    # Semantic banned phrase check via LLM (stub or Ollama)
    texts = [tb.text for tb in canvas.text_blocks]
    warnings = semantic_banned_check(texts)
    for w in warnings:
        result.issues.append(
            type(result).issues.type_(__root__=None)  # hack, but we will append manually below
        )
    # Actually append properly
    from .schemas import ValidationIssue
    for w in warnings:
        result.issues.append(
            ValidationIssue(code="SEMANTIC_WARNING", message=w, severity="warning")
        )
    return result

@app.post("/autofix", response_model=AutoFixResponse)
def autofix(req: AutoFixRequest):
    fixed_canvas, val, fixes = hill_climb_autofix(req.canvas)
    return AutoFixResponse(canvas=fixed_canvas, applied_fixes=fixes, validation=val)

@app.post("/render", response_model=RenderResponse)
def render(req: RenderRequest):
    creatives = []
    all_issues = []
    for fmt in req.formats:
        size = CREATIVE_SIZES.get(fmt, CREATIVE_SIZES["story"])
        # For simplicity render a blank canvas with text overlays.
        img = Image.new("RGBA", size, (255, 255, 255, 255))
        # Optionally generate SD background
        bg = generate_background("retail promo background, soft gradients", size=size)
        if bg is not None:
            img = bg.convert("RGBA")

        # TODO: draw text, packshots etc. Here we just keep blank for demo.
        out_dir = DATA_DIR / "renders"
        out_path = out_dir / f"{req.canvas.id}_{fmt}.jpg"
        size_bytes = save_with_size_limit(img, out_path)
        creatives.append(RenderedCreative(format=fmt, path=str(out_path), size_bytes=size_bytes))

    # After rendering, we can log validation again
    val = run_rules(req.canvas)
    all_issues.extend(val.issues)
    audit_path = write_audit_log(req.canvas.id, all_issues, fixes=[])
    return RenderResponse(creatives=creatives, audit_log_path=str(audit_path))
