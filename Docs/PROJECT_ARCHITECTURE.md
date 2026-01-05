# Adora ML Core Model - Project Architecture & Flow

## 📋 Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Data Flow](#data-flow)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [AI/ML Pipeline](#aiml-pipeline)
- [Security & Authentication](#security--authentication)
- [Deployment & Scaling](#deployment--scaling)
- [Development Workflow](#development-workflow)

## 🎯 Overview

Adora ML Core Model is a comprehensive AI-powered platform for automated creative validation, layout correction, and final ad rendering in retail media. The system provides end-to-end creative intelligence for marketing automation, integrating OCR, object detection, compliance checking, and auto-layout optimization.

### Key Capabilities
- **Smart Creative Validation**: OCR, YOLO object detection, banned-phrase scanning, brand compliance
- **AI Auto-Fix Engine**: Automatic font size, color, contrast, and safe-zone adjustments
- **Background Removal**: Clean product cutouts using advanced segmentation
- **Multi-Format Generation**: Instagram Stories, Feed posts, Facebook banners
- **Version Control**: Asset versioning with rollback capabilities
- **Compliance Automation**: Tesco brand guidelines and legal requirements validation

## 🏗️ System Architecture

### High-Level Architecture

<img width="1550" height="834" alt="diagram-export-03-01-2026-13_55_20" src="https://github.com/user-attachments/assets/2a02f3b2-965a-46cb-9d9f-c6d64df3742a" />

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │◄──►│   FastAPI       │◄──►│   SQLite DB     │
│   (Frontend)    │    │   Backend       │    │   (Assets)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   AI Models     │
                    │   (GPU/CPU)     │
                    └─────────────────┘
```

### Component Breakdown

#### 1. Frontend Layer (Streamlit)
- **Purpose**: User interface for creative management
- **Features**:
  - Dashboard with analytics and KPIs
  - Asset library management
  - Image editor with AI tools
  - AI analysis interface
  - Compliance validation tools
  - Version history browser

#### 2. Backend Layer (FastAPI)
- **Purpose**: Business logic and API services
- **Components**:
  - Authentication & authorization
  - Asset management (CRUD operations)
  - Image processing pipeline
  - AI model orchestration
  - Compliance validation engine
  - Report generation

#### 3. Data Layer (SQLite)
- **Purpose**: Persistent storage for assets and metadata
- **Tables**:
  - `assets`: Core asset information
  - `asset_versions`: Version control history
  - `asset_comments`: User comments and annotations
  - `users`: Authentication data (file-based for demo)

#### 4. AI/ML Layer
- **Purpose**: Intelligent processing and analysis
- **Models**:
  - Object Detection (Facebook DETR)
  - Stable Diffusion XL (Image generation)
  - OCR (Tesseract)
  - Background Removal (rembg)

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: SQLite3 with custom ORM layer
- **Authentication**: JWT tokens with bcrypt password hashing
- **Image Processing**: Pillow, OpenCV, rembg
- **AI/ML**: PyTorch, Transformers, Diffusers
- **OCR**: Tesseract OCR
- **System Monitoring**: psutil

### Frontend
- **Framework**: Streamlit
- **Visualization**: Matplotlib, Plotly integration
- **HTTP Client**: Requests library
- **Image Handling**: Pillow

### Infrastructure
- **Containerization**: Docker support
- **Process Management**: Uvicorn ASGI server
- **Logging**: Python logging with rotating file handler
- **Environment**: Configurable via environment variables

## 🔄 Data Flow

### Asset Upload Flow
```
1. User uploads image via Streamlit UI
2. Frontend sends multipart request to /upload_packshot
3. Backend saves file to storage/uploads/
4. Creates database entry in assets table
5. Creates initial version entry
6. Returns asset ID to frontend
7. Frontend refreshes asset library
```

### Image Processing Flow
```
1. User selects asset and applies manipulations
2. Frontend sends processing parameters to /manipulate_image
3. Backend loads original image
4. Applies transformations in sequence:
   - Background removal (if requested)
   - Cropping (if coordinates provided)
   - Resizing (if dimensions specified)
   - Rotation (if angle provided)
   - Filter application (brightness/contrast/sharpness)
   - Text overlay (if text provided)
5. Saves new version to storage/generated/
6. Updates database with new version
7. Returns processing results
```

### AI Analysis Flow
```
1. User requests analysis for asset
2. Frontend calls /analyze_image endpoint
3. Backend performs multi-stage analysis:
   - Basic image metrics (dimensions, file size)
   - Color analysis (average color, brightness)
   - Complexity scoring (edge detection)
   - OCR text extraction
   - Object detection (YOLO/DETR)
   - Auto-tagging based on analysis
4. Returns comprehensive analysis results
5. Frontend displays results with visualizations
```

### Ad Generation Flow
```
1. User initiates creative generation
2. Frontend calls /generate_ad_assets
3. Backend analyzes source packshot
4. Generates marketing text using templates
5. Creates images for multiple formats:
   - Instagram Story (9:16)
   - Instagram Feed (1:1)
   - Facebook Banner (1.91:1)
6. Evaluates generated images for quality
7. Saves generated assets
8. Returns results with evaluation metrics
```

## 📡 API Endpoints

### Authentication Endpoints
- `POST /register` - User registration
- `POST /login` - User authentication
- `POST /me` - Get current user info
- `POST /change_password` - Password update

### Asset Management
- `POST /upload_packshot` - Single asset upload
- `POST /batch_upload` - Multiple asset upload
- `GET /assets` - List all assets
- `GET /asset/{id}` - Get specific asset
- `POST /manipulate_image` - Apply image transformations
- `POST /batch_manipulate` - Batch image processing

### AI & Analysis
- `POST /analyze_image` - Comprehensive image analysis
- `POST /generate_ad_assets` - Generate advertising creatives
- `POST /validate` - Content compliance validation
- `POST /validate_image` - Image compliance checking
- `POST /batch_validate` - Batch compliance validation

### Version Control
- `GET /asset/{id}/versions` - Get version history
- `GET /asset/{id}/version/{v}` - Get specific version
- `POST /asset/{id}/restore/{v}` - Restore to version
- `POST /asset/{id}/comment` - Add comment
- `GET /asset/{id}/comments` - Get comments

### System Management
- `POST /system_health` - System diagnostics
- `POST /cleanup_assets` - Remove old assets
- `POST /generate_report` - Create analytics report
- `POST /backup_data` - System backup
- `GET /export_report` - Download CSV report

## 🗄️ Database Schema

### Assets Table
```sql
CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT,
    path TEXT,
    uploaded_at REAL,
    current_version INTEGER DEFAULT 1,
    created_by TEXT
);
```

### Asset Versions Table
```sql
CREATE TABLE asset_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    version_number INTEGER,
    path TEXT,
    operation TEXT,
    operation_params TEXT,
    created_at REAL,
    created_by TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets (id)
);
```

### Asset Comments Table
```sql
CREATE TABLE asset_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    version_id INTEGER,
    comment TEXT,
    created_at REAL,
    created_by TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets (id),
    FOREIGN KEY (version_id) REFERENCES asset_versions (id)
);
```

## 🤖 AI/ML Pipeline

### Object Detection Pipeline
- **Model**: Facebook DETR ResNet-50
- **Purpose**: Identify objects and people in images
- **Input**: PIL Image
- **Output**: Detected objects with confidence scores
- **Use Cases**: Compliance checking, auto-tagging

### Stable Diffusion Pipeline
- **Model**: Stability AI SDXL Base 1.0
- **Purpose**: Generate advertising images
- **Input**: Text prompts
- **Output**: High-quality images (1024x1024)
- **Use Cases**: Creative asset generation

### OCR Pipeline
- **Engine**: Tesseract OCR
- **Purpose**: Extract text from images
- **Input**: Image file
- **Output**: Extracted text content
- **Use Cases**: Compliance validation, content analysis

### Background Removal Pipeline
- **Library**: rembg (U2-Net)
- **Purpose**: Remove image backgrounds
- **Input**: Image with background
- **Output**: Transparent PNG
- **Use Cases**: Product isolation, creative composition

## 🔐 Security & Authentication

### JWT Authentication
- **Token Type**: Bearer tokens
- **Expiration**: 24 hours
- **Storage**: In-memory (demo) or database (production)
- **Endpoints**: All API routes except registration/login

### Password Security
- **Hashing**: bcrypt with salt
- **Storage**: JSON file (demo) or database (production)
- **Validation**: Minimum 6 characters

### File Security
- **Storage**: Local filesystem with organized directories
- **Access**: Authenticated users only
- **Validation**: File type checking, size limits

## 🚀 Deployment & Scaling

### Development Setup
```bash
# Backend
cd backend
python -m venv .venv
source .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
python -m venv .venv
source .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Docker Deployment
- **Base Image**: python:3.9-slim
- **Multi-stage Build**: Optimized for production
- **Volume Mounts**: Persistent storage for assets
- **GPU Support**: CUDA-enabled containers

