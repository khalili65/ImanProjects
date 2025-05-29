from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

from .models.audio_models import (
    AudioFileModel, 
    AudioChunk, 
    TranscriptionResult, 
    ValidationEdit,
    UploadResponse,
    ProcessingProgress,
    ProjectSummary,
    ChunkWithTranscription,
    ErrorResponse
)
from .services.audio_processor import AudioProcessor
from .services.transcription_service import ElevenLabsTranscriptionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Audio Transcription & Editing App",
    description="Educational project demonstrating AI integration, modular design, and virtual environments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (demonstrates dependency injection)
audio_processor = AudioProcessor()
transcription_service = ElevenLabsTranscriptionService()

# In-memory storage for demo (in production, use a database)
# This demonstrates the need for proper data persistence
file_storage: Dict[str, AudioFileModel] = {}
chunks_storage: Dict[str, List[AudioChunk]] = {}
transcriptions_storage: Dict[str, TranscriptionResult] = {}
validations_storage: Dict[str, ValidationEdit] = {}

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serve the main web interface.
    
    Educational note: This demonstrates how to serve HTML interfaces
    alongside API endpoints in FastAPI.
    """
    with open("app/static/index.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.post("/api/upload", response_model=UploadResponse)
async def upload_audio_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload and process an audio file.
    
    This endpoint demonstrates:
    - File upload handling
    - Background task processing
    - Input validation
    - Error handling
    """
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Check file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if hasattr(file, 'size') and file.size > max_size:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Process audio file
            audio_info, chunks = await audio_processor.process_audio_file(temp_path, file.filename)
            
            # Store in memory (in production, use a database)
            file_storage[audio_info.id] = audio_info
            chunks_storage[audio_info.id] = chunks
            
            # Start background transcription
            background_tasks.add_task(transcribe_file_chunks, audio_info.id, chunks)
            
            logger.info(f"Successfully uploaded and processed {file.filename}")
            
            return UploadResponse(
                file_id=audio_info.id,
                message=f"File uploaded successfully. Processing {len(chunks)} chunks.",
                file_info=audio_info
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def transcribe_file_chunks(file_id: str, chunks: List[AudioChunk]):
    """
    Background task to transcribe all chunks for a file.
    
    Educational note: This shows how to handle long-running operations
    without blocking the main API thread.
    """
    try:
        logger.info(f"Starting background transcription for file {file_id}")
        
        # Get audio files directory
        audio_files_dir = Path("./audio_files")
        
        # Transcribe all chunks
        results = await transcription_service.transcribe_multiple_chunks(
            chunks, 
            audio_files_dir,
            max_concurrent=3
        )
        
        # Store transcription results
        for result in results:
            transcriptions_storage[result.chunk_id] = result
        
        logger.info(f"Completed background transcription for file {file_id}")
        
    except Exception as e:
        logger.error(f"Error in background transcription: {str(e)}")


@app.get("/api/files/{file_id}/status", response_model=ProcessingProgress)
async def get_processing_status(file_id: str):
    """
    Get processing status for a file.
    
    This demonstrates progress tracking for long-running operations.
    """
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = file_storage[file_id]
    chunks = chunks_storage.get(file_id, [])
    
    # Count completed transcriptions
    completed_transcriptions = sum(
        1 for chunk in chunks 
        if chunk.id in transcriptions_storage
    )
    
    progress_percentage = (completed_transcriptions / len(chunks)) * 100 if chunks else 0
    
    # Determine current step
    if progress_percentage == 0:
        current_step = "Starting transcription..."
    elif progress_percentage < 100:
        current_step = f"Transcribing chunks... ({completed_transcriptions}/{len(chunks)})"
    else:
        current_step = "Transcription complete"
    
    return ProcessingProgress(
        file_id=file_id,
        current_step=current_step,
        progress_percentage=progress_percentage,
        chunks_processed=completed_transcriptions,
        total_chunks=len(chunks)
    )


@app.get("/api/files/{file_id}/summary", response_model=ProjectSummary)
async def get_project_summary(file_id: str):
    """
    Get complete project summary with all chunks and transcriptions.
    
    This endpoint provides the main data for the web interface.
    """
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = file_storage[file_id]
    chunks = chunks_storage.get(file_id, [])
    
    # Build chunks with transcriptions
    chunks_with_transcriptions = []
    completed_transcriptions = 0
    validated_chunks = 0
    
    for chunk in chunks:
        transcription = transcriptions_storage.get(chunk.id)
        validation = validations_storage.get(chunk.id)
        
        if transcription:
            completed_transcriptions += 1
        if validation:
            validated_chunks += 1
        
        # Create audio URL for chunk
        audio_url = f"/api/chunks/{chunk.id}/audio"
        
        chunk_data = ChunkWithTranscription(
            chunk=chunk,
            transcription=transcription,
            validation=validation,
            audio_url=audio_url
        )
        chunks_with_transcriptions.append(chunk_data)
    
    return ProjectSummary(
        file_info=file_info,
        total_chunks=len(chunks),
        completed_transcriptions=completed_transcriptions,
        validated_chunks=validated_chunks,
        total_duration=file_info.duration_seconds,
        chunks=chunks_with_transcriptions
    )


@app.get("/api/chunks/{chunk_id}/audio")
async def get_chunk_audio(chunk_id: str):
    """
    Serve audio chunk file.
    
    Educational note: This shows how to serve binary files through FastAPI.
    """
    # Find the chunk
    chunk = None
    for chunks_list in chunks_storage.values():
        for c in chunks_list:
            if c.id == chunk_id:
                chunk = c
                break
        if chunk:
            break
    
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Get file path
    chunk_path = audio_processor.get_chunk_file_path(chunk.chunk_filename)
    
    if not chunk_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=chunk_path,
        media_type="audio/wav",
        filename=chunk.chunk_filename
    )


