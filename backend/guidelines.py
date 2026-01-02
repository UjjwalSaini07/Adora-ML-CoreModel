import re
from typing import Dict, List, Optional
import cv2
import pytesseract
import numpy as np
from PIL import Image
import colorsys

# Enhanced forbidden terms with categories
FORBIDDEN_COPY_TERMS = {
    'guarantees': ['guarantee', 'guaranteed', 'money-back', 'refund', '100%'],
    'sustainability': ['sustainable', 'green', 'eco-friendly', 'environmentally friendly', 'carbon neutral'],
    'competitions': ['competition', 'win', 'won', 'winner', 'award', 'prize', 'enter to win'],
    'health_claims': ['healthy', 'nutritious', 'low-fat', 'organic', 'natural'],
    'exclusivity': ['exclusive', 'limited time', 'only', 'never before']
}

ALLOWED_TAGS = [
    'Only at Tesco',
    'Available at Tesco',
    'Selected stores. While stocks last',
    'Available in selected stores. Clubcard/app required. Ends DD/MM',
    'Clubcard Price',
    'Tesco Clubcard',
    'Valid until DD/MM/YYYY'
]

# Platform-specific requirements
PLATFORM_REQUIREMENTS = {
    'instagram_story': {
        'aspect_ratio': (9, 16),
        'safe_zones': {'top': 200, 'bottom': 250, 'sides': 100},
        'min_font_size': 24
    },
    'instagram_feed': {
        'aspect_ratio': (1, 1),
        'safe_zones': {'all': 150},
        'min_font_size': 20
    },
    'facebook_banner': {
        'aspect_ratio': (1200, 628),
        'safe_zones': {'all': 50},
        'min_font_size': 18
    }
}

# Brand color palette (Tesco colors in RGB)
BRAND_COLORS = {
    'tesco_blue': (0, 84, 159),
    'tesco_dark_blue': (0, 34, 68),
    'tesco_red': (220, 36, 48),
    'tesco_white': (255, 255, 255)
}

def _contains_forbidden(text: str) -> Dict[str, List[str]]:
    """Check for forbidden terms and return categories found"""
    if not text:
        return {}
    t = text.lower()
    found = {}
    for category, terms in FORBIDDEN_COPY_TERMS.items():
        found_terms = [term for term in terms if term in t]
        if found_terms:
            found[category] = found_terms
    return found

def _check_text_length(text: str, max_length: int, field_name: str) -> Optional[Dict]:
    """Check text length constraints"""
    if len(text) > max_length:
        return {
            'type': 'warning',
            'msg': f'{field_name} exceeds recommended length ({len(text)}/{max_length} characters).'
        }
    return None

def _check_brand_colors(image: np.ndarray) -> List[Dict]:
    """Check if image contains brand colors"""
    issues = []
    try:
        # Convert to RGB if needed
        if image.shape[2] == 3:
            # Get dominant colors (simple approach)
            pixels = image.reshape(-1, 3)
            unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
            dominant_colors = unique_colors[np.argsort(counts)[-5:]]  # Top 5 colors

            brand_found = False
            for color in dominant_colors:
                for brand_name, brand_rgb in BRAND_COLORS.items():
                    # Simple color distance check
                    distance = np.sqrt(np.sum((color - np.array(brand_rgb))**2))
                    if distance < 50:  # Threshold for color similarity
                        brand_found = True
                        break
                if brand_found:
                    break

            if not brand_found:
                issues.append({
                    'type': 'warning',
                    'msg': 'Brand colors not detected. Consider incorporating Tesco blue or red.'
                })
    except Exception as e:
        issues.append({
            'type': 'warning',
            'msg': f'Color analysis failed: {str(e)}'
        })

    return issues

def _check_contrast_and_readability(image: np.ndarray) -> List[Dict]:
    """Check text contrast and readability"""
    issues = []
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Calculate contrast
        contrast = gray.std()

        if contrast < 30:
            issues.append({
                'type': 'warning',
                'msg': 'Low contrast detected. Text may be hard to read.'
            })

        # Check for high brightness (washed out)
        brightness = np.mean(gray)
        if brightness > 200:
            issues.append({
                'type': 'warning',
                'msg': 'Image appears washed out. Consider increasing contrast.'
            })

    except Exception as e:
        issues.append({
            'type': 'warning',
            'msg': f'Contrast analysis failed: {str(e)}'
        })

    return issues

