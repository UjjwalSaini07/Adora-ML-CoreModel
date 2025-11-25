from PIL import ImageStat, Image
from app.utils import contrast_ratio, sample_pixel, sample_box_average, make_audit_entry
import math

def check_safe_zone(element_box, format_name="Story"):
    # Story format: top safe zone y >= 200px (example from spec)
    x, y, w, h = element_box

    if format_name == "Story":
        if y < 200:
            return make_audit_entry(
                "safe_zone",
                False,
                f"Element y={y} in top safe zone < 200"
            )

    return make_audit_entry("safe_zone", True, "OK")


def check_font_size(font_px, min_px=20):
    ok = font_px >= min_px
    return make_audit_entry(
        "font_size",
        ok,
        f"font {font_px}px < min {min_px}px" if not ok else "OK"
    )


def check_contrast_text_on_bg(text_rgb, bg_sample_rgb, min_ratio=4.5):
    ratio = contrast_ratio(text_rgb, bg_sample_rgb)

    return make_audit_entry(
        "contrast",
        ratio >= min_ratio,
        f"Contrast {ratio:.2f} < {min_ratio}" if ratio < min_ratio else "OK",
        meta={"ratio": round(ratio, 2)}
    )


def run_all_rules(image, candidate):
    """
    Unified rule evaluator used by autofix.py
    """
    box = candidate["box"]
    font_px = candidate["font_px"]
    text_color = candidate["color_rgb"]

    # sample background behind text
    bg = sample_box_average(image, box)

    results = {
        "hard": [
            check_safe_zone(box, candidate.get("format", "Story")),
            check_font_size(font_px),
            check_contrast_text_on_bg(text_color, bg)
        ]
    }

    return results
