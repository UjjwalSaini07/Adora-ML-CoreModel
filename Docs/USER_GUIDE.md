# Adora ML Core Model - User Guide

## 🎨 Welcome to Adora

Adora is your AI-powered creative assistant for retail media. This guide will help you make the most of its features for creating compliant, high-quality advertising assets.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Dashboard Overview](#dashboard-overview)
- [Asset Management](#asset-management)
- [Image Editing](#image-editing)
- [AI Analysis](#ai-analysis)
- [Creative Generation](#creative-generation)
- [Compliance Validation](#compliance-validation)
- [Version Control](#version-control)
- [Best Practices](#best-practices)

## 🚀 Getting Started

### First Login
1. Open your browser to the Adora interface
2. Click the **Register** tab to create an account
3. Fill in your username, email, and password
4. Click **Register** and then **Login** with your credentials

### System Requirements
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Internet**: Stable connection for AI processing
- **Storage**: At least 5GB free space for assets and models

## 📊 Dashboard Overview

The dashboard provides comprehensive insights into your creative operations.

### Key Metrics
- **Total Assets**: Number of uploaded creative assets
- **Processed Assets**: Assets that have been analyzed or modified
- **Compliance Rate**: Percentage of compliant assets
- **Average File Size**: Typical asset size for optimization planning

### Analytics Charts
- **Upload Trends**: Daily asset upload patterns
- **Weekly Performance**: Activity breakdown by day of week
- **File Size Distribution**: Asset size analysis and optimization tips
- **System Health**: Real-time performance monitoring

### Quick Actions
- **Clean Up Assets**: Remove assets older than 30 days
- **Generate Report**: Create comprehensive analytics report
- **System Maintenance**: Run health checks and diagnostics
- **Backup Data**: Create system backup

## 📁 Asset Management

### Uploading Assets
1. In the sidebar, locate **"Upload New Asset"**
2. Click to select an image file (PNG, JPG, JPEG)
3. Add an optional label for organization
4. Click **"Upload Asset"**

### Asset Library
- **Search**: Use the search bar to find assets by label
- **Preview**: Click on assets to view them
- **Select**: Use the **"Select for Editing"** button to choose assets for other tools

### Batch Operations
For multiple assets, use the API endpoints or contact your administrator for bulk upload tools.

## ✏️ Image Editing

### Basic Adjustments
1. Go to **"Image Editor"** in the navigation
2. Select an asset using the ID input or from the Asset Library
3. Use the **"Basic Adjustments"** expander for:
   - **Background Removal**: AI-powered cutout creation
   - **Resize**: Change dimensions while maintaining aspect ratio
   - **Rotation**: Rotate image by degrees
   - **Crop**: Define exact crop coordinates

### Advanced Filters
- **Brightness**: Adjust image brightness (-100% to +100%)
- **Contrast**: Enhance or reduce contrast
- **Sharpness**: Increase clarity and detail

### Text Overlay
- **Text Content**: Enter text to add to image
- **Position**: Set X,Y coordinates for placement
- **Font Size**: Adjust text size (10-100px)

### Processing Workflow
1. Configure all desired adjustments
2. Click **"Apply Changes"**
3. Wait for processing to complete
4. Check Asset Library for the new version

## 🤖 AI Analysis

### Running Analysis
1. Navigate to **"AI Analysis"**
2. Enter or select an asset ID
3. Click **"Analyze Image"**

### Analysis Results

#### Basic Metrics
- **Dimensions**: Width × Height in pixels
- **File Size**: Storage size in KB
- **Aspect Ratio**: Width/Height ratio

#### Color Analysis
- **Average Color**: Dominant color with RGB values
- **Brightness**: Overall image brightness (0-255)
- **Color Picker**: Visual color representation

#### Technical Metrics
- **Complexity Score**: Image detail level (0-1)
- **Text Detection**: Whether text is present in the image

#### AI-Powered Insights
- **Auto-Tags**: Automatically generated descriptive tags
- **Object Detection**: Identified objects with confidence scores
- **Extracted Text**: OCR results from any visible text

### Using Analysis Results
- **Tagging**: Use auto-tags for organization
- **Compliance**: Check for restricted content (people detection)
- **Optimization**: Identify images needing brightness/contrast adjustment

## 🎨 Creative Generation

### AI Creative Assistant
1. Go to **"AI Creative Assistant"**
2. Select a packshot asset
3. Choose generation options:
   - **Generate Ad Creatives**: Create images for social media
   - **Include Detailed Analysis**: Show technical breakdown

### Generated Formats
- **Instagram Story**: 9:16 vertical format (1080×1920)
- **Instagram Feed**: 1:1 square format (1080×1080)
- **Facebook Banner**: 1.91:1 horizontal format (1200×628)

### Evaluation Metrics
Each generated creative includes:
- **Brightness**: Optimal lighting check
- **Contrast**: Visual appeal measurement
- **Text Readability**: Legibility assessment
- **Layout Balance**: Composition quality score
- **Safe Zone Compliance**: Platform guideline adherence
- **Platform Suitability**: Format compatibility

### Marketing Text
Automatically generated:
- **Headline**: Attention-grabbing main text
- **Subhead**: Supporting descriptive text
- **Disclaimer**: Legal compliance text
- **Tags**: Relevant categorization labels

## ✅ Compliance Validation

### Content Guidelines
1. Go to **"Compliance Check"**
2. Use the **"Content Guidelines"** section for text validation
3. Enter your creative copy:
   - **Headline**: Main advertising text
   - **Subheadline**: Supporting text
   - **Disclaimer**: Legal text (required for alcohol content)
   - **Tags**: Availability or promotional labels

### Validation Rules
- **Forbidden Terms**: No guarantees, money-back claims, or sustainability statements
- **Alcohol Content**: Requires "drinkaware" disclaimer
- **Tesco Tags**: Must use approved availability text
- **Accessibility**: Minimum 20px font size recommended

### Image Compliance
1. Enter an asset ID for image validation
2. The system checks for:
   - **Text Detection**: Ensures readable fonts
   - **Safe Zones**: Proper spacing for social media
   - **Brand Guidelines**: Tesco-specific requirements

### Issue Types
- **Hard Fail**: Must be fixed before use
- **Warning**: Recommended improvements

## 📚 Version Control

### Viewing History
1. Navigate to **"Version History"**
2. Enter an asset ID
3. Click **"Load Version History"**

### Version Information
Each version shows:
- **Version Number**: Sequential version ID
- **Operation**: What was done (upload, manipulate, restore)
- **Timestamp**: When the version was created
- **Parameters**: Technical details of changes
- **Creator**: Who made the changes

### Restoring Versions
1. Find the desired version in the history
2. Click **"Restore to Version X"**
3. Confirm the restoration
4. The asset reverts to that version (creates new version)

### Comments
- **Add Comments**: Document changes or approvals
- **View Discussion**: See team feedback on versions
- **Version-Specific**: Comment on particular iterations

## 💡 Best Practices

### Asset Preparation
- **High Resolution**: Start with high-quality images (at least 1000px on longest side)
- **Clean Backgrounds**: Use solid backgrounds for best AI processing
- **Proper Lighting**: Well-lit subjects for better analysis
- **Square Crops**: Consider 1:1 aspect ratios for flexibility

### File Management
- **Naming Convention**: Use descriptive labels (e.g., "Coca-Cola-6Pack-Front")
- **Organization**: Group related assets with consistent naming
- **Regular Cleanup**: Remove unused assets to save storage
- **Backup**: Regular system backups for important work

### Compliance First
- **Early Validation**: Check compliance before finalizing creatives
- **Brand Guidelines**: Always follow Tesco requirements
- **Legal Review**: Have legal team approve alcohol-related content
- **Accessibility**: Ensure text is readable on mobile devices

### Performance Optimization
- **Batch Processing**: Process multiple similar assets together
- **GPU Usage**: Use GPU-enabled instances for faster AI processing
- **File Sizes**: Optimize images to under 500KB for web use
- **Caching**: Keep frequently used assets readily available

### Team Collaboration
- **Version Control**: Use versioning for all important changes
- **Comments**: Document decisions and approvals
- **Shared Assets**: Coordinate with team members on asset usage
- **Regular Reviews**: Schedule periodic compliance and quality checks

## 🔧 Troubleshooting

### Common Issues

**Upload Failures:**
- Check file format (PNG, JPG, JPEG only)
- Ensure file size under 10MB
- Verify network connection

**Processing Errors:**
- Try smaller images for initial testing
- Check system resources (memory, disk space)
- Restart the application if needed

**AI Model Issues:**
- Allow time for initial model loading (2-5 minutes)
- Ensure stable internet for model downloads
- Check GPU memory if using CUDA

**Compliance Warnings:**
- Review Tesco brand guidelines
- Ensure all required disclaimers are present
- Check font sizes and contrast ratios

### Getting Help
- **Documentation**: Check this guide and API reference
- **Logs**: Review application logs for error details
- **Community**: Join discussions for tips and solutions
- **Support**: Contact your system administrator for technical issues

## 📈 Advanced Features

### API Integration
- **REST API**: Full programmatic access to all features
- **Batch Operations**: Process multiple assets simultaneously
- **Custom Workflows**: Build automated creative pipelines

### Analytics & Reporting
- **Custom Reports**: Generate detailed analytics
- **Performance Tracking**: Monitor system and user metrics
- **Export Capabilities**: CSV downloads for external analysis

### System Administration
- **Health Monitoring**: Real-time system diagnostics
- **User Management**: Admin controls for user accounts
- **Backup & Recovery**: Comprehensive data protection

**Version**: 1.0.0
**Last Updated**: January 2026

*Happy creating with Adora! 🎨*