def validate_creative_rules(payload: Dict, platform: str = 'general') -> List[Dict]:
    issues = []
    tags = payload.get('tags', '') or ''
    headline = payload.get('headline', '') or ''
    subhead = payload.get('subhead', '') or ''
    caveat = payload.get('caveat', '') or ''
    description = payload.get('description', '') or ''

    # Length checks
    length_checks = [
        (headline, 40, 'Headline'),
        (subhead, 80, 'Subheadline'),
        (description, 150, 'Description'),
        (tags, 50, 'Tags')
    ]

    for text, max_len, field in length_checks:
        check = _check_text_length(text, max_len, field)
        if check:
            issues.append(check)

    # Alcohol content check
    alcohol_triggers = ['alcohol', 'wine', 'beer', 'spirit', 'vodka', 'whisky', 'whiskey', 'cider', 'lager', 'ale']
    all_text = f"{tags} {headline} {subhead} {description}".lower()
    if any(trigger in all_text for trigger in alcohol_triggers):
        if 'drinkaware' not in caveat.lower():
            issues.append({
                'type': 'hard_fail',
                'msg': 'Alcohol-related content requires Drinkaware disclaimer.',
                'category': 'legal'
            })

    # Forbidden terms check
    all_texts = [headline, subhead, caveat, description]
    for text, field_name in zip(all_texts, ['Headline', 'Subheadline', 'Caveat', 'Description']):
        forbidden = _contains_forbidden(text)
        if forbidden:
            for category, terms in forbidden.items():
                issues.append({
                    'type': 'hard_fail',
                    'msg': f'Forbidden {category.replace("_", " ")} terms in {field_name}: {", ".join(terms)}',
                    'category': 'compliance'
                })

    # Tags validation
    if tags:
        allowed_found = any(at.lower() in tags.lower() for at in ALLOWED_TAGS)
        if not allowed_found:
            issues.append({
                'type': 'hard_fail',
                'msg': f'Tags must be one of: {", ".join(ALLOWED_TAGS)}',
                'category': 'brand'
            })

    # Platform-specific checks
    if platform in PLATFORM_REQUIREMENTS:
        req = PLATFORM_REQUIREMENTS[platform]
        issues.append({
            'type': 'info',
            'msg': f'Platform: {platform.replace("_", " ").title()} - Aspect ratio {req["aspect_ratio"][0]}:{req["aspect_ratio"][1]}, min font {req["min_font_size"]}px',
            'category': 'guidance'
        })

    # General accessibility and best practices
    issues.extend([
        {
            'type': 'warning',
            'msg': f'Accessibility: Ensure minimum font size >= {PLATFORM_REQUIREMENTS.get(platform, {}).get("min_font_size", 20)}px',
            'category': 'accessibility'
        },
        {
            'type': 'info',
            'msg': 'Best practice: Include clear call-to-action in headline or subheadline',
            'category': 'guidance'
        },
        {
            'type': 'info',
            'msg': 'Brand consistency: Use Tesco brand colors and maintain consistent tone',
            'category': 'brand'
        }
    ])

    return issues

