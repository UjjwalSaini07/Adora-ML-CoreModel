from typing import List, Dict
from PIL import Image

try:
    from ultralytics import YOLO
    _model = YOLO("yolov8n.pt")  # light model
except Exception:
    _model = None

def detect_person_and_objects(image: Image.Image) -> List[Dict]:
    """Run YOLOv8 detection. Returns list of {label, conf, box}.
    If YOLO is not available, returns an empty list.
    """
    if _model is None:
        return []
    results = _model(image)
    out = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls)
            label = r.names[cls]
            conf = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            out.append(
                {"label": label, "conf": conf, "box": [x1, y1, x2, y2]}
            )
    return out
