from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
from db import init_db, save_asset, list_assets, get_asset_path
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

BASE_DIR = Path(__file__).resolve().parent.parent / "storage"
LOG_DIR = os.getenv('LOG_DIR', str(BASE_DIR / "logs"))
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger('creative_tool')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(os.path.join(LOG_DIR, 'app.log'), maxBytes=5_000_000, backupCount=3)
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)

app = FastAPI(title='Retail Media Creative Tool Prototype')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Initialize DB
DB_PATH = os.getenv('DB_PATH', str(BASE_DIR / "assets.db"))
init_db(DB_PATH)

# Check for CUDA
GPU_AVAILABLE = torch.cuda.is_available() if 'torch' in globals() else False
logger.info(f'GPU available: {GPU_AVAILABLE}')

@app.post('/upload_packshot')
async def upload_packshot(file: UploadFile = File(...), label: str = Form(None)):
    try:
        tmp_path = save_upload_file_temp(file, subfolder='uploads')
        asset_id = save_asset(DB_PATH, tmp_path, label or file.filename)
        logger.info(f'Uploaded asset {asset_id} label={label} filename={file.filename}')
        return {'asset_id': asset_id, 'filename': file.filename}
    except Exception as e:
        logger.exception('Upload failed')
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/assets')
def assets():
    return list_assets(DB_PATH)

@app.get('/asset/{asset_id}')
def asset(asset_id: int):
    path = get_asset_path(DB_PATH, asset_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Asset not found')
    return FileResponse(path, media_type='image/png')

@app.post('/manipulate_image')
async def manipulate_image(asset_id: int = Form(...), remove_bg: bool = Form(False),
                            width: int = Form(None), height: int = Form(None), rotate: int = Form(0),
                            crop_left: int = Form(None), crop_top: int = Form(None), crop_right: int = Form(None), crop_bottom: int = Form(None),
                            filter_type: str = Form(None), filter_value: float = Form(1.0),
                            overlay_text_str: str = Form(''), overlay_x: int = Form(0), overlay_y: int = Form(0), font_size: int = Form(20)):
    path = get_asset_path(DB_PATH, asset_id)
    if not path:
        raise HTTPException(status_code=404, detail='Asset not found')
    out_path = path
    if remove_bg:
        out_path = remove_background(out_path)
    if crop_left is not None and crop_top is not None and crop_right is not None and crop_bottom is not None:
        out_path = crop_image(out_path, crop_left, crop_top, crop_right, crop_bottom)
    if width or height:
        out_path = resize_image(out_path, width=width, height=height)
    if rotate:
        out_path = rotate_image(out_path, rotate)
    if filter_type:
        out_path = apply_filter(out_path, filter_type, filter_value)
    if overlay_text_str:
        out_path = overlay_text(out_path, overlay_text_str, overlay_x, overlay_y, font_size)
    logger.info(f'Manipulated image {asset_id} -> {out_path} remove_bg={remove_bg} crop=({crop_left},{crop_top},{crop_right},{crop_bottom}) size=({width},{height}) rotate={rotate} filter={filter_type}:{filter_value} text="{overlay_text_str}"')
    return {'result_path': out_path}

@app.post('/validate')
async def validate(headline: str = Form(''), subhead: str = Form(''), caveat: str = Form(''), tags: str = Form('')):
    payload = {'headline': headline, 'subhead': subhead, 'caveat': caveat, 'tags': tags}
    issues = validate_creative_rules(payload)
    logger.info(f'Validation run issues={issues}')
    return {'issues': issues}

@app.post('/validate_image')
async def validate_image(asset_id: int = Form(...)):
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
def system_health():
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
def cleanup_assets(days: int = 30):
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
def generate_report():
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
def backup_data():
    import shutil
    backup_time = time.strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backup_{backup_time}'
    try:
        shutil.copytree('storage', f'storage/{backup_dir}')
        result = {
            'status': 'success',
            'backup_path': f'storage/{backup_dir}',
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

@app.get('/export_report')
def export_report():
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
