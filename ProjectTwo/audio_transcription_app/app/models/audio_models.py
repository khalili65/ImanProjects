from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    NEEDS_REVIEW = "needs_review"


class AudioFileModel(BaseModel):
    """Model for uploaded audio files"""
    id: str
    filename: str
    original_filename: str
    file_size: int
    duration_seconds: float
    format: str
    sample_rate: int
    channels: int
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    total_chunks: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AudioChunk(BaseModel):
    """Model for audio chunks created from the original file"""
    id: str
    file_id: str
    chunk_index: int
    start_time: float  # seconds
    end_time: float    # seconds
    duration: float    # seconds
    chunk_filename: str
    transcription_status: TranscriptionStatus = TranscriptionStatus.NOT_STARTED
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TranscriptionResult(BaseModel):
    """Model for transcription results from ElevenLabs API"""
    chunk_id: str
    raw_transcription: str
    confidence_score: Optional[float] = None
    language: Optional[str] = None
    processing_time: float  # seconds
    api_response_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationEdit(BaseModel):
    """Model for user validation and edits"""
    chunk_id: str
    original_text: str
    edited_text: str
    user_confidence: int = Field(ge=1, le=5, description="User confidence rating (1-5)")
    notes: Optional[str] = None
    is_validated: bool = True
    editor_id: Optional[str] = None  # For future user management
    edited_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChunkWithTranscription(BaseModel):
    """Combined model for frontend display"""
    chunk: AudioChunk
    transcription: Optional[TranscriptionResult] = None
    validation: Optional[ValidationEdit] = None
    audio_url: str  # URL to access the audio chunk


class ProjectSummary(BaseModel):
    """Summary of entire transcription project"""
    file_info: AudioFileModel
    total_chunks: int
    completed_transcriptions: int
    validated_chunks: int
    total_duration: float
    estimated_accuracy: Optional[float] = None
    chunks: List[ChunkWithTranscription]


class UploadResponse(BaseModel):
    """Response model for file upload"""
    file_id: str
    message: str
    file_info: AudioFileModel


class ProcessingProgress(BaseModel):
    """Model for tracking processing progress"""
    file_id: str
    current_step: str
    progress_percentage: float
    chunks_processed: int
    total_chunks: int
    estimated_time_remaining: Optional[float] = None  # seconds
    
    
class ExportRequest(BaseModel):
    """Request model for exporting final transcription"""
    file_id: str
    format: str = Field(default="txt", pattern="^(txt|json|srt|vtt)$")
    include_timestamps: bool = True
    include_metadata: bool = False


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 