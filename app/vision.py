import io, numpy as np
from PIL import Image
import pytesseract
from rembg import remove
from ultralytics import YOLO

yolo_model = YOLO('yolov8n.pt')  # small model for speed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def remove_background_bytes(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    out = remove(img)  # returns PIL Image
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()

def ocr_image_bytes(image_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    text = pytesseract.image_to_string(img)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    return {"text": text, "data": data}

def run_yolo_bytes(image_bytes: bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = yolo_model(np.array(img))
    # results is a list; take first
    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            label = yolo_model.model.names[cls]
            detections.append({"label": label, "conf": conf, "xyxy": xyxy})
    return detections
