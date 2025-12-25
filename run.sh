#!/bin/bash
echo "cd .\backend\"
echo "cd .\frontend\"

echo "python -m venv .venv"
echo ".\.venv\Scripts\Activate.ps1"
echo "pip install -r requirements.txt"
echo "python.exe -m pip install --upgrade pip"

echo "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo "streamlit run streamlit_app.py"
