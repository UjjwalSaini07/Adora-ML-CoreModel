import re
from typing import Dict, List
import cv2
import pytesseract
import numpy as np
from PIL import Image

FORBIDDEN_COPY_TERMS = [
    'guarantee', 'money-back', 'sustainab', 'green', 'competition', 'win', 'won', 'award'
]

ALLOWED_TAGS = ['Only at Tesco', 'Available at Tesco', 'Selected stores. While stocks last', 'Available in selected stores. Clubcard/app required. Ends DD/MM']

def _contains_forbidden(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    for kw in FORBIDDEN_COPY_TERMS:
        if kw in t:
            return True
    return False

def validate_creative_rules(payload: Dict) -> List[Dict]:
    issues = []
    tags = payload.get('tags', '') or ''
    headline = payload.get('headline', '') or ''
    subhead = payload.get('subhead', '') or ''
    caveat = payload.get('caveat', '') or ''

    alcohol_triggers = ['alcohol', 'wine', 'beer', 'spirit', 'vodka', 'whisky', 'whiskey', 'cider']
    if any(t in (tags+headline+subhead).lower() for t in alcohol_triggers):
        if 'drinkaware' not in caveat.lower():
            issues.append({'type':'hard_fail', 'msg':'Alcohol content requires drinkaware caveat (missing or insufficient).'})
    # Forbidden claims
    if _contains_forbidden(headline) or _contains_forbidden(subhead) or _contains_forbidden(caveat):
        issues.append({'type':'hard_fail', 'msg':'Forbidden claims or sustainability/guarantee language detected.'})
    if tags:
        allowed_found = any(at.lower() in tags.lower() for at in ALLOWED_TAGS)
        if not allowed_found:
            issues.append({'type':'hard_fail', 'msg':'Tesco tag text is not one of the allowed values.'})
    issues.append({'type':'warning', 'msg':'Accessibility: ensure minimum font size >= 20px for social/brand materials.'})
    issues.append({'type':'warning', 'msg':'Social safe zone: for 9:16 stories keep 200px top and 250px bottom free from text/logos.'})

    return issues

def validate_image_guidelines(image_path: str) -> List[Dict]:
    issues = []
    try:
        img = cv2.imread(image_path)
        if img is None:
            issues.append({'type':'hard_fail', 'msg':'Unable to load image for validation.'})
            return issues
        height, width = img.shape[:2]

        # Check aspect ratio for social (assume 9:16 for stories)
        aspect = height / width
        if 1.5 < aspect < 1.9:
            top_zone = img[:200, :]
            bottom_zone = img[height-250:, :]
            def has_content(zone):
                gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
                return np.sum(thresh) > 1000  # arbitrary threshold
            if has_content(top_zone):
                issues.append({'type':'warning', 'msg':'Top safe zone (200px) may contain text/logos.'})
            if has_content(bottom_zone):
                issues.append({'type':'warning', 'msg':'Bottom safe zone (250px) may contain text/logos.'})

        # OCR for text detection
        text = pytesseract.image_to_string(Image.open(image_path))
        if text.strip():
            issues.append({'type':'warning', 'msg':'Text detected in image; ensure minimum font size >=20px.'})
            if _contains_forbidden(text):
                issues.append({'type':'hard_fail', 'msg':'Forbidden claims detected in image text.'})

    except Exception as e:
        issues.append({'type':'warning', 'msg':f'Image validation failed: {str(e)}'})

    return issues
