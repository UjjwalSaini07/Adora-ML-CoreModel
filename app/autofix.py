import random
from app.rules import check_safe_zone, check_font_size, check_contrast_text_on_bg
from app.utils import sample_pixel

def score_candidate(candidate, image, rules_fn):
    # run rules and return (passes_all, soft_score)
    results = rules_fn(candidate, image)
    hard_pass = all(r["pass"] for r in results["hard"])
    soft_score = results.get("aesthetic_score", 0.5)  # placeholder
    return hard_pass, soft_score, results

def simple_rules_fn(candidate, image):
    # candidate contains element_box, font_px, color_rgb
    hard = []
    hard.append(check_safe_zone(candidate["box"], candidate.get("format","Story")))
    hard.append(check_font_size(candidate["font_px"], min_px=20))
    # sample background color behind text center (simple)
    cx = int(candidate["box"][0] + candidate["box"][2]/2)
    cy = int(candidate["box"][1] + candidate["box"][3]/2)
    bg = image.convert("RGB").getpixel((max(0,min(image.width-1,cx)), max(0,min(image.height-1,cy))))
    hard.append(check_contrast_text_on_bg(candidate["color_rgb"], bg, min_ratio=4.5))
    return {"hard": hard, "aesthetic_score": random.random()}  # aesthetic placeholder

def hill_climb_autofix(initial_candidate, image, rules_fn, budget=30):
    best = initial_candidate.copy()
    best_pass, best_score, _ = score_candidate(best, image, rules_fn)
    if best_pass:
        return best, {"note":"already passes"}
    for t in range(budget):
        cand = best.copy()
        # mutate: move y, change font, change color to black/white
        cand["box"] = (cand["box"][0], cand["box"][1] + random.randint(20,120), cand["box"][2], cand["box"][3])
        cand["font_px"] = max(10, cand["font_px"] + random.choice([-2,0,2,4]))
        cand["color_rgb"] = random.choice([(0,0,0),(255,255,255),(10,10,10)])
        pass_, score, res = score_candidate(cand, image, rules_fn)
        if pass_ and score > best_score:
            best = cand
            best_score = score
            best_pass = True
            if best_pass:
                return best, res
    return best, res
