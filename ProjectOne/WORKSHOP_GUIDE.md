# Workshop: Building an Intelligent Quran Recitation App with Cursor AI

## Overview
This workshop introduces interns to the practical use of Cursor AI for developing intelligent, real-time web applications using FastAPI. You'll build a modular and layered web app inspired by Tarteel AI, designed to help users recite the Quran accurately. The application will capture live audio from a reciter, transcribe it on the fly using an ASR model (such as Whisper fine-tuned for Quranic recitation), and provide immediate feedback on recitation errors.

## Learning Objectives
By the end of this workshop, you will:
- Build a real-time web application using FastAPI
- Integrate speech recognition using Whisper models
- Handle Arabic text processing and comparison
- Implement live audio capture and processing
- Create interactive user interfaces with real-time feedback
- Learn to leverage AI-powered coding assistants like Cursor AI

## Prerequisites
- Basic Python knowledge
- Familiarity with web development concepts
- Access to Cursor AI
- Microphone for testing

## Database Setup

### Quran Database Structure
You've been provided with a SQLite database (`quran_workshop.db`) containing:

**Tables:**
1. **`suras`** - Surah information
   - `sura` (INTEGER): Surah number (1-114)
   - `name` (TEXT): Arabic name
   - `name_en` (TEXT): English name
   - `num_ayahs` (INTEGER): Number of verses

2. **`verses`** - Quranic verses
   - `sura` (INTEGER): Surah number
   - `ayah` (INTEGER): Verse number within surah
   - `text` (TEXT): Arabic text of the verse

3. **`page_mapping`** - Page layout mapping
   - `page` (INTEGER): Page number
   - `sura` (INTEGER): Surah number
   - `ayah` (INTEGER): Verse number

### Database Access Example
```python
import sqlite3

def connect_to_quran_db(db_path="quran_workshop.db"):
    conn = sqlite3.connect(db_path)
    return conn

def get_verse(conn, surah, ayah):
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM verses WHERE sura = ? AND ayah = ?", (surah, ayah))
    result = cursor.fetchone()
    return result[0] if result else None
```

## Workshop Steps

### Step 1: Project Setup and Environment (30 minutes)
**Goal:** Set up development environment and project structure

**Instructions:**
1. Create a new project folder: `quran_recitation_app`
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install initial dependencies:
   ```bash
   pip install fastapi uvicorn sqlite3 python-multipart
   ```

**Investigate:**
- Open Cursor AI and explore its features
- Create a basic FastAPI app structure
- Test that you can run a simple "Hello World" FastAPI application

**Challenge:** Create a basic FastAPI endpoint that returns "Bismillah" in Arabic

### Step 2: Database Integration (45 minutes)
**Goal:** Connect to the Quran database and create data access layer

**Instructions:**
1. Copy the provided `quran_workshop.db` to your project folder
2. Create a `database.py` module to handle database operations
3. Implement functions to:
   - Connect to the database
   - Retrieve verses by surah and ayah
   - Get page contents
   - Fetch surah information

**Investigate:**
- How is Arabic text stored in the database?
- What's the relationship between pages, surahs, and ayahs?
- Try querying different verses and observe the text format

**Challenge:** Create an API endpoint that returns a specific verse in JSON format

### Step 3: Audio Capture and Processing (60 minutes)
**Goal:** Implement live audio recording functionality

**Instructions:**
1. Install audio dependencies:
   ```bash
   pip install sounddevice soundfile numpy
   ```
2. Create an `audio.py` module for audio handling
3. Implement functions for:
   - Recording audio from microphone
   - Saving audio files
   - Basic audio preprocessing

**Investigate:**
- What sample rate works best for speech recognition?
- How do you handle different microphone configurations?
- What audio formats are supported?

**Challenge:** Create a web endpoint that can capture audio and save it temporarily

### Step 4: Speech Recognition Integration (90 minutes)
**Goal:** Integrate Whisper ASR model for Arabic speech recognition

**Instructions:**
1. Install speech recognition dependencies:
   ```bash
   pip install transformers torch torchaudio
   ```
2. Create a `speech_recognition.py` module
3. Implement ASR functionality using:
   - HuggingFace Transformers pipeline
   - Model: `tarteel-ai/whisper-base-ar-quran` (Quran-specific)
   - Fallback to `openai/whisper-base` if needed

**Key Implementation Details:**
```python
from transformers import pipeline

def load_asr_model():
    # Try Quran-specific model first
    try:
        asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="tarteel-ai/whisper-base-ar-quran",
            device="cpu"  # or "cuda" if available
        )
        return asr_pipeline
    except Exception as e:
        # Fallback to general Arabic model
        asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-base",
            device="cpu"
        )
        return asr_pipeline

def transcribe_audio(audio_file_path):
    # Implementation here
    pass
```

