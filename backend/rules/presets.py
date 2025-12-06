from dataclasses import dataclass

@dataclass
class GuidelineConfig:
    name: str
    top_safe_zone_px: int = 200
    min_font_px: int = 20
    min_contrast_ratio: float = 4.5
    max_packshots: int = 1

TESCO_STORY = GuidelineConfig(
    name="tesco_story",
    top_safe_zone_px=200,
    min_font_px=20,
    min_contrast_ratio=4.5,
    max_packshots=1,
)

DEFAULT_CONFIGS = {
    "story": TESCO_STORY,
    "feed": GuidelineConfig(name="tesco_feed", top_safe_zone_px=120),
    "banner": GuidelineConfig(name="tesco_banner", top_safe_zone_px=80),
}
