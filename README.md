# Adora ML Core Model

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/UjjwalSaini07/Adora-ML-CoreModel)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Adora ML Core Model is a comprehensive AI-powered platform for automated creative validation, layout correction, and final ad rendering in retail media. The system provides end-to-end creative intelligence for marketing automation, integrating OCR, object detection, compliance checking, and auto-layout optimization.

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [⭐ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📚 Documentation](#-documentation)
- [🔧 Installation](#-installation)
- [🎨 Usage](#-usage)
- [🔌 API Reference](#-api-reference)
- [📊 System Requirements](#-system-requirements)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)

## 🎯 Overview

Adora is designed for retail media creative management, providing AI-powered tools for:

- **Smart Creative Validation**: OCR, YOLO object detection, banned-phrase scanning, brand compliance
- **AI Auto-Fix Engine**: Automatic adjustments for font size, color, contrast, and safe-zone placement
- **Background Removal**: Clean product cutouts using advanced segmentation
- **Multi-Format Generation**: Instagram Stories, Feed posts, Facebook banners
- **Version Control**: Asset versioning with rollback capabilities
- **Compliance Automation**: Tesco brand guidelines and legal requirements validation

## ⭐ Key Features

### 🤖 AI-Powered Analysis
- **Object Detection**: Facebook DETR model for identifying objects and people
- **OCR Processing**: Tesseract-powered text extraction from images
- **Color Analysis**: RGB values, brightness, and contrast evaluation
- **Complexity Scoring**: Image detail and composition analysis
- **Auto-Tagging**: Intelligent content categorization

### 🎨 Creative Generation
- **Stable Diffusion XL**: High-quality image generation for advertising
- **Marketing Text**: AI-generated headlines, subheads, and disclaimers
- **Multi-Format Support**: Optimized outputs for different social platforms
- **Quality Evaluation**: Automated assessment of generated content

### ✅ Compliance & Validation
- **Tesco Guidelines**: Automated brand compliance checking
- **Alcohol Content**: Drinkaware disclaimer validation
- **Accessibility**: Font size and readability requirements
- **Safe Zones**: Platform-specific spacing validation

### 📊 Analytics & Monitoring
- **Real-time Dashboard**: Live KPIs and performance metrics
- **Upload Trends**: Daily and weekly activity analysis
- **System Health**: CPU, memory, and API response monitoring
- **CSV Export**: Comprehensive reporting capabilities

### 🔧 Developer Features
- **RESTful API**: Complete programmatic access via FastAPI
- **Version Control**: Asset history with rollback capabilities
- **Batch Operations**: Bulk processing for multiple assets
- **Environment Configuration**: Flexible deployment settings

## 🏗️ Architecture

### System Components

<img width="1550" height="834" alt="diagram-export-03-01-2026-13_55_20" src="https://github.com/user-attachments/assets/2a02f3b2-965a-46cb-9d9f-c6d64df3742a" />

### Technology Stack

**Backend:**
- **Framework**: FastAPI (async Python web framework)
- **Database**: SQLite3 with custom ORM layer
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI/ML**: PyTorch, Transformers, Diffusers, OpenCV
- **OCR**: Tesseract OCR engine

**Frontend:**
- **Framework**: Streamlit with custom CSS styling
- **Visualization**: Matplotlib, Plotly integration
- **HTTP Client**: Requests library for API communication

**Infrastructure:**
- **Containerization**: Docker support with multi-stage builds
- **Process Management**: Uvicorn ASGI server
- **Logging**: Rotating file handler with configurable levels
- **Environment**: Configurable via `.env` files

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git
- Tesseract OCR (for text recognition)
- Optional: CUDA-compatible GPU

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/UjjwalSaini07/Adora-ML-CoreModel.git
   cd Adora-ML-CoreModel
   ```

2. **Install Tesseract OCR:**
   ```bash
   # Windows
   winget install -e --id UB-Mannheim.TesseractOCR

   # Verify installation
   tesseract --version
   ```

3. **Set up Backend:**
   ```bash
   cd backend

   # Create virtual environment
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Install dependencies
   pip install -r requirements.txt

   # Configure environment
   cp .env.example .env
   ```

4. **Set up Frontend:**
   ```bash
   cd ../frontend
   pip install -r requirements.txt
   ```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run streamlit_app.py
```

**Access the application:**
- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000

### First Steps
1. Register a new account
2. Upload your first asset
3. Explore the dashboard analytics
4. Try AI analysis on your assets
5. Generate creative variations

## 📚 Documentation

Comprehensive documentation is available in the `Docs/` folder:

- **[📖 Project Architecture](Docs/PROJECT_ARCHITECTURE.md)** - Technical architecture and data flow
- **[🚀 Quick Start Guide](Docs/QUICK_START.md)** - Step-by-step setup instructions
- **[👥 User Guide](Docs/USER_GUIDE.md)** - Complete user manual and best practices
- **[🔌 API Reference](Docs/API_REFERENCE.md)** - Complete API documentation
- **[📋 Release Notes](Docs/RELEASE_NOTES.md)** - Version history and updates
- **[📚 Documentation Hub](Docs/README.md)** - Central documentation index

## 🔧 Installation

### Development Setup
```bash
# Clone repository
git clone https://github.com/UjjwalSaini07/Adora-ML-CoreModel.git
cd Adora-ML-CoreModel
```
```bash
# Backend setup
cd backend
python -m venv venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```
```bash
# Frontend setup
cd ../frontend
pip install -r requirements.txt
```

### Docker Setup (Future)
```bash
# Build and run with Docker
docker-compose up --build
```

### Production Deployment
- Configure environment variables in `.env`
- Set up reverse proxy (nginx)
- Configure SSL certificates
- Set up monitoring and logging
- Configure backup procedures

## 🎨 Usage

### For Users
1. **Access the web interface** at http://localhost:8501
2. **Register/Login** with your credentials
3. **Upload assets** via the sidebar
4. **Navigate between features** using the sidebar menu:
   - Dashboard: Analytics and KPIs
   - Asset Library: Browse and manage assets
   - Image Editor: Transform images
   - AI Analysis: Intelligent insights
   - Creative Generation: Ad creation
   - Compliance Check: Validation tools

### For Developers
- **API Access**: Use REST endpoints for integration
- **Environment Config**: Customize via `.env` files
- **Batch Operations**: Process multiple assets programmatically
- **Version Control**: Track asset changes and history

## 🔌 API Reference

The API provides comprehensive endpoints for all functionality:

### Authentication
```http
POST /register      # User registration
POST /login         # User authentication
GET  /me           # Current user info
```

### Asset Management
```http
POST /upload_packshot     # Upload single asset
POST /batch_upload        # Upload multiple assets
GET  /assets             # List all assets
GET  /asset/{id}         # Get specific asset
POST /manipulate_image    # Transform images
```

### AI & Analysis
```http
POST /analyze_image        # Comprehensive AI analysis
POST /generate_ad_assets   # Generate advertising creatives
POST /validate            # Content compliance
POST /validate_image      # Image compliance
```

### System Management
```http
POST /system_health    # System diagnostics
GET  /export_report    # CSV export
POST /generate_report  # Analytics report
```

**Full API Documentation**: http://localhost:8000/docs (when backend is running)

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **RAM**: 4GB
- **Storage**: 5GB free space
- **Python**: 3.9+
- **Network**: Stable internet connection

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **RAM**: 8GB+
- **Storage**: 20GB+ free space
- **GPU**: NVIDIA GPU with 4GB+ VRAM (optional, for faster AI processing)
- **Python**: 3.9+ with pip

### AI Model Requirements
- **Object Detection**: ~1GB disk space
- **Stable Diffusion**: ~10GB disk space
- **OCR Engine**: Tesseract OCR installed
- **CUDA**: Optional, enables GPU acceleration

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation for new features
- Ensure backward compatibility
- Test on multiple platforms

### Code Structure
```
Adora-ML-CoreModel/
├── backend/              # FastAPI backend
│   ├── main.py          # Application entry point
│   ├── db.py            # Database operations
│   ├── utils.py         # Image processing utilities
│   ├── guidelines.py    # Compliance validation
│   └── requirements.txt # Python dependencies
├── frontend/            # Streamlit frontend
│   ├── streamlit_app.py # Main application
│   └── requirements.txt # Python dependencies
├── storage/             # Generated assets and data
├── Docs/               # Documentation
└── README.md           # This file
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Core Technologies
- **FastAPI** - Modern, fast web framework
- **Streamlit** - Amazing frontend framework
- **PyTorch** - Deep learning framework
- **Hugging Face** - AI model hub
- **OpenCV** - Computer vision library
- **Pillow** - Image processing

### AI Models & Libraries
- **Facebook DETR** - Object detection
- **Stability AI SDXL** - Image generation
- **Tesseract OCR** - Text recognition
- **RemBG** - Background removal

### Community
- Open source contributors
- AI/ML research community
- FastAPI and Streamlit communities


## 📞 Support & Contact

- **Documentation**: Comprehensive guides in `Docs/` folder
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join community conversations
- **API Docs**: Interactive documentation at `/docs`

## 🏆 Version History

### v1.0.0 (Current)
- Complete AI-powered creative platform
- Advanced image analysis and generation
- Compliance automation
- Real-time analytics dashboard
- Version control system

### Previous Versions
- **v0.9.0**: Beta release with core AI features
- **v0.8.0**: Alpha release with basic functionality

**Full changelog**: See [Release Notes](Docs/RELEASE_NOTES.md)

**Built with ❤️ for the creative community**

*Adora ML Core Model - Transforming retail media creative workflows with AI*
