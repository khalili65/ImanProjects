# 🎵 Audio Transcription App - Setup Guide

## Overview
This guide will walk you through setting up the AI Audio Transcription & Editing application. This is an educational project designed to teach:

- **Virtual Environment Management** 🔧
- **Modular Application Architecture** 🏗️
- **AI API Integration** 🤖
- **Interactive Web Development** 🌐
- **Production-Ready Practices** 🚀

## Prerequisites
- Python 3.8 to 3.12 (see troubleshooting for 3.12 specific issues)
- Basic command line knowledge
- Audio files for testing (MP3, WAV, M4A, etc.)

## Quick Start (If you're having installation issues)

### Option 1: Minimal Installation
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install minimal requirements (safer for Python 3.12)
pip install -r requirements-minimal.txt

# Run the app
python run_app.py
```

### Option 2: Full Installation (try this first)
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install full requirements
pip install -r requirements.txt

# Run the app
python run_app.py
```

## Step 1: Understanding Virtual Environments

### Why Virtual Environments Matter
```bash
# Without virtual environments:
pip install package-v1.0  # Global installation
# Later...
pip install package-v2.0  # Breaks other projects!

# With virtual environments:
python -m venv myproject  # Isolated environment
source myproject/bin/activate  # Activate
pip install package-v1.0  # Safe, isolated installation
```

### Benefits:
- ✅ **Dependency Isolation**: No conflicts between projects
- ✅ **Reproducible Environments**: Same setup across machines
- ✅ **Easy Deployment**: Clear dependency management
- ✅ **Collaboration**: Team members get identical setups

### Create Virtual Environment
```bash
# Navigate to project directory
cd audio_transcription_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

## Step 2: Install Dependencies

### Understanding requirements.txt
The `requirements.txt` file specifies exact package versions:

```
fastapi==0.104.1    # Web framework
uvicorn==0.24.0     # ASGI server
pydantic==2.5.0     # Data validation
librosa>=0.10.0     # Audio processing (optional)
pydub==0.25.1       # Audio manipulation
```

### Install packages:
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt

# If you get installation errors, try minimal version:
pip install -r requirements-minimal.txt

# Verify installation
pip list
```

## Troubleshooting

### Python 3.12 "distutils" Error

**Problem**: You see `ModuleNotFoundError: No module named 'distutils'`

**Solution Options**:

#### Option A: Use Minimal Installation
```bash
# Install only essential packages
pip install -r requirements-minimal.txt
```
The app will work with basic audio processing using pydub only.

#### Option B: Install System Dependencies First
```bash
# On macOS (with Homebrew):
brew install portaudio
export SYSTEM_VERSION_COMPAT=0

# On Ubuntu/Debian:
sudo apt-get update
sudo apt-get install build-essential python3-dev libffi-dev

# Then try installing requirements
pip install setuptools wheel
pip install -r requirements.txt
```

#### Option C: Install Packages Individually
```bash
# Install core packages first
pip install fastapi uvicorn pydantic requests python-dotenv

# Install audio packages one by one
pip install pydub
pip install --no-build-isolation numpy
pip install --no-build-isolation librosa
```

#### Option D: Use Conda (if available)
```bash
# Create conda environment
conda create -n audio-app python=3.11
conda activate audio-app

# Install packages via conda
conda install -c conda-forge librosa pydub fastapi uvicorn
pip install -r requirements-minimal.txt
```

### Other Common Issues:

1. **"ModuleNotFoundError"**
   ```bash
   # Solution: Check virtual environment and dependencies
   which python  # Should show venv path
   pip install -r requirements-minimal.txt
   ```

2. **"Port 8000 already in use"**
   ```bash
   # Solution: Use different port
   uvicorn app.main:app --port 8001
   ```

3. **"Permission denied" errors**
   ```bash
   # Solution: Check file permissions
   chmod +x run_app.py
   ```

4. **Audio processing errors**
   ```bash
   # Solution: Install system dependencies
   # macOS:
   brew install ffmpeg
   # Ubuntu:
   sudo apt-get install ffmpeg
   ```

5. **Compiler errors on Windows**
   ```bash
   # Install Microsoft Visual C++ Build Tools
   # Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   # Or use pre-compiled wheels:
   pip install --only-binary=all librosa
   ```

## Step 3: Environment Configuration

### Create .env file (optional for ElevenLabs API):
```bash
# Copy example configuration
cp env.example .env

# Edit with your settings
nano .env
```

### Environment Variables:
```bash
# ElevenLabs API (optional - app works with mock service)
ELEVENLABS_API_KEY=your_api_key_here

# Application settings
MAX_FILE_SIZE_MB=50
CHUNK_DURATION_SECONDS=30
```

## Step 4: Understanding the Application Architecture

### Directory Structure Explained:
```
audio_transcription_app/
├── app/
│   ├── main.py                 # 🌐 FastAPI application entry point
│   ├── models/                 # 📊 Data structures and validation
│   │   └── audio_models.py     # Pydantic models for type safety
│   ├── services/               # 🔧 Business logic layer
│   │   ├── audio_processor.py  # Audio chunking algorithms
│   │   └── transcription_service.py  # AI API integration
│   ├── api/                    # 🛣️ REST endpoints
│   └── static/                 # 🎨 Frontend files
│       └── index.html          # Interactive web interface
├── audio_files/                # 📁 File storage
├── requirements.txt            # 📦 Dependencies
├── requirements-minimal.txt    # 📦 Minimal dependencies
└── run_app.py                  # 🚀 Startup script
```

