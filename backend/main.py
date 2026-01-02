from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
from dotenv import load_dotenv
from db import init_db, save_asset, list_assets, get_asset_path, save_asset_version, get_asset_versions, add_asset_comment, get_asset_comments
from utils import save_upload_file_temp, remove_background, resize_image, rotate_image, crop_image, apply_filter, overlay_text
from guidelines import validate_creative_rules, validate_image_guidelines
import logging
from logging.handlers import RotatingFileHandler
import torch
from pathlib import Path
import cv2
import pytesseract
import numpy as np
import time
import pandas as pd
import io
import json
from typing import List
import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Security
from diffusers import DiffusionPipeline
from transformers import pipeline
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Load configuration from environment variables
load_dotenv()

# Authentication configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'UMrSzNvT5Lt9YXgbJtuSf8pO5KCpjOGKK81dRWxG8tYeHK7bm')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

security = HTTPBearer()

# Directory configuration
BASE_DIR = Path(os.getenv('BASE_DIR', Path(__file__).resolve().parent.parent / "storage"))
LOG_DIR = os.getenv('LOG_DIR', str(BASE_DIR / "logs"))
DB_PATH = os.getenv('DB_PATH', str(BASE_DIR / "assets.db"))

# Create necessary directories
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', '5242880'))  # 5MB default
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '3'))

logger = logging.getLogger('creative_tool')
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'app.log'),
    maxBytes=LOG_MAX_SIZE,
    backupCount=LOG_BACKUP_COUNT
)
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)

# FastAPI application configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

app = FastAPI(
    title='Adora ML Core Model - Retail Media Creative Tool',
    description='AI-powered creative validation, layout correction, and ad rendering platform',
    version='1.0.0',
    debug=DEBUG
)

# CORS configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
if CORS_ORIGINS == '*':
    allow_origins = ['*']
else:
    allow_origins = [origin.strip() for origin in CORS_ORIGINS.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Initialize database
init_db(DB_PATH)
logger.info(f'Database initialized at: {DB_PATH}')

# GPU configuration
USE_GPU = os.getenv('USE_GPU', 'true').lower() == 'true'
GPU_AVAILABLE = torch.cuda.is_available() if USE_GPU else False
logger.info(f'GPU available: {GPU_AVAILABLE}, GPU enabled: {USE_GPU}')

# Performance and limits configuration
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '10485760'))  # 10MB default
BATCH_LIMIT = int(os.getenv('BATCH_LIMIT', '50'))
AI_TIMEOUT = int(os.getenv('AI_TIMEOUT', '300'))

# Feature flags
ENABLE_ADVANCED_AI = os.getenv('ENABLE_ADVANCED_AI', 'true').lower() == 'true'
ENABLE_BATCH_OPERATIONS = os.getenv('ENABLE_BATCH_OPERATIONS', 'true').lower() == 'true'
ENABLE_VERSION_CONTROL = os.getenv('ENABLE_VERSION_CONTROL', 'true').lower() == 'true'
ENABLE_COMMENTS = os.getenv('ENABLE_COMMENTS', 'true').lower() == 'true'

logger.info('Application configuration loaded successfully')

# Initialize models
device = "cuda" if GPU_AVAILABLE else "cpu"
try:
    object_detector = pipeline("object-detection", model="facebook/detr-resnet-50", device=device)
    logger.info("Object detection model loaded")
except Exception as e:
    logger.warning(f"Failed to load object detection model: {e}")
    object_detector = None

try:
    stable_diffusion_pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16 if GPU_AVAILABLE else torch.float32,
        use_safetensors=True,
        variant="fp16" if GPU_AVAILABLE else None
    )
    stable_diffusion_pipe.to(device)
    logger.info("Stable Diffusion model loaded")
except Exception as e:
    logger.warning(f"Failed to load Stable Diffusion model: {e}")
    stable_diffusion_pipe = None

# Authentication functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post('/upload_packshot')
async def upload_packshot(file: UploadFile = File(...), label: str = Form(None), current_user: dict = Depends(verify_token)):
    try:
        tmp_path = save_upload_file_temp(file, subfolder='uploads')
        asset_id = save_asset(DB_PATH, tmp_path, label or file.filename, current_user['sub'])
        logger.info(f'Uploaded asset {asset_id} label={label} filename={file.filename}')
        return {'asset_id': asset_id, 'filename': file.filename}
    except Exception as e:
        logger.exception('Upload failed')
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/assets')
def assets(current_user: dict = Depends(verify_token)):
    return list_assets(DB_PATH)