**Investigate:**
- How does the Quran-specific model differ from general Whisper?
- What preprocessing is needed for audio files?
- How do you handle model loading errors?

**Challenge:** Compare transcription accuracy between different models

### Step 5: Text Processing and Comparison (60 minutes)
**Goal:** Implement Arabic text processing and similarity comparison

**Instructions:**
1. Install text processing dependencies:
   ```bash
   pip install python-Levenshtein
   ```
2. Create a `text_processing.py` module
3. Implement functions for:
   - Removing Arabic diacritics (تشكيل)
   - Normalizing text spacing
   - Calculating similarity between texts
   - Handling partial matches

**Key Implementation Details:**
```python
import Levenshtein

def clean_arabic_text(text):
    """Remove diacritics and normalize Arabic text"""
    # Arabic diacritics Unicode ranges
    diacritics = [
        '\u064B', '\u064C', '\u064D', '\u064E', '\u064F',
        '\u0650', '\u0651', '\u0652', '\u0653', '\u0654',
        '\u0655', '\u0656', '\u0657', '\u0658', '\u0659',
        '\u065A', '\u065B', '\u065C', '\u065D', '\u065E',
        '\u065F', '\u0670'
    ]
    
    for diacritic in diacritics:
        text = text.replace(diacritic, '')
    
    return ' '.join(text.split())  # Normalize spaces

def calculate_similarity(reference, transcribed, threshold=0.6):
    """Calculate similarity between reference and transcribed text"""
    ref_clean = clean_arabic_text(reference)
    trans_clean = clean_arabic_text(transcribed)
    
    distance = Levenshtein.distance(ref_clean, trans_clean)
    max_len = max(len(ref_clean), len(trans_clean))
    
    if max_len == 0:
        similarity = 1.0
    else:
        similarity = 1.0 - (distance / max_len)
    
    return {
        'similarity': similarity,
        'is_correct': similarity >= threshold,
        'reference_clean': ref_clean,
        'transcribed_clean': trans_clean
    }
```

**Investigate:**
- Why do we need to remove diacritics?
- How does Levenshtein distance work with Arabic text?
- What similarity threshold works best for Quranic recitation?

**Challenge:** Implement word-level comparison and feedback

### Step 6: FastAPI Web Application (90 minutes)
**Goal:** Create a complete web API with all endpoints

**Instructions:**
1. Create `main.py` as your FastAPI application
2. Implement the following endpoints:
   - `GET /`: Homepage with documentation
   - `GET /verses/{surah}/{ayah}`: Get specific verse
   - `GET /pages/{page_num}`: Get page content
   - `POST /transcribe`: Upload audio and get transcription
   - `POST /practice`: Compare recitation with reference

**Key Implementation Structure:**
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import tempfile
import os

app = FastAPI(title="Quran Recitation Practice API")

@app.get("/")
async def read_root():
    return {"message": "Quran Recitation Practice API"}

@app.get("/verses/{surah}/{ayah}")
async def get_verse(surah: int, ayah: int):
    # Implementation here
    pass

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    # Save uploaded file temporarily
    # Process with ASR
    # Return transcription
    pass

@app.post("/practice")
async def practice_recitation(
    surah: int,
    ayah: int,
    audio: UploadFile = File(...)
):
    # Get reference verse from database
    # Transcribe uploaded audio
    # Compare and return feedback
    pass
```

**Investigate:**
- How do you handle file uploads in FastAPI?
- What's the best way to manage temporary files?
- How do you structure error responses?

**Challenge:** Add real-time WebSocket support for live transcription

### Step 7: Frontend Interface (60 minutes)
**Goal:** Create a basic web interface for testing

**Instructions:**
1. Create a `static` folder for HTML/CSS/JS files
2. Build a simple interface with:
   - Verse selection (surah/ayah dropdowns)
   - Record button for audio capture
   - Display area for results
   - Feedback visualization

**Basic HTML Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Quran Recitation Practice</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; direction: rtl; }
        .arabic { font-size: 24px; line-height: 1.8; }
        .correct { background-color: #d4edda; }
        .incorrect { background-color: #f8d7da; }
    </style>
</head>
<body>
    <h1>تدريب على تلاوة القرآن</h1>
    
    <div>
        <select id="surah-select">
            <!-- Populate with surahs -->
        </select>
        <select id="ayah-select">
            <!-- Populate with ayahs -->
        </select>
    </div>
    
    <div id="verse-display" class="arabic"></div>
    
    <div>
        <button id="record-btn">Start Recording</button>
        <button id="stop-btn">Stop Recording</button>
    </div>
    
    <div id="results"></div>
    
    <script>
        // JavaScript for audio recording and API calls
    </script>
</body>
</html>
```

