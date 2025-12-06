import csv
import json
from pathlib import Path
from typing import List
from ..config import AUDIT_LOG_DIR
from ..schemas import ValidationIssue

def write_audit_log(canvas_id: str, issues: List[ValidationIssue], fixes: List[str]) -> Path:
    json_path = AUDIT_LOG_DIR / f"{canvas_id}_audit.json"
    csv_path = AUDIT_LOG_DIR / f"{canvas_id}_audit.csv"

    data = {
        "canvas_id": canvas_id,
        "issues": [i.dict() for i in issues],
        "applied_fixes": fixes,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["code", "message", "severity"])
        for i in issues:
            writer.writerow([i.code, i.message, i.severity])

    return json_path
