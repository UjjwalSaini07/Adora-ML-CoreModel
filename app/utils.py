"""
General utilities for:
- Color / contrast tools
- Semantic similarity w/ sentence embeddings
- Banned phrase detection
- OCR helpers
- Image sampling
- Audit utilities
"""

import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import string

# 1. Basic color utilities
def rgb_tuple(v):
    """Ensure (r, g, b) tuple."""
    if isinstance(v, tuple) and len(v) == 3:
        return v
    if isinstance(v, list) and len(v) == 3:
        return tuple(v)
    raise ValueError("Expected RGB triple")


def clamp(val, low=0, high=255):
    return max(low, min(high, val))


def luminance(rgb):
    r, g, b = [x / 255 for x in rgb]

    def adjust(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    R, G, B = adjust(r), adjust(g), adjust(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def contrast_ratio(rgb1, rgb2):
    """WCAG contrast ratio."""
    L1, L2 = luminance(rgb1), luminance(rgb2)
    L1, L2 = max(L1, L2), min(L1, L2)
    return (L1 + 0.05) / (L2 + 0.05)


# 2. OCR utilities
def normalize_text(t):
    """Lowercase, remove punctuation, collapse whitespace."""
    t = t.lower()
    t = t.translate(str.maketrans("", "", string.punctuation))
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# 3. Semantic similarity using TF-IDF (simple, fast)
def semantic_similarity(a, b):
    """
    Quick text similarity using TF-IDF vectors.
    For stronger models you can swap for sentence-transformers.
    """
    texts = [a, b]
    vec = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
    return float(sim)


# 4. Banned phrase detection
DEFAULT_BANNED = [
    "eco-friendly",
    "100% free",
    "win now",
    "guaranteed",
    "limited time",
    "deal expires",
    "best ever",
    "miracle",
    "clinically proven"
]

def detect_banned_phrases(text, banned_list=None, threshold=0.75):
    """
    Return flagged banned phrases using semantic match.
    threshold: similarity threshold
    """
    if banned_list is None:
        banned_list = DEFAULT_BANNED

    text_n = normalize_text(text)
    hits = []

    for bp in banned_list:
        sim = semantic_similarity(text_n, bp.lower())
        if sim >= threshold:
            hits.append({"phrase": bp, "similarity": sim})

    return hits


# 5. Image utilities for sampling background color
def sample_pixel(img: Image.Image, x, y):
    """
    Safe pixel sample (clamps coords into image).
    """
    xx = int(max(0, min(img.width - 1, x)))
    yy = int(max(0, min(img.height - 1, y)))
    return img.convert("RGB").getpixel((xx, yy))


def sample_box_average(img: Image.Image, box):
    """
    Average RGB inside a bounding box.
    box = (x, y, w, h)
    """
    x, y, w, h = box
    x2, y2 = x + w, y + h
    region = img.crop((x, y, x2, y2)).convert("RGB")
    arr = np.array(region)
    if arr.size == 0:
        return (128, 128, 128)
    r = arr[:, :, 0].mean()
    g = arr[:, :, 1].mean()
    b = arr[:, :, 2].mean()
    return (int(r), int(g), int(b))


# 6. Audit utilities
def make_audit_entry(rule_name, passed, msg="", meta=None):
    """Unified audit entry."""
    return {
        "rule": rule_name,
        "pass": passed,
        "msg": msg,
        "meta": meta or {}
    }


def merge_audits(*items):
    """Combine multiple audit arrays."""
    merged = []
    for it in items:
        if isinstance(it, list):
            merged.extend(it)
        else:
            merged.append(it)
    return merged


# 7. Basic bounding box utilities
def move_box(box, dx=0, dy=0):
    x, y, w, h = box
    return (x + dx, y + dy, w, h)


def scale_box(box, scale):
    x, y, w, h = box
    return (x, y, int(w * scale), int(h * scale))