@app.put("/api/chunks/{chunk_id}/validate")
async def validate_transcription(chunk_id: str, validation: ValidationEdit):
    """
    Save user validation/edit for a transcription.
    
    This demonstrates the interactive feedback loop that makes
    the application useful for real-world scenarios.
    """
    # Verify chunk exists
    chunk_exists = False
    for chunks_list in chunks_storage.values():
        if any(c.id == chunk_id for c in chunks_list):
            chunk_exists = True
            break
    
    if not chunk_exists:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Ensure validation is for correct chunk
    validation.chunk_id = chunk_id
    
    # Store validation
    validations_storage[chunk_id] = validation
    
    logger.info(f"Validation saved for chunk {chunk_id}")
    
    return {"message": "Validation saved successfully"}


@app.get("/api/files/{file_id}/export")
async def export_transcription(
    file_id: str,
    format: str = "txt",
    include_timestamps: bool = True
):
    """
    Export final transcription in various formats.
    
    Educational note: This shows how to provide multiple output formats
    to meet different user needs.
    """
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = file_storage[file_id]
    chunks = chunks_storage.get(file_id, [])
    
    # Collect all text (prefer validated over original)
    text_segments = []
    
    for chunk in sorted(chunks, key=lambda x: x.chunk_index):
        validation = validations_storage.get(chunk.id)
        transcription = transcriptions_storage.get(chunk.id)
        
        if validation:
            text = validation.edited_text
        elif transcription:
            text = transcription.raw_transcription
        else:
            text = "[No transcription available]"
        
        if include_timestamps:
            text_segments.append(f"[{chunk.start_time:.1f}s - {chunk.end_time:.1f}s] {text}")
        else:
            text_segments.append(text)
    
    # Format output
    if format == "txt":
        content = "\n".join(text_segments)
        media_type = "text/plain"
        filename = f"{file_info.original_filename}_transcription.txt"
    elif format == "json":
        export_data = {
            "file_info": file_info.dict(),
            "transcription": text_segments,
            "exported_at": datetime.now().isoformat()
        }
        content = json.dumps(export_data, indent=2)
        media_type = "application/json"
        filename = f"{file_info.original_filename}_transcription.json"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    # Create temporary file for download
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f".{format}") as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name
    
    return FileResponse(
        path=temp_path,
        media_type=media_type,
        filename=filename
    )


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Educational note: Always include health checks for production deployments.
    """
    api_status = await transcription_service.get_api_status()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "audio_processor": "active",
            "transcription_service": api_status
        },
        "storage": {
            "files_in_memory": len(file_storage),
            "chunks_in_memory": sum(len(chunks) for chunks in chunks_storage.values())
        }
    }


@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file and clean up associated data.
    
    Educational note: Proper cleanup is important for resource management.
    """
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Clean up storage
    chunks = chunks_storage.get(file_id, [])
    
    # Remove transcriptions and validations
    for chunk in chunks:
        transcriptions_storage.pop(chunk.id, None)
        validations_storage.pop(chunk.id, None)
    
    # Remove chunks and file info
    chunks_storage.pop(file_id, None)
    file_storage.pop(file_id, None)
    
    # Clean up files
    audio_processor.cleanup_temp_files(file_id)
    
    logger.info(f"Deleted file {file_id} and associated data")
    
    return {"message": "File deleted successfully"}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom error handler for better error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors gracefully."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        ).dict()
    )


# Educational endpoint to explain the application architecture
@app.get("/api/architecture")
async def explain_architecture():
    """
    Educational endpoint explaining the application architecture.
    
    This helps students understand why the code is structured this way.
    """
    return {
        "architecture_overview": {
            "modular_design": {
                "models": "Data structures and validation using Pydantic",
                "services": "Business logic separated from API logic",
                "api": "Clean REST endpoints with proper HTTP methods",
                "static": "Frontend assets and templates"
            },
            "why_virtual_environments": [
                "Isolate project dependencies",
                "Prevent version conflicts",
                "Enable reproducible deployments",
                "Make collaboration easier"
            ],
            "ai_integration_patterns": [
                "External API integration with proper error handling",
                "Asynchronous processing for performance",
                "Mock services for development",
                "Rate limiting and retry logic"
            ],
            "production_considerations": [
                "Database instead of in-memory storage",
                "User authentication and authorization",
                "File storage (S3, local filesystem)",
                "Monitoring and logging",
                "Load balancing and scaling"
            ]
        },
        "learning_objectives": [
            "Understand separation of concerns",
            "Learn API integration best practices",
            "Experience async/await patterns",
            "Practice error handling",
            "Build interactive user interfaces"
        ]
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # For development
        log_level="info"
    ) 