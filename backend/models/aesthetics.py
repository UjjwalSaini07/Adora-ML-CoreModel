from ..schemas import CreativeCanvas

def aesthetic_score(canvas: CreativeCanvas) -> float:
    """
    Very simple heuristic aesthetic scorer stub.
    Replace with CNN/MobileNet-based scorer later.
    Returns a float in [0, 1].
    """
    score = 0.5
    score += max(0, 0.3 - 0.05 * len(canvas.text_blocks))
    if len(canvas.packshot_ids) == 1:
        score += 0.1
    return max(0.0, min(1.0, score))
