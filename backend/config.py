from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

DB_PATH = DATA_DIR / "retail_tool.db"
AUDIT_LOG_DIR = DATA_DIR / "audit_logs"
AUDIT_LOG_DIR.mkdir(exist_ok=True, parents=True)

# Example creative sizes (width, height)
CREATIVE_SIZES = {
    "story": (1080, 1920),
    "feed": (1080, 1080),
    "banner": (1200, 628),
}

MAX_FILE_SIZE_BYTES = 500 * 1024  # 500 KB

# LLM / SD feature flags
# USE_OLLAMA = False  # set True + configure in models/llm_client.py
# ENABLE_SD = False   # set True after configuring sd_client.py
USE_OLLAMA = True
ENABLE_SD = True
