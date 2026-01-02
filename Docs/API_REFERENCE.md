# Adora ML Core Model - API Reference

## 📡 API Overview

Base URL: `http://localhost:8000`
Authentication: JWT Bearer tokens (except registration/login)

### Authentication Headers
```
Authorization: Bearer UMrSzNvT5Lt9YXgbJtuSf8pO5KCpjOGKK81dRWxG8tYeHK7bm
```

## 🔐 Authentication Endpoints

### POST /register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string (optional)"
}
```

**Response:**
```json
{
  "message": "User registered successfully"
}
```

### POST /login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### GET /me
Get current user information.

**Response:**
```json
{
  "username": "string",
  "role": "user"
}
```

## 📁 Asset Management

### POST /upload_packshot
Upload a new asset (packshot image).

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: Image file (PNG, JPG, JPEG)
- `label`: Optional label string

**Response:**
```json
{
  "asset_id": 123,
  "filename": "image.jpg"
}
```

### GET /assets
List all assets for the authenticated user.

**Response:**
```json
[
  {
    "id": 123,
    "label": "Product Shot 1",
    "path": "/storage/uploads/image.png",
    "uploaded_at": 1640995200.0,
    "current_version": 1,
    "created_by": "username"
  }
]
```

### GET /asset/{asset_id}
Retrieve a specific asset file.

**Response:** Binary image data

### POST /manipulate_image
Apply image transformations to an asset.

**Form Data:**
```json
{
  "asset_id": 123,
  "remove_bg": "false",
  "width": 800,
  "height": 1200,
  "rotate": 0,
  "crop_left": 0,
  "crop_top": 0,
  "crop_right": 800,
  "crop_bottom": 1200,
  "filter_type": "brightness",
  "filter_value": 1.2,
  "overlay_text_str": "Sample Text",
  "overlay_x": 10,
  "overlay_y": 10,
  "font_size": 20
}
```

**Response:**
```json
{
  "result_path": "/storage/generated/image_processed.png",
  "new_version": 2,
  "operations_applied": ["resize", "filter"]
}
```

## 🤖 AI & Analysis

### POST /analyze_image
Perform comprehensive AI analysis on an asset.

**Form Data:**
```json
{
  "asset_id": 123
}
```

**Response:**
```json
{
  "dimensions": {"width": 800, "height": 1200},
  "average_color": [128, 128, 128],
  "brightness": 0.7,
  "complexity_score": 0.15,
  "has_text": true,
  "extracted_text": "Product description...",
  "file_size_kb": 245.6,
  "aspect_ratio": 0.667,
  "detected_objects": [
    {"label": "bottle", "confidence": 0.95}
  ],
  "detected_people": [],
  "restricted_content": false,
  "auto_tags": ["bright", "text_overlay", "bottle"]
}
```

### POST /generate_ad_assets
Generate advertising creatives from a packshot.

**Form Data:**
```json
{
  "asset_id": 123
}
```

**Response:**
```json
{
  "analysis": {...},
  "marketing_text": {
    "headline": "Discover the Perfect Beverage for You!",
    "subhead": "Premium quality beverage with exceptional taste.",
    "caveat": "Terms and conditions apply. See packaging for details.",
    "tags": ["bottle", "beverage"]
  },
  "generated_assets": {
    "story": {
      "path": "/storage/generated/123_story_1640995200.png",
      "evaluation": {
        "brightness": 0.8,
        "contrast": 1.2,
        "text_readable": true,
        "layout_balance_score": 45.2,
        "safe_zone_compliant": true,
        "platform_suitable": true
      },
      "filename": "123_story_1640995200.png"
    },
    "feed": {...},
    "banner": {...}
  }
}
```

## ✅ Compliance Validation

### POST /validate
Validate creative copy against brand guidelines.

**Form Data:**
```json
{
  "headline": "Amazing Product!",
  "subhead": "Best in class",
  "caveat": "Drinkaware message",
  "tags": "Available at Tesco"
}
```

**Response:**
```json
{
  "issues": [
    {
      "type": "hard_fail",
      "msg": "Forbidden claims detected"
    },
    {
      "type": "warning",
      "msg": "Ensure minimum font size >= 20px"
    }
  ]
}
```

### POST /validate_image
Validate image against compliance requirements.

**Form Data:**
```json
{
  "asset_id": 123
}
```

**Response:**
```json
{
  "issues": [
    {
      "type": "warning",
      "msg": "Text detected; ensure minimum font size >=20px"
    }
  ]
}
```

## 📊 System Management

### POST /system_health
Get comprehensive system health metrics.

**Response:**
```json
{
  "timestamp": 1640995200.0,
  "cpu_percent": 25.5,
  "memory_percent": 45.2,
  "disk_usage": 60.1,
  "uptime_seconds": 3600,
  "gpu_available": true,
  "active_connections": 1,
  "total_assets": 25,
  "storage_used_mb": 125.5
}
```

### GET /export_report
Export comprehensive system report as CSV.

**Response:** CSV file download

### POST /generate_report
Generate analytics report.

**Response:**
```json
{
  "generated_at": 1640995200.0,
  "total_assets": 25,
  "processed_assets": 20,
  "processing_rate": 80.0,
  "average_file_size_kb": 245.6,
  "storage_estimate_mb": 6.14
}
```

## 🔄 Version Control

### GET /asset/{asset_id}/versions
Get version history for an asset.

**Response:**
```json
{
  "versions": [
    {
      "version": 1,
      "operation": "upload",
      "params": null,
      "created_at": 1640995200.0,
      "created_by": "username"
    },
    {
      "version": 2,
      "operation": "manipulate",
      "params": "{\"resize\": {\"width\": 800, \"height\": 1200}}",
      "created_at": 1640995300.0,
      "created_by": "username"
    }
  ]
}
```

### GET /asset/{asset_id}/version/{version}
Retrieve a specific version of an asset.

**Response:** Binary image data

### POST /asset/{asset_id}/restore/{version}
Restore asset to a previous version.

**Response:**
```json
{
  "new_version": 3,
  "message": "Asset restored to version 1"
}
```

## 💬 Comments & Collaboration

### POST /asset/{asset_id}/comment
Add a comment to an asset or version.

**Form Data:**
```json
{
  "comment": "Looks good, approved for production",
  "version_id": 2
}
```

**Response:**
```json
{
  "comment_id": 456,
  "message": "Comment added successfully"
}
```

### GET /asset/{asset_id}/comments
Get all comments for an asset.

**Response:**
```json
{
  "comments": [
    {
      "comment": "Initial upload looks good",
      "created_at": 1640995200.0,
      "created_by": "reviewer",
      "version": 1
    }
  ]
}
```

## 📦 Batch Operations

### POST /batch_upload
Upload multiple assets simultaneously.

**Content-Type:** `multipart/form-data`

**Form Data:**
- `files`: Multiple image files
- `labels`: Comma-separated labels (optional)

**Response:**
```json
{
  "uploaded_assets": [
    {"asset_id": 123, "filename": "image1.jpg", "label": "Product 1"},
    {"asset_id": 124, "filename": "image2.jpg", "label": "Product 2"}
  ],
  "total_uploaded": 2
}
```

### POST /batch_manipulate
Apply operations to multiple assets.

**Form Data:**
```json
{
  "asset_ids": "123,124,125",
  "operations": "{\"resize\": {\"width\": 800, \"height\": 800}}"
}
```

**Response:**
```json
{
  "results": [
    {
      "asset_id": 123,
      "status": "success",
      "result_path": "/storage/generated/123_processed.png",
      "applied_operations": ["resize"],
      "new_version": 2
    }
  ],
  "total_processed": 3
}
```

## 🚨 Error Responses

All endpoints may return the following error formats:

### 400 Bad Request
```json
{
  "detail": "Invalid input parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid token"
}
```

### 404 Not Found
```json
{
  "detail": "Asset not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Processing failed: [error details]"
}
```

## 📊 Rate Limits

- **Authenticated requests**: 1000 per hour per user
- **File uploads**: 50 MB per hour per user
- **AI operations**: 100 per hour per user
- **Batch operations**: 10 concurrent operations per user

## 🔧 WebSocket Support (Future)

Real-time updates for:
- Processing status
- System health metrics
- Collaborative editing notifications

**API Version**: v1.0.0
**Base URL**: http://localhost:8000
**Documentation**: http://localhost:8000/docs (when backend is running)