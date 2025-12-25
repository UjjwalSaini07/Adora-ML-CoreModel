import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def semantic_banned_check(texts: list[str]) -> list[str]:
    if not texts:
        return []

    prompt = (
        "You are a moderation system.\n"
        "Check the following texts for banned or unsafe content.\n"
        "Return a JSON array of warnings.\n\n"
        f"Texts:\n{texts}"
    )

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,  # increased timeout
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", [])
    except requests.exceptions.RequestException:
        # Never crash backend
        return []
