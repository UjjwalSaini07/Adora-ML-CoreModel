import os
import requests
from typing import List

# USE_OLLAMA = bool(os.getenv("USE_OLLAMA", "0") == "1")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
USE_OLLAMA = True
OLLAMA_MODEL = "llama3"


def semantic_banned_check(texts: List[str]) -> List[str]:
    """Ask LLaMA (via Ollama) if any text violates soft 'banned' semantics.
    Returns list of human-readable warnings. Uses a stub if Ollama not enabled.
    """
    joined = "\n".join(texts)
    if not USE_OLLAMA:
        # Stub: simple keyword check as fallback
        banned_keywords = ["eco-friendly", "win", "guarantee", "carbon neutral"]
        found = [kw for kw in banned_keywords if kw.lower() in joined.lower()]
        if not found:
            return []
        return [f"Found potentially banned phrases: {', '.join(found)}"]
    prompt = f"""You are a compliance checker for retail ads.
Text:
{joined}

Return a short bullet list of any phrases that look like:
- competitions or 'win'
- guarantees
- sustainability or eco claims

Return 'OK' if nothing problematic."""
    resp = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }, timeout=60)
    data = resp.json()
    content = data.get("response", "").strip()
    if content.upper().startswith("OK"):
        return []
    return [line.strip(" -") for line in content.splitlines() if line.strip()]