**Investigate:**
- How do you capture audio in the browser?
- What's the best way to display Arabic text?
- How do you handle real-time feedback?

### Step 8: Advanced Features and Optimization (90 minutes)
**Goal:** Add advanced features and optimize performance

**Advanced Features to Implement:**
1. **Real-time streaming recognition** (if time permits)
2. **Word-by-word feedback**
3. **Progress tracking**
4. **Multiple recitation modes**
5. **Audio playback of reference recitations**

**Performance Optimizations:**
1. **Model caching**
2. **Async processing**
3. **Database connection pooling**
4. **Audio compression**

**Investigate:**
- How can you implement streaming audio processing?
- What caching strategies work best for ML models?
- How do you handle concurrent users?

**Challenge:** Implement a "continuous mode" where the app automatically advances to the next verse after correct recitation

## Technical Deep Dives

### Arabic Text Processing
- **Unicode considerations**: Arabic text uses complex Unicode ranges
- **Diacritics handling**: Understanding when and why to remove تشكيل
- **Text normalization**: Handling different forms of the same letter
- **Right-to-left (RTL) display**: Proper web rendering of Arabic

### Speech Recognition for Arabic
- **Model selection**: Comparing general vs. Quran-specific models
- **Audio preprocessing**: Sample rates, noise reduction, normalization
- **Postprocessing**: Error correction, confidence scoring
- **Real-time constraints**: Balancing accuracy vs. speed

### Similarity Algorithms
- **Levenshtein distance**: Character-level comparison
- **Word-level matching**: Handling insertions/deletions
- **Phonetic similarity**: Considering pronunciation variations
- **Contextual matching**: Understanding partial recitations

## Deployment and Production Considerations

### Scalability
- **Model serving**: Efficient model loading and inference
- **Database optimization**: Indexing and query optimization
- **Caching strategies**: Redis for frequently accessed data
- **Load balancing**: Handling multiple concurrent users

### Security
- **Input validation**: Sanitizing audio uploads
- **Rate limiting**: Preventing abuse
- **Authentication**: User management (if needed)
- **Data privacy**: Handling user recordings

### Monitoring
- **Performance metrics**: Response times, accuracy rates
- **Error tracking**: ASR failures, database errors
- **Usage analytics**: Popular verses, user patterns
- **Health checks**: System status monitoring

## Troubleshooting Guide

### Common Issues
1. **Model loading errors**
   - Check internet connection for downloading
   - Verify sufficient disk space
   - Try fallback models

2. **Audio capture problems**
   - Microphone permissions in browser
   - Audio format compatibility
   - Sample rate mismatches

3. **Arabic text display issues**
   - Font support for Arabic
   - UTF-8 encoding
   - RTL text alignment

4. **Performance problems**
   - Model inference time
   - Database query optimization
   - Memory usage with large audio files

### Debugging Tips
- Use print statements to trace execution
- Log model predictions and confidence scores
- Test with known audio samples
- Validate database queries separately

## Next Steps and Extensions

### Additional Features
- **Multi-user support** with user accounts
- **Progress tracking** and statistics
- **Gamification** with scores and achievements
- **Social features** for sharing progress
- **Mobile app** development
- **Offline mode** with local models

### Advanced ML Features
- **Custom model fine-tuning** on specific recitation styles
- **Real-time error detection** and correction suggestions
- **Pronunciation assessment** beyond just text matching
- **Accent adaptation** for different Arabic dialects

### Integration Opportunities
- **Existing Quran apps** and platforms
- **Educational institutions** for learning programs
- **Accessibility features** for visually impaired users
- **Multi-language support** for non-Arabic speakers

## Resources and References

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers/)
- [Whisper Model Documentation](https://huggingface.co/openai/whisper-base)

### Arabic NLP Resources
- [Arabic Text Processing Libraries](https://github.com/aub-mind/arabert)
- [Quranic Arabic Datasets](https://github.com/Tarteel-io/tarteel-ml)

### Audio Processing
- [SoundDevice Documentation](https://python-sounddevice.readthedocs.io/)
- [Audio Processing Best Practices](https://pytorch.org/audio/stable/tutorials/)

---

**Remember:** This workshop is designed to be interactive. At each step, experiment with the code, ask questions, and try to understand not just how things work, but why they work that way. Use Cursor AI to help you explore, debug, and improve your implementation! 