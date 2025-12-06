from typing import List
from ..schemas import CreativeCanvas, ValidationIssue, ValidationResult
from .presets import DEFAULT_CONFIGS

def _check_safe_zone(canvas: CreativeCanvas, cfg) -> List[ValidationIssue]:
    issues = []
    for tb in canvas.text_blocks:
        if tb.y < cfg.top_safe_zone_px:
            issues.append(ValidationIssue(
                code="SAFE_ZONE_TOP",
                message=f"Text '{tb.text[:15]}...' is in top safe zone (<{cfg.top_safe_zone_px}px).",
                severity="error",
            ))
    return issues

def _check_font_sizes(canvas: CreativeCanvas, cfg) -> List[ValidationIssue]:
    issues = []
    for tb in canvas.text_blocks:
        if tb.font_size < cfg.min_font_px:
            issues.append(ValidationIssue(
                code="FONT_TOO_SMALL",
                message=f"Text '{tb.text[:15]}...' font {tb.font_size}px < {cfg.min_font_px}px.",
                severity="error",
            ))
    return issues

def _check_packshot_count(canvas: CreativeCanvas, cfg) -> List[ValidationIssue]:
    issues = []
    if len(canvas.packshot_ids) > cfg.max_packshots:
        issues.append(ValidationIssue(
            code="TOO_MANY_PACKSHOTS",
            message=f"{len(canvas.packshot_ids)} packshots > allowed {cfg.max_packshots}.",
            severity="error",
        ))
    return issues

def run_rules(canvas: CreativeCanvas) -> ValidationResult:
    cfg = DEFAULT_CONFIGS.get(canvas.format, DEFAULT_CONFIGS["story"])
    issues: List[ValidationIssue] = []
    issues.extend(_check_safe_zone(canvas, cfg))
    issues.extend(_check_font_sizes(canvas, cfg))
    issues.extend(_check_packshot_count(canvas, cfg))
    passed = not any(i.severity == "error" for i in issues)
    return ValidationResult(canvas_id=canvas.id, issues=issues, passed=passed)
