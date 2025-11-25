from PIL import ImageStat, Image
from app.utils import contrast_ratio, sample_pixel, sample_box_average, make_audit_entry
import math

def contrast_ratio(rgb1, rgb2):
    # luminance calc per WCAG
    def lum(c):
        c = [x/255.0 for x in c]
        def adjust(v):
            return v/12.92 if v <= 0.03928 else ((v+0.055)/1.055)**2.4
        r,g,b = map(adjust,c)
        return 0.2126*r + 0.7152*g + 0.0722*b
    L1, L2 = lum(rgb1), lum(rgb2)
    L1, L2 = max(L1,L2), min(L1,L2)
    return (L1 + 0.05) / (L2 + 0.05)

def check_safe_zone(element_box, format_name="Story"):
    # Story format: top safe zone y >= 200px (example from spec)
    # element_box = (x,y,w,h)
    x,y,w,h = element_box
    if format_name == "Story":
        if y < 200:
            return {"pass": False, "msg": f"Element y={y} in top safe zone < 200"}
    return {"pass": True}

def check_font_size(font_px, min_px=20):
    ok = font_px >= min_px
    return {"pass": ok, "msg": f"font {font_px}px < min {min_px}px" if not ok else "ok"}

def check_contrast_text_on_bg(text_rgb, bg_sample_rgb, min_ratio=4.5):
    ratio = contrast_ratio(text_rgb, bg_sample_rgb)
    return {"pass": ratio >= min_ratio, "ratio": round(ratio,2)}