def validate_image_guidelines(image_path: str, platform: str = 'general') -> List[Dict]:
    issues = []
    try:
        img = cv2.imread(image_path)
        if img is None:
            issues.append({
                'type': 'hard_fail',
                'msg': 'Unable to load image for validation.',
                'category': 'technical'
            })
            return issues

        height, width = img.shape[:2]
        aspect_ratio = height / width

        # Platform-specific aspect ratio check
        if platform in PLATFORM_REQUIREMENTS:
            req = PLATFORM_REQUIREMENTS[platform]
            expected_ar = req['aspect_ratio'][1] / req['aspect_ratio'][0]  # height/width
            ar_diff = abs(aspect_ratio - expected_ar) / expected_ar

            if ar_diff > 0.1:  # 10% tolerance
                issues.append({
                    'type': 'warning',
                    'msg': f'Aspect ratio {aspect_ratio:.2f} doesn\'t match {platform.replace("_", " ")} requirements ({req["aspect_ratio"][0]}:{req["aspect_ratio"][1]} = {expected_ar:.2f})',
                    'category': 'format'
                })

            # Safe zone checks
            safe_zones = req['safe_zones']
            if 'all' in safe_zones:
                margin = safe_zones['all']
                zones_to_check = [
                    ('top', img[:margin, :]),
                    ('bottom', img[height-margin:, :]),
                    ('left', img[:, :margin]),
                    ('right', img[:, width-margin:])
                ]
            else:
                zones_to_check = []
                if 'top' in safe_zones:
                    zones_to_check.append(('top', img[:safe_zones['top'], :]))
                if 'bottom' in safe_zones:
                    zones_to_check.append(('bottom', img[height-safe_zones['bottom']:, :]))
                if 'sides' in safe_zones:
                    zones_to_check.extend([
                        ('left', img[:, :safe_zones['sides']]),
                        ('right', img[:, width-safe_zones['sides']:])
                    ])

            for zone_name, zone in zones_to_check:
                if _has_content_in_zone(zone):
                    issues.append({
                        'type': 'warning',
                        'msg': f'{zone_name.title()} safe zone ({safe_zones.get(zone_name, safe_zones.get("all", 0))}px) may contain text/logos.',
                        'category': 'layout'
                    })

        # OCR for text detection and analysis
        pil_img = Image.open(image_path)
        text = pytesseract.image_to_string(pil_img)

        if text.strip():
            issues.append({
                'type': 'info',
                'msg': f'Text detected in image: "{text.strip()[:100]}..."',
                'category': 'content'
            })

            # Check font size (rough estimate)
            # This is a simplified check - in production, you'd use more sophisticated OCR
            text_lines = text.strip().split('\n')
            if len(text_lines) > 0:
                avg_line_length = sum(len(line) for line in text_lines) / len(text_lines)
                estimated_font_size = min(50, max(12, int(100 / avg_line_length)))  # Rough estimation

                min_font = PLATFORM_REQUIREMENTS.get(platform, {}).get('min_font_size', 20)
                if estimated_font_size < min_font:
                    issues.append({
                        'type': 'warning',
                        'msg': f'Estimated font size ({estimated_font_size}px) below minimum ({min_font}px) for {platform.replace("_", " ")}',
                        'category': 'accessibility'
                    })

            # Check for forbidden terms in image text
            forbidden = _contains_forbidden(text)
            if forbidden:
                for category, terms in forbidden.items():
                    issues.append({
                        'type': 'hard_fail',
                        'msg': f'Forbidden {category.replace("_", " ")} terms in image text: {", ".join(terms)}',
                        'category': 'compliance'
                    })

        # Color and contrast analysis
        issues.extend(_check_brand_colors(img))
        issues.extend(_check_contrast_and_readability(img))

        # Image quality checks
        file_size_kb = len(open(image_path, 'rb').read()) / 1024
        if file_size_kb > 500:
            issues.append({
                'type': 'warning',
                'msg': f'Large file size ({file_size_kb:.1f}KB). Consider optimization for web delivery.',
                'category': 'performance'
            })

        # Resolution check
        min_resolution = 1000  # pixels
        if width < min_resolution or height < min_resolution:
            issues.append({
                'type': 'warning',
                'msg': f'Low resolution ({width}x{height}). Minimum recommended: {min_resolution}px on shortest side.',
                'category': 'quality'
            })

    except Exception as e:
        issues.append({
            'type': 'warning',
            'msg': f'Image validation failed: {str(e)}',
            'category': 'technical'
        })

    return issues

def _has_content_in_zone(zone: np.ndarray, threshold: int = 1000) -> bool:
    """Check if a zone contains significant content (text/logos)"""
    try:
        gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        return np.sum(thresh) > threshold
    except:
        return False