@app.get('/asset/{asset_id}')
def asset(asset_id: int, current_user: dict = Depends(verify_token)):
    path = get_asset_path(DB_PATH, asset_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Asset not found')
    return FileResponse(path, media_type='image/png')

@app.post('/manipulate_image')
async def manipulate_image(asset_id: int = Form(...), remove_bg: bool = Form(False),
                             width: int = Form(None), height: int = Form(None), rotate: int = Form(0),
                             crop_left: int = Form(None), crop_top: int = Form(None), crop_right: int = Form(None), crop_bottom: int = Form(None),
                             filter_type: str = Form(None), filter_value: float = Form(1.0),
                             overlay_text_str: str = Form(''), overlay_x: int = Form(0), overlay_y: int = Form(0), font_size: int = Form(20),
                             current_user: dict = Depends(verify_token)):
    path = get_asset_path(DB_PATH, asset_id)
    if not path:
        raise HTTPException(status_code=404, detail='Asset not found')
    out_path = path
    operations_applied = []

    if remove_bg:
        out_path = remove_background(out_path)
        operations_applied.append('remove_bg')
    if crop_left is not None and crop_top is not None and crop_right is not None and crop_bottom is not None:
        out_path = crop_image(out_path, crop_left, crop_top, crop_right, crop_bottom)
        operations_applied.append('crop')
    if width or height:
        out_path = resize_image(out_path, width=width, height=height)
        operations_applied.append('resize')
    if rotate:
        out_path = rotate_image(out_path, rotate)
        operations_applied.append('rotate')
    if filter_type:
        out_path = apply_filter(out_path, filter_type, filter_value)
        operations_applied.append('filter')
    if overlay_text_str:
        out_path = overlay_text(out_path, overlay_text_str, overlay_x, overlay_y, font_size)
        operations_applied.append('overlay_text')

    # Save new version
    operation_params = {
        'remove_bg': remove_bg,
        'crop': {'left': crop_left, 'top': crop_top, 'right': crop_right, 'bottom': crop_bottom} if crop_left is not None else None,
        'resize': {'width': width, 'height': height} if width or height else None,
        'rotate': rotate if rotate else None,
        'filter': {'type': filter_type, 'value': filter_value} if filter_type else None,
        'overlay_text': {'text': overlay_text_str, 'x': overlay_x, 'y': overlay_y, 'font_size': font_size} if overlay_text_str else None
    }
    new_version = save_asset_version(DB_PATH, asset_id, out_path, 'manipulate', json.dumps(operation_params), current_user['sub'])

    logger.info(f'Manipulated image {asset_id} -> {out_path} operations={operations_applied} new_version={new_version}')
    return {'result_path': out_path, 'new_version': new_version, 'operations_applied': operations_applied}

@app.post('/validate')
async def validate(headline: str = Form(''), subhead: str = Form(''), caveat: str = Form(''), tags: str = Form(''), current_user: dict = Depends(verify_token)):
    payload = {'headline': headline, 'subhead': subhead, 'caveat': caveat, 'tags': tags}
    issues = validate_creative_rules(payload)
    logger.info(f'Validation run issues={issues}')
    return {'issues': issues}

@app.post('/validate_image')
async def validate_image(asset_id: int = Form(...), current_user: dict = Depends(verify_token)):
    path = get_asset_path(DB_PATH, asset_id)
    if not path:
        raise HTTPException(status_code=404, detail='Asset not found')
    issues = validate_image_guidelines(path)
    logger.info(f'Image validation for {asset_id} issues={issues}')
    return {'issues': issues}

@app.get('/download_sample_zip')
def download_sample_zip():
    zipf = os.path.join(os.path.dirname(__file__), '..', 'sample_output.zip')
    if not os.path.exists(zipf):
        raise HTTPException(status_code=404, detail='Sample not ready')
    return FileResponse(zipf, media_type='application/zip', filename='sample_output.zip')

@app.post('/system_health')
def system_health(current_user: dict = Depends(verify_token)):
    import psutil
    health_data = {
        'timestamp': time.time(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime_seconds': time.time() - psutil.boot_time(),
        'gpu_available': GPU_AVAILABLE,
        'active_connections': 1,  # Mock
        'total_assets': len(list_assets(DB_PATH)),
        'storage_used_mb': sum(os.path.getsize(asset['path']) for asset in list_assets(DB_PATH)) / (1024 * 1024) if list_assets(DB_PATH) else 0
    }
    logger.info(f'System health check: {health_data}')
    return health_data

@app.post('/cleanup_assets')
def cleanup_assets(days: int = 30, current_user: dict = Depends(verify_token)):
    cutoff = time.time() - (days * 24 * 60 * 60)
    assets = list_assets(DB_PATH)
    old_assets = [a for a in assets if a['uploaded_at'] < cutoff]
    result = {
        'found_old_assets': len(old_assets),
        'would_delete': [a['id'] for a in old_assets],
        'message': f'Found {len(old_assets)} assets older than {days} days. Run with confirm=true to delete.'
    }
    logger.info(f'Cleanup check: {result}')
    return result

@app.post('/generate_report')
def generate_report(current_user: dict = Depends(verify_token)):
    assets = list_assets(DB_PATH)
    total_assets = len(assets)
    processed = sum(1 for a in assets if 'processed' in (a.get('label') or '').lower())
    avg_size = sum(os.path.getsize(a['path']) for a in assets[:min(10, len(assets))]) / (1024 * min(10, len(assets))) if assets else 0

    report = {
        'generated_at': time.time(),
        'total_assets': total_assets,
        'processed_assets': processed,
        'processing_rate': (processed / total_assets * 100) if total_assets > 0 else 0,
        'average_file_size_kb': avg_size,
        'storage_estimate_mb': total_assets * 0.15,
        'top_labels': {}
    }
    logger.info(f'Report generated: {report}')
    return report

@app.post('/backup_data')
def backup_data(current_user: dict = Depends(verify_token)):
    import shutil
    backup_time = time.strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backup_{backup_time}'
    try:
        # Use BASE_DIR to ensure correct path
        storage_path = str(BASE_DIR)
        backup_path = os.path.join(storage_path, backup_dir)
        shutil.copytree(storage_path, backup_path)
        result = {
            'status': 'success',
            'backup_path': backup_path,
            'timestamp': time.time(),
            'message': f'Backup created successfully at {backup_dir}'
        }
    except Exception as e:
        result = {
            'status': 'error',
            'error': str(e),
            'message': 'Backup failed'
        }
    logger.info(f'Backup operation: {result}')
    return result

@app.post('/batch_upload')
async def batch_upload(files: List[UploadFile] = File(...), labels: str = Form(None), current_user: dict = Depends(verify_token)):
    """
    Upload multiple assets in batch
    """
    try:
        labels_list = labels.split(',') if labels else []
        results = []

        for i, file in enumerate(files):
            tmp_path = save_upload_file_temp(file, subfolder='uploads')
            label = labels_list[i] if i < len(labels_list) else None
            asset_id = save_asset(DB_PATH, tmp_path, label or file.filename, current_user['sub'])
            results.append({
                'asset_id': asset_id,
                'filename': file.filename,
                'label': label
            })
            logger.info(f'Batch uploaded asset {asset_id} filename={file.filename}')

        return {'uploaded_assets': results, 'total_uploaded': len(results)}
    except Exception as e:
        logger.exception('Batch upload failed')
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/batch_manipulate')
async def batch_manipulate(asset_ids: str = Form(...), operations: str = Form(...), current_user: dict = Depends(verify_token)):
    """
    Apply manipulations to multiple assets in batch
    """
    try:
        import json
        asset_ids_list = [int(x.strip()) for x in asset_ids.split(',')]
        operations_dict = json.loads(operations)

        results = []
        for asset_id in asset_ids_list:
            path = get_asset_path(DB_PATH, asset_id)
            if not path:
                results.append({'asset_id': asset_id, 'status': 'error', 'message': 'Asset not found'})
                continue

            out_path = path
            applied_ops = []

            # Apply operations in sequence
            if operations_dict.get('remove_bg', False):
                out_path = remove_background(out_path)
                applied_ops.append('remove_bg')

            if 'crop' in operations_dict:
                crop_data = operations_dict['crop']
                out_path = crop_image(out_path, crop_data['left'], crop_data['top'], crop_data['right'], crop_data['bottom'])
                applied_ops.append('crop')

            if 'resize' in operations_dict:
                resize_data = operations_dict['resize']
                out_path = resize_image(out_path, width=resize_data.get('width'), height=resize_data.get('height'))
                applied_ops.append('resize')

            if operations_dict.get('rotate', 0):
                out_path = rotate_image(out_path, operations_dict['rotate'])
                applied_ops.append('rotate')

            if 'filter' in operations_dict:
                filter_data = operations_dict['filter']
                out_path = apply_filter(out_path, filter_data['type'], filter_data['value'])
                applied_ops.append('filter')

            if 'overlay_text' in operations_dict:
                text_data = operations_dict['overlay_text']
                out_path = overlay_text(out_path, text_data['text'], text_data['x'], text_data['y'], text_data['font_size'])
                applied_ops.append('overlay_text')

            # Save new version for batch operations
            operation_params = {
                'batch_operation': True,
                'operations': operations_dict
            }
            new_version = save_asset_version(DB_PATH, asset_id, out_path, 'batch_manipulate', json.dumps(operation_params), current_user['sub'])

            results.append({
                'asset_id': asset_id,
                'status': 'success',
                'result_path': out_path,
                'applied_operations': applied_ops,
                'new_version': new_version
            })

        logger.info(f'Batch manipulated {len(asset_ids_list)} assets')
        return {'results': results, 'total_processed': len(results)}
    except Exception as e:
        logger.exception('Batch manipulation failed')
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/batch_validate')
async def batch_validate(asset_ids: str = Form(...), current_user: dict = Depends(verify_token)):
    """
    Validate multiple assets in batch
    """
    try:
        asset_ids_list = [int(x.strip()) for x in asset_ids.split(',')]
        results = []

        for asset_id in asset_ids_list:
            path = get_asset_path(DB_PATH, asset_id)
            if not path:
                results.append({'asset_id': asset_id, 'status': 'error', 'message': 'Asset not found'})
                continue

            issues = validate_image_guidelines(path)
            results.append({
                'asset_id': asset_id,
                'status': 'success',
                'issues': issues,
                'compliant': len(issues) == 0
            })

        logger.info(f'Batch validated {len(asset_ids_list)} assets')
        return {'results': results, 'total_validated': len(results)}
    except Exception as e:
        logger.exception('Batch validation failed')
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/analyze_image')
async def analyze_image(asset_id: int = Form(...), current_user: dict = Depends(verify_token)):
    """
    AI-powered image analysis including auto-tagging and object detection
    """
    try:
        path = get_asset_path(DB_PATH, asset_id)
        if not path:
            raise HTTPException(status_code=404, detail='Asset not found')

        # Basic image analysis using OpenCV
        image = cv2.imread(path)
        height, width = image.shape[:2]

        # Color analysis
        avg_color = cv2.mean(image)[:3]
        avg_color_rgb = tuple(reversed([int(c) for c in avg_color]))

        # Brightness analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])

        # Edge detection for complexity
        edges = cv2.Canny(image, 100, 200)
        complexity = np.sum(edges > 0) / (height * width)

        # OCR for text detection
        try:
            text_content = pytesseract.image_to_string(image)
            has_text = len(text_content.strip()) > 0
        except:
            text_content = ""
            has_text = False

        # Object detection
        detected_objects = []
        detected_people = []
        if object_detector:
            try:
                pil_image = Image.open(path)
                detections = object_detector(pil_image)
                for detection in detections:
                    label = detection['label']
                    score = detection['score']
                    if score > 0.5:  # Confidence threshold
                        detected_objects.append({'label': label, 'confidence': score})
                        if label == 'person':
                            detected_people.append({'confidence': score})
            except Exception as e:
                logger.warning(f"Object detection failed: {e}")

        analysis = {
            'dimensions': {'width': width, 'height': height},
            'average_color': avg_color_rgb,
            'brightness': float(brightness),
            'complexity_score': float(complexity),
            'has_text': has_text,
            'extracted_text': text_content[:500] if text_content else "",  # Limit text length
            'file_size_kb': os.path.getsize(path) / 1024,
            'aspect_ratio': width / height if height > 0 else 0,
            'detected_objects': detected_objects,
            'detected_people': detected_people,
            'restricted_content': len(detected_people) > 0  # Flag if people detected
        }

        # Auto-tagging based on analysis
        tags = []
        if brightness < 50:
            tags.append('dark')
        elif brightness > 200:
            tags.append('bright')

        if complexity < 0.01:
            tags.append('simple')
        elif complexity > 0.1:
            tags.append('complex')

        if has_text:
            tags.append('text_overlay')

        # Color-based tags
        r, g, b = avg_color_rgb
        if r > g and r > b:
            tags.append('red_tone')
        elif g > r and g > b:
            tags.append('green_tone')
        elif b > r and b > g:
            tags.append('blue_tone')

        # Object-based tags
        for obj in detected_objects:
            tags.append(obj['label'])

        analysis['auto_tags'] = tags

        logger.info(f'Analyzed image {asset_id}: {analysis}')
        return analysis
    except Exception as e:
        logger.exception(f'Image analysis failed for asset {asset_id}')
        raise HTTPException(status_code=500, detail=str(e))

def generate_marketing_text(analysis):
    """
    Generate marketing text based on image analysis
    """
    text = analysis.get('extracted_text', '').strip()
    objects = [obj['label'] for obj in analysis.get('detected_objects', [])]
    has_people = len(analysis.get('detected_people', [])) > 0

    # Simple template-based generation
    if 'bottle' in objects or 'container' in text.lower():
        product_type = "beverage"
    elif 'food' in objects or 'snack' in text.lower():
        product_type = "snack"
    else:
        product_type = "product"

    headline = f"Discover the Perfect {product_type.title()} for You!"
    subhead = f"Premium quality {product_type} with exceptional taste."
    caveat = "Terms and conditions apply. See packaging for details."

    return {
        'headline': headline,
        'subhead': subhead,
        'caveat': caveat,
        'tags': objects
    }

def generate_image_with_sd(prompt, negative_prompt="blurry, low quality, distorted"):
    """
    Generate image using Stable Diffusion
    """
    if not stable_diffusion_pipe:
        raise Exception("Stable Diffusion model not loaded")

    try:
        image = stable_diffusion_pipe(prompt=prompt, negative_prompt=negative_prompt).images[0]
        return image
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise

def evaluate_generated_image(image, format_type):
    """
    Evaluate generated image for quality metrics
    """
    # Convert PIL to numpy
    img_array = np.array(image)

    # Basic evaluations
    height, width = img_array.shape[:2]

    # Brightness
    hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    brightness = np.mean(hsv[:, :, 2])

    # Contrast (std dev of brightness)
    contrast = np.std(hsv[:, :, 2])

    # Text readability (placeholder - assume good if not too dark)
    readable = brightness > 100

    # Layout balance (center mass)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    moments = cv2.moments(gray)
    if moments["m00"] != 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        center_balance = abs(cx - width//2) + abs(cy - height//2)
    else:
        center_balance = 0

    # Safe zones (assume 10% margins)
    safe_zone_violation = (cx < width*0.1 or cx > width*0.9 or cy < height*0.1 or cy > height*0.9)

    return {
        'brightness': float(brightness),
        'contrast': float(contrast),
        'text_readable': readable,
        'layout_balance_score': float(center_balance),
        'safe_zone_compliant': not safe_zone_violation,
        'platform_suitable': format_type in ['story', 'feed', 'banner']
    }

@app.post('/generate_ad_assets')
async def generate_ad_assets(asset_id: int = Form(...), current_user: dict = Depends(verify_token)):
    """
    Generate advertising assets based on packshot analysis
    """
    try:
        # First, analyze the image
        analysis_response = await analyze_image(asset_id, current_user)
        analysis = analysis_response

        if analysis.get('restricted_content'):
            raise HTTPException(status_code=400, detail="Image contains restricted content (people detected)")

        # Generate marketing text
        marketing_text = generate_marketing_text(analysis)

        # Generate images for different formats
        formats = {
            'story': {'size': (1080, 1920), 'aspect': 9/16},  # Vertical
            'feed': {'size': (1080, 1080), 'aspect': 1},      # Square
            'banner': {'size': (1200, 628), 'aspect': 1200/628}  # Horizontal
        }

        generated_assets = {}
        image_generation_dir = os.path.join(BASE_DIR, 'image_generation')
        os.makedirs(image_generation_dir, exist_ok=True)

        for format_name, specs in formats.items():
            prompt = f"A high-quality advertisement for {marketing_text['headline']} {marketing_text['subhead']}, professional {format_name} format, clean design"
            try:
                image = generate_image_with_sd(prompt)
                # Resize to format
                image = image.resize(specs['size'], Image.LANCZOS)

                # Evaluate
                evaluation = evaluate_generated_image(image, format_name)

                # Save
                filename = f"{asset_id}_{format_name}_{int(time.time())}.png"
                filepath = os.path.join(image_generation_dir, filename)
                image.save(filepath)

                generated_assets[format_name] = {
                    'path': filepath,
                    'evaluation': evaluation,
                    'filename': filename
                }

            except Exception as e:
                logger.error(f"Failed to generate {format_name}: {e}")
                generated_assets[format_name] = {'error': str(e)}

        result = {
            'analysis': analysis,
            'marketing_text': marketing_text,
            'generated_assets': generated_assets
        }

        logger.info(f'Generated ad assets for {asset_id}')
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f'Ad asset generation failed for asset {asset_id}')
        raise HTTPException(status_code=500, detail=str(e))

# Authentication endpoints
@app.post('/register')
async def register(username: str = Form(...), password: str = Form(...), email: str = Form(None)):
    """Register a new user"""
    try:
        # In production, store users in database
        # For demo, we'll use a simple file-based storage
        users_file = os.path.join(BASE_DIR, 'users.json')
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                users = json.load(f)
        else:
            users = {}

        if username in users:
            raise HTTPException(status_code=400, detail="Username already exists")

        users[username] = {
            'password_hash': hash_password(password),
            'email': email,
            'created_at': time.time(),
            'role': 'user'
        }

        with open(users_file, 'w') as f:
            json.dump(users, f)

        logger.info(f'User registered: {username}')
        return {'message': 'User registered successfully'}
    except Exception as e:
        logger.exception('Registration failed')
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/login')
async def login(username: str = Form(...), password: str = Form(...)):
    """Authenticate user and return JWT token"""
    try:
        users_file = os.path.join(BASE_DIR, 'users.json')
        if not os.path.exists(users_file):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        with open(users_file, 'r') as f:
            users = json.load(f)

        if username not in users or not verify_password(password, users[username]['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": username, "role": users[username]['role']})
        logger.info(f'User logged in: {username}')
        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': JWT_EXPIRATION_HOURS * 3600
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Login failed')
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/me')
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current user information"""
    return {
        'username': current_user['sub'],
        'role': current_user.get('role', 'user')
    }

@app.post('/change_password')
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    current_user: dict = Depends(verify_token)
):
    """Change user password"""
    try:
        users_file = os.path.join(BASE_DIR, 'users.json')
        with open(users_file, 'r') as f:
            users = json.load(f)

        username = current_user['sub']
        if not verify_password(old_password, users[username]['password_hash']):
            raise HTTPException(status_code=400, detail="Invalid old password")

        users[username]['password_hash'] = hash_password(new_password)

        with open(users_file, 'w') as f:
            json.dump(users, f)

        logger.info(f'Password changed for user: {username}')
        return {'message': 'Password changed successfully'}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Password change failed')
        raise HTTPException(status_code=500, detail=str(e))

# Version control endpoints
@app.get('/asset/{asset_id}/versions')
async def get_asset_version_history(asset_id: int, current_user: dict = Depends(verify_token)):
    """Get version history for an asset"""
    try:
        versions = get_asset_versions(DB_PATH, asset_id)
        return {'versions': versions}
    except Exception as e:
        logger.exception(f'Failed to get versions for asset {asset_id}')
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/asset/{asset_id}/version/{version}')
async def get_asset_version(asset_id: int, version: int, current_user: dict = Depends(verify_token)):
    """Get specific version of an asset"""
    try:
        path = get_asset_path(DB_PATH, asset_id, version)
        if not path or not os.path.exists(path):
            raise HTTPException(status_code=404, detail='Version not found')
        return FileResponse(path, media_type='image/png')
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f'Failed to get version {version} for asset {asset_id}')
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/asset/{asset_id}/comment')
async def add_comment_to_asset(
    asset_id: int,
    comment: str = Form(...),
    version_id: int = Form(None),
    current_user: dict = Depends(verify_token)
):
    """Add a comment to an asset or specific version"""
    try:
        comment_id = add_asset_comment(DB_PATH, asset_id, comment, version_id, current_user['sub'])
        return {'comment_id': comment_id, 'message': 'Comment added successfully'}
    except Exception as e:
        logger.exception(f'Failed to add comment to asset {asset_id}')
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/asset/{asset_id}/comments')
async def get_asset_comments_endpoint(asset_id: int, current_user: dict = Depends(verify_token)):
    """Get comments for an asset"""
    try:
        comments = get_asset_comments(DB_PATH, asset_id)
        return {'comments': comments}
    except Exception as e:
        logger.exception(f'Failed to get comments for asset {asset_id}')
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/asset/{asset_id}/restore/{version}')
async def restore_asset_version(
    asset_id: int,
    version: int,
    current_user: dict = Depends(verify_token)
):
    """Restore asset to a previous version"""
    try:
        # Get the path of the version to restore
        version_path = get_asset_path(DB_PATH, asset_id, version)
        if not version_path:
            raise HTTPException(status_code=404, detail='Version not found')

        # Create a copy of the version as new current version
        import shutil
        new_path = version_path.replace('.png', f'_restored_v{version}_{int(time.time())}.png')
        shutil.copy2(version_path, new_path)

        # Save as new version
        new_version = save_asset_version(DB_PATH, asset_id, new_path, 'restore', json.dumps({'restored_from': version}), current_user['sub'])

        return {'new_version': new_version, 'message': f'Asset restored to version {version}'}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f'Failed to restore asset {asset_id} to version {version}')
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/export_report')
def export_report(current_user: dict = Depends(verify_token)):
    assets = list_assets(DB_PATH)
    total_assets = len(assets)

    # System health data
    import psutil
    health_data = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime_seconds': time.time() - psutil.boot_time(),
        'gpu_available': GPU_AVAILABLE,
    }

    # Asset analytics
    if assets:
        df = pd.DataFrame(assets)
        df['uploaded_at'] = pd.to_datetime(df['uploaded_at'], unit='s')

        processed = sum(1 for a in assets if 'processed' in (a.get('label') or '').lower())
        avg_size = sum(os.path.getsize(a['path']) for a in assets[:min(10, len(assets))]) / (1024 * min(10, len(assets))) if assets else 0

        categories = {'Product': 0, 'Lifestyle': 0, 'Banner': 0, 'Packshot': 0, 'Other': 0}
        for asset in assets:
            label = (asset.get('label') or '').lower()
            if 'product' in label or 'shot' in label:
                categories['Product'] += 1
            elif 'lifestyle' in label or 'scene' in label:
                categories['Lifestyle'] += 1
            elif 'banner' in label or 'header' in label:
                categories['Banner'] += 1
            elif 'packshot' in label or 'package' in label:
                categories['Packshot'] += 1
            else:
                categories['Other'] += 1

        # Upload patterns
        hourly_uploads = df.groupby(df['uploaded_at'].dt.hour).size()
        daily_uploads = df.groupby(df['uploaded_at'].dt.date).size()

    # Create comprehensive report data
    report_data = {
        'Report_Generated_At': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        'Total_Assets': total_assets,
        'Processed_Assets': processed if assets else 0,
        'Processing_Rate_Percent': (processed / total_assets * 100) if total_assets > 0 else 0,
        'Average_File_Size_KB': avg_size if assets else 0,
        'Storage_Used_MB': sum(os.path.getsize(asset['path']) for asset in assets) / (1024 * 1024) if assets else 0,
        'Storage_Estimate_MB': total_assets * 0.15,

        # System Health
        'CPU_Usage_Percent': health_data['cpu_percent'],
        'Memory_Usage_Percent': health_data['memory_percent'],
        'Disk_Usage_Percent': health_data['disk_usage'],
        'System_Uptime_Hours': health_data['uptime_seconds'] / 3600,
        'GPU_Available': 'Yes' if health_data['gpu_available'] else 'No',

        # Asset Categories
        'Product_Assets': categories.get('Product', 0),
        'Lifestyle_Assets': categories.get('Lifestyle', 0),
        'Banner_Assets': categories.get('Banner', 0),
        'Packshot_Assets': categories.get('Packshot', 0),
        'Other_Assets': categories.get('Other', 0),
    }

    # Add hourly upload data
    for hour in range(24):
        report_data[f'Uploads_Hour_{hour}'] = hourly_uploads.get(hour, 0) if assets else 0

    df_report = pd.DataFrame([report_data])
    csv_buffer = io.StringIO()
    df_report.to_csv(csv_buffer, index=False)
    # Return CSV file
    csv_buffer.seek(0)
    response = csv_buffer.getvalue()

    logger.info(f'Comprehensive report exported with {len(report_data)} metrics')

    return {
        'filename': f'creative_tool_report_{time.strftime("%Y%m%d_%H%M%S")}.csv',
        'content': response,
        'metrics_count': len(report_data)
    }

if __name__ == '__main__':
    uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=True)
