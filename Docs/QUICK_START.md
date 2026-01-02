# Adora ML Core Model - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide will help you get Adora ML Core Model up and running on your local machine.

### Prerequisites

- **Python 3.9+** installed
- **Git** for cloning the repository
- **Tesseract OCR** for text recognition
- **Optional**: CUDA-compatible GPU for AI acceleration

### 1. Clone the Repository

```bash
git clone https://github.com/UjjwalSaini07/Adora-ML-CoreModel.git
cd Adora-ML-CoreModel
```

### 2. Install Tesseract OCR

**Windows (PowerShell):**
```bash
winget install -e --id UB-Mannheim.TesseractOCR
```

**Verify Installation:**
```bash
tesseract --version
```

### 3. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with your settings (especially JWT_SECRET)
```

### 4. Set Up Frontend

```bash
# Open new terminal, navigate to frontend directory
cd frontend

# Install dependencies
pip install -r requirements.txt
```

### 5. Start the Services

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

### 6. Access the Application

- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000

## 🎯 First Steps

### 1. Register an Account
1. Open the Streamlit app at http://localhost:8501
2. Click on "Register" tab
3. Create your account with username, email, and password

### 2. Upload Your First Asset
1. Log in with your credentials
2. In the sidebar, use the "Upload New Asset" section
3. Select an image file (PNG, JPG, JPEG)
4. Add an optional label
5. Click "Upload Asset"

### 3. Explore Features
- **Dashboard**: View analytics and system health
- **Asset Library**: Browse and manage your uploaded assets
- **Image Editor**: Apply transformations to your images
- **AI Analysis**: Get intelligent insights about your assets
- **Compliance Check**: Validate content against brand guidelines

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check if port 8000 is available
- Ensure all dependencies are installed
- Verify Python version (3.9+ required)

**Frontend connection errors:**
- Confirm backend is running on port 8000
- Check firewall settings
- Verify BACKEND_URL in streamlit_app.py

**AI models not loading:**
- GPU: Install CUDA drivers and PyTorch with CUDA support
- CPU: Models will load slower but still work
- Check available disk space (models require ~10GB)

**Tesseract errors:**
- Ensure Tesseract is installed and in PATH
- On Windows, restart terminal after installation

### Performance Tips

- **GPU Acceleration**: Install CUDA for faster AI processing
- **Memory**: Close other applications for better performance
- **Storage**: Ensure at least 20GB free space for models and assets
- **Network**: Stable internet connection for model downloads

## 📚 Next Steps

### Learn More
- [Project Architecture](PROJECT_ARCHITECTURE.md) - Deep dive into system design
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Release Notes](RELEASE_NOTES.md) - Version history and updates

### Development
- **Contributing**: Check GitHub for contribution guidelines
- **Issues**: Report bugs or request features
- **Discussions**: Join community conversations

### Production Deployment
- **Docker**: Use provided Docker setup for containerized deployment
- **Cloud**: Deploy to AWS/GCP/Azure for production use
- **Scaling**: Configure load balancing for multiple users

**Need Help?** Check the [troubleshooting section](#-troubleshooting) or create an issue on GitHub.

**Happy Creating! 🎨**