# Adora-ML-CoreModel

Adora ML Core Model is a lightweight yet powerful AI engine designed for automated creative validation, layout correction, and final ad rendering. Built for hackathons and real-world marketing automation, it integrates OCR, object detection, banned-phrase compliance, safe-zone checking, and auto-layout optimization into one unified pipeline ⚡. The system intelligently analyzes product packshots, detects design issues, and applies auto-fixes to produce compliant, visually appealing creatives—ready for campaigns or downstream workflows. With a clean FastAPI backend and a modern Streamlit UI 🎨, this project offers an efficient end-to-end solution for automated creative intelligence, ensuring accuracy, speed, and usability for both developers and non-technical users 🚀.

## ⭐ Key Features
- 🔍 Smart Creative Validation — OCR, YOLO detections, banned-phrase scanning, and brand-compliance logic
- 🎨 AI Auto-Fix Engine — Adjusts font size, color, contrast, and safe-zone placement automatically
- 🧠 Background Removal — Clean, transparent product cutouts using robust segmentation
- ⚡ FastAPI Backend — High-performance API endpoints for validate, autofix, render & health check
- 🖼 Render Engine — Composes final creatives with text, product packshots, and backgrounds
- 🛠 Modern Streamlit Frontend — User-friendly UI for testing, previewing, and interacting with the system
- 🚀 Modular Architecture — Easy to extend, plug-and-play components for hackathons or production use


## Commands

### Backend Fast API Commands:
```bash
  python -m venv .venv
```

```bash
  .\.venv\Scripts\Activate.ps1
```

```bash
  pip install -r requirements.txt
```

```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Streamlit Commands:
```bash
  streamlit run streamlit_app.py
```

### Tesseract Installation Commands:
```bash
  winget install -e --id UB-Mannheim.TesseractOCR
```
```bash
  Get-ChildItem "C:\Program Files" -Recurse -Filter tesseract.exe -ErrorAction SilentlyContinue
```
```bash
  tesseract --version
```