### Why This Structure?
- **Separation of Concerns**: Each module has a single responsibility
- **Testability**: Individual components can be tested in isolation
- **Maintainability**: Changes in one area don't affect others
- **Scalability**: Easy to add new features or services
- **Graceful Degradation**: Works with or without optional dependencies

## Step 5: Run the Application

### Method 1: Using the startup script (Recommended for learning)
```bash
python run_app.py
```

This script will:
- ✅ Check Python version
- ✅ Verify virtual environment
- ✅ Validate dependencies
- ✅ Create necessary directories
- ✅ Start the server with helpful information

### Method 2: Direct uvicorn command
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 6: Access the Application

### Web Interface
- **Main App**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Architecture Info**: http://localhost:8000/api/architecture

### Test the Application
1. **Upload an audio file** (drag & drop or choose file)
2. **Watch the processing** (chunking and transcription)
3. **Edit transcriptions** interactively
4. **Rate confidence** using star ratings
5. **Export results** in different formats

## Understanding Feature Availability

The application works in two modes:

### Full Mode (with librosa/soundfile):
- ✅ Advanced audio analysis
- ✅ Precise duration calculation
- ✅ Detailed audio metadata
- ✅ Optimized chunking algorithms

### Basic Mode (pydub only):
- ✅ Basic audio processing
- ✅ File format conversion
- ✅ Simple chunking
- ✅ All core functionality

The app automatically detects available libraries and adjusts accordingly.

## Step 7: Understanding Key Concepts

### 1. Audio Chunking Strategy
```python
# The app intelligently chunks audio by:
# 1. Detecting silence for natural breaks
# 2. Combining short segments to target duration (~30s)
# 3. Falling back to time-based chunking if needed

# Why this matters for AI transcription:
# - Preserves word boundaries
# - Optimizes API usage
# - Improves accuracy
```

### 2. Asynchronous Processing
```python
# Background tasks don't block the UI:
@app.post("/api/upload")
async def upload_file(background_tasks: BackgroundTasks):
    # File processing happens in background
    background_tasks.add_task(transcribe_chunks)
    return {"status": "processing"}  # Immediate response
```

### 3. Error Handling & Validation
```python
# Input validation with Pydantic:
class AudioFileModel(BaseModel):
    filename: str
    file_size: int
    duration_seconds: float  # Automatic type checking

# API error handling:
try:
    result = await api_call()
except Exception as e:
    logger.error(f"API error: {e}")
    return {"error": "Service unavailable"}
```

### 4. Graceful Degradation
```python
# Handle missing dependencies gracefully:
try:
    import librosa
    HAS_ADVANCED_AUDIO = True
except ImportError:
    HAS_ADVANCED_AUDIO = False
    # Use fallback methods
```

## Development Workflow

### 1. Making Changes
```bash
# The app runs with --reload, so changes auto-update
# Edit any .py file and see changes immediately
```

### 2. Testing
```bash
# Run the test suite
python -m pytest tests/

# Test specific functionality
python -m pytest tests/test_audio_processor.py
```

### 3. Adding Features
1. **Models**: Add new Pydantic models in `app/models/`
2. **Services**: Implement business logic in `app/services/`
3. **APIs**: Create endpoints in `app/api/` or `app/main.py`
4. **Frontend**: Modify `app/static/index.html`

## Educational Exercises

### Exercise 1: Virtual Environment Experiment
```bash
# Try this to see the difference:
deactivate  # Exit virtual environment
pip list    # See global packages
source venv/bin/activate  # Re-enter venv
pip list    # See isolated packages
```

### Exercise 2: Add a New Feature
Try adding a new API endpoint:
```python
@app.get("/api/files/{file_id}/stats")
async def get_file_stats(file_id: str):
    # Your implementation here
    return {"word_count": 150, "average_confidence": 0.95}
```

### Exercise 3: Customize Audio Processing
Modify the chunking parameters in `audio_processor.py`:
```python
# Try different values and see the effect:
chunk_duration=20,      # 20 seconds instead of 30
silence_thresh=-30      # Different silence threshold
```

## Production Considerations

### What would change in production?
1. **Database**: Replace in-memory storage with PostgreSQL/MongoDB
2. **File Storage**: Use AWS S3 or similar cloud storage
3. **Authentication**: Add user management and API keys
4. **Monitoring**: Add logging, metrics, and health checks
5. **Scaling**: Use containers and load balancers
6. **Security**: HTTPS, rate limiting, input sanitization

### Environment Management
```bash
# Production deployment:
pip freeze > requirements-production.txt  # Lock exact versions
docker build -t audio-transcription .      # Containerize
kubectl deploy audio-transcription.yaml    # Deploy to Kubernetes
```

## Next Steps

1. **Experiment** with different audio files
2. **Modify** the chunking algorithms
3. **Add** new features (user authentication, batch processing)
4. **Deploy** to a cloud platform
5. **Share** your learnings with the team

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Models**: https://pydantic-docs.helpmanual.io/
- **Audio Processing**: https://librosa.org/doc/latest/
- **ElevenLabs API**: https://docs.elevenlabs.io/

---

## Support

If you encounter issues:
1. **Try minimal installation** first: `pip install -r requirements-minimal.txt`
2. Check this guide's troubleshooting section
3. Review the application logs
4. Test with the health check endpoint
5. Ask questions in the team chat

**Remember**: The app works great even without advanced audio libraries! 🚀 