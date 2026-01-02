# 📚 Adora ML Core Model - Documentation

Welcome to the comprehensive documentation for Adora ML Core Model, your AI-powered creative assistant for retail media.

## 📖 Documentation Overview

This documentation set provides everything you need to understand, deploy, and use Adora effectively.

### 📋 Quick Start
- **[QUICK_START.md](QUICK_START.md)** - Get up and running in 5 minutes
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user manual for all features
- **[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)** - Technical architecture and data flow
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
- **[RELEASE_NOTES.md](RELEASE_NOTES.md)** - Version history and updates

## 🎯 What is Adora?

Adora ML Core Model is a comprehensive AI-powered platform for automated creative validation, layout correction, and final ad rendering in retail media. It integrates OCR, object detection, banned-phrase compliance, safe-zone checking, and auto-layout optimization into one unified pipeline.

### Key Capabilities
- 🔍 **Smart Creative Validation** - OCR, YOLO detections, banned-phrase scanning
- 🎨 **AI Auto-Fix Engine** - Automatic adjustments for compliance and quality
- 🧠 **Background Removal** - Clean product cutouts using segmentation
- ⚡ **FastAPI Backend** - High-performance API with automatic documentation
- 🖼️ **Multi-Format Generation** - Instagram, Facebook, and banner formats
- 🛠️ **Modern Streamlit Frontend** - User-friendly interface for all users

## 🚀 Getting Started

### For Users
1. **Read the [Quick Start Guide](QUICK_START.md)** to set up your environment
2. **Follow the [User Guide](USER_GUIDE.md)** to learn all features
3. **Check [Release Notes](RELEASE_NOTES.md)** for the latest updates

### For Developers
1. **Study the [Project Architecture](PROJECT_ARCHITECTURE.md)** for system understanding
2. **Use the [API Reference](API_REFERENCE.md)** for integration
3. **Review [Release Notes](RELEASE_NOTES.md)** for migration guidance

## 🏗️ System Architecture

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

### Technology Stack
- **Backend**: FastAPI, SQLite, PyTorch, OpenCV
- **Frontend**: Streamlit, Matplotlib, Pandas
- **AI/ML**: Stable Diffusion, DETR Object Detection, Tesseract OCR
- **Infrastructure**: Docker, Uvicorn, JWT Authentication

## 📊 Key Features

### Asset Management
- Upload and organize creative assets
- Version control with rollback capabilities
- Batch processing for multiple assets
- Comprehensive metadata tracking

### AI-Powered Analysis
- Object detection and auto-tagging
- Color analysis and brightness evaluation
- Text extraction via OCR
- Complexity scoring and quality metrics

### Creative Generation
- Multi-format ad creation (Story, Feed, Banner)
- Marketing text generation
- Quality evaluation and compliance checking
- Background removal and image manipulation

### Compliance & Validation
- Tesco brand guideline validation
- Alcohol content disclaimer checking
- Accessibility and readability assessment
- Safe zone verification for social media

### Analytics & Reporting
- Real-time dashboard with KPIs
- Upload trend analysis
- System health monitoring
- CSV export for comprehensive reporting

## 🔧 Installation & Setup

### Prerequisites
- Python 3.9+
- Tesseract OCR
- Git
- Optional: CUDA-compatible GPU

### Quick Setup
```bash
# Clone repository
git clone <repository-url>
cd Adora-ML-CoreModel

# Install Tesseract
winget install -e --id UB-Mannheim.TesseractOCR

# Setup backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Setup frontend
cd ../frontend
pip install -r requirements.txt

# Start services
Terminal 1: cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
Terminal 2: cd frontend && streamlit run streamlit_app.py
```

## 📡 API Access

- **Base URL**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs (Swagger UI)
- **Authentication**: JWT Bearer tokens
- **Rate Limits**: 1000 requests/hour per user

### Example API Call
```python
import requests

# Login
response = requests.post('http://localhost:8000/login',
    data={'username': 'user', 'password': 'pass'})
token = response.json()['access_token']

# Upload asset
headers = {'Authorization': f'Bearer {token}'}
files = {'file': open('image.jpg', 'rb')}
response = requests.post('http://localhost:8000/upload_packshot',
    files=files, headers=headers)
```

## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines:

1. **Fork** the repository
2. **Create** a feature branch
3. **Commit** your changes
4. **Push** to the branch
5. **Open** a Pull Request

### Development Setup
- Follow the installation steps above
- Use virtual environments for dependency management
- Write tests for new features
- Update documentation for API changes

## 📞 Support & Community

### Getting Help
- **Documentation**: This docs folder contains comprehensive guides
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join community conversations
- **API Docs**: Interactive API documentation at `/docs`

### Enterprise Support
- **Professional Services**: Custom integrations and training
- **SLA Support**: 24/7 support for enterprise deployments
- **Consulting**: Architecture reviews and performance optimization

## 📜 License

This project is licensed under the MIT License - see the LICENSE file in the root directory for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **Streamlit** for the amazing frontend framework
- **PyTorch** and **Hugging Face** for AI model support
- **OpenCV** and **Pillow** for image processing
- **Tesseract** for OCR capabilities

**Version**: 1.0.0
**Release Date**: January 2, 2026
**Documentation Updated**: January 2, 2026

*Built with ❤️ for the creative community*