### Production Considerations (Future Considerations)
- **Database**: PostgreSQL for production scale
- **File Storage**: Cloud storage (S3, GCS) for assets
- **Caching**: Redis for session and API caching
- **Load Balancing**: Nginx reverse proxy
- **Monitoring**: Prometheus metrics collection

## 🔄 Development Workflow

### Code Organization
```
backend/
├── main.py          # FastAPI application
├── db.py            # Database operations
├── utils.py         # Image processing utilities
├── guidelines.py    # Compliance validation rules
└── requirements.txt # Python dependencies

frontend/
├── streamlit_app.py # Streamlit application
└── requirements.txt # Python dependencies

storage/             # Generated at runtime
├── uploads/         # Original assets
├── generated/       # Processed assets
├── logs/           # Application logs
└── assets.db       # SQLite database
```

### Testing Strategy
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **UI Tests**: Streamlit interaction testing
- **Performance Tests**: Load testing for AI models

### CI/CD Pipeline
- **Linting**: Black, flake8, mypy
- **Testing**: pytest with coverage
- **Security**: Safety dependency checking
- **Docker**: Automated image building
- **Deployment**: GitHub Actions for automated deployment

## 📞 Support & Contributing

For questions, issues, or contributions, please refer to the project's issue tracker and contribution guidelines.

**Version**: 1.0.0
**Last Updated**: January 2026
**Authors**: Adora ML Team
