# Workshop: Building an AI-Powered Audio Transcription & Editing App

## Overview
This interactive workshop teaches students how to build a modular, production-ready web application that integrates AI services for audio transcription and editing. Using FastAPI and ElevenLabs API, you'll create an intelligent audio processing system that chunks audio files, transcribes them, and provides an interactive interface for validation and editing.

## Learning Objectives
By the end of this workshop, you will understand:
- **Why Virtual Environments Matter:** Dependency isolation and reproducible development
- **Modular Application Design:** Clean architecture and separation of concerns
- **AI API Integration:** Working with external AI services (ElevenLabs)
- **Real-time Web Applications:** Interactive user interfaces with FastAPI
- **Audio Processing:** Chunking audio without breaking words
- **Data Validation:** User feedback and content editing workflows

## Why This Matters
- **Virtual Environments:** Prevent dependency conflicts and ensure consistent deployments
- **Modular Design:** Makes code maintainable, testable, and scalable
- **AI Integration:** Learn to leverage external AI services effectively
- **Production Readiness:** Build applications that can handle real-world scenarios

## Prerequisites
- Basic Python knowledge
- Understanding of web development concepts
- Access to ElevenLabs API (free tier available)
- Audio files for testing (provided)

## Project Structure
```
audio_transcription_app/
├── venv/                    # Virtual environment (why isolation matters)
├── app/
│   ├── main.py             # FastAPI main application
│   ├── models/             # Data models (modular design)
│   ├── services/           # Business logic (separation of concerns)
│   ├── api/                # API endpoints (clean interfaces)
│   └── static/             # Frontend files
├── audio_files/            # Input audio files
├── requirements.txt        # Dependency management
└── README.md              # Documentation

```

## Workshop Steps

### Step 1: Understanding Virtual Environments (20 minutes)
**Goal:** Learn why virtual environments are crucial for Python development

**The Problem Without Virtual Environments:**
- Global package conflicts
- Version incompatibilities
- Difficult deployment
- Unreproducible environments

**Instructions:**
1. Create project directory:
   ```bash
   mkdir audio_transcription_app
   cd audio_transcription_app
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Observe the difference:
   ```bash
   which python  # Should point to venv/bin/python
   pip list      # Should show minimal packages
   ```

**Interactive Exercise:** Try installing a package both globally and in venv to see the difference.

### Step 2: Setting Up Modular Architecture (30 minutes)
**Goal:** Understand why modular design matters

**Instructions:**
1. Create the modular structure:
   ```bash
   mkdir -p app/{models,services,api,static}
   touch app/__init__.py app/main.py
   touch app/models/__init__.py app/services/__init__.py app/api/__init__.py
   ```

2. Install dependencies:
   ```bash
   pip install fastapi uvicorn python-multipart requests pydub
   ```

3. Create requirements.txt:
   ```bash
   pip freeze > requirements.txt
   ```

**Why This Matters:**
- **models/**: Data structures and validation
- **services/**: Business logic and AI integration
- **api/**: REST endpoints and web interface
- **static/**: Frontend assets

### Step 3: Audio Processing Service (45 minutes)
**Goal:** Build intelligent audio chunking

**The Challenge:** Split audio into ~30-second chunks without breaking words

**Instructions:**
Create `app/services/audio_processor.py`:
- Load audio files using pydub
- Implement smart chunking algorithm
- Detect silence for natural break points
- Handle edge cases (very short/long files)

**Interactive Challenge:** Process different types of audio and observe chunking behavior.

### Step 4: ElevenLabs Integration (45 minutes)
**Goal:** Integrate external AI service for transcription

**Instructions:**
Create `app/services/transcription_service.py`:
- Set up ElevenLabs API client
- Handle authentication and rate limiting
- Process audio chunks asynchronously
- Implement error handling and retries

**AI Integration Best Practices:**
- API key management
- Rate limiting respect
- Error handling
- Fallback strategies

### Step 5: Data Models and Validation (30 minutes)
**Goal:** Create robust data structures

**Instructions:**
Create `app/models/audio_models.py`:
- AudioFile model
- TranscriptionChunk model
- ValidationResult model
- User feedback models

**Why Models Matter:**
- Data validation
- API documentation
- Type safety
- Database schema

### Step 6: Interactive Web Interface (60 minutes)
**Goal:** Build user-friendly validation interface

**Features:**
- Audio player for each chunk
- Editable transcription text
- Validation controls
- Progress tracking
- Export functionality

**Instructions:**
Create interactive HTML/JavaScript interface that:
- Plays audio chunks
- Shows transcriptions
- Allows text editing
- Submits validations

### Step 7: API Endpoints (45 minutes)
**Goal:** Create clean, RESTful API

**Endpoints:**
- `POST /upload` - Upload audio file
- `GET /chunks/{file_id}` - Get audio chunks
- `POST /transcribe/{chunk_id}` - Transcribe chunk
- `PUT /validate/{chunk_id}` - Update transcription
- `GET /export/{file_id}` - Export final results

### Step 8: Testing and Deployment (30 minutes)
**Goal:** Ensure production readiness

**Instructions:**
- Unit tests for services
- Integration tests for API
- Error handling scenarios
- Performance optimization

## Interactive Exercises Throughout

### Exercise 1: Virtual Environment Experiment
Compare package installations with and without virtual environments.

### Exercise 2: Modular vs Monolithic
Refactor a monolithic script into modular components.

### Exercise 3: API Integration
Handle different types of API responses and errors.

### Exercise 4: Audio Processing
Process various audio formats and lengths.

### Exercise 5: User Experience
Design intuitive validation workflows.

## Expected Outcomes
Students will build a complete, production-ready application demonstrating:
- Professional Python development practices
- Clean, modular architecture
- AI service integration
- Interactive web interfaces
- Error handling and validation

## Next Steps
- Deploy to cloud platform
- Add user authentication
- Implement batch processing
- Add more AI services
- Create mobile interface

---

*This workshop emphasizes hands-on learning with real-world applications, preparing students for professional AI development.* 