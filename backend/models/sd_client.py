import os
from typing import Optional
from PIL import Image
import io

ENABLE_SD = bool(os.getenv("ENABLE_SD", "0") == "1")

try:
    if ENABLE_SD:
        from diffusers import StableDiffusionPipeline
        import torch
        SD_MODEL_ID = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = StableDiffusionPipeline.from_pretrained(
            SD_MODEL_ID,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        )
        pipe = pipe.to(device)
    else:
        pipe = None
except Exception:
    pipe = None
    ENABLE_SD = False

def generate_background(prompt: str, size=(1080, 1920)) -> Optional[Image.Image]:
    """Generate a background image using Stable Diffusion or return None if disabled."""
    if pipe is None:
        return None
    image = pipe(prompt).images[0]
    return image.resize(size)
