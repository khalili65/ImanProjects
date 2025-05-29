import os
import uuid
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence
from typing import List, Tuple, Optional
import logging
from pathlib import Path

from ..models.audio_models import AudioFileModel, AudioChunk, ProcessingStatus

# Try to import optional audio processing libraries
try:
    import librosa
    import soundfile as sf
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    print("⚠️  Advanced audio processing libraries not available.")
    print("   For full functionality, install: pip install librosa soundfile")
    print("   The app will work with basic audio processing using pydub.")

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Service for processing audio files into intelligent chunks.
    
    This service demonstrates why modular design matters:
    - Separation of concerns (audio processing vs API logic)
    - Reusable across different endpoints
    - Testable in isolation
    - Configurable parameters
    - Graceful handling of optional dependencies
    """
    
    def __init__(self, 
                 chunk_duration: int = 30,  # seconds
                 min_silence_len: int = 500,  # milliseconds
                 silence_thresh: int = -40,  # dB
                 output_dir: str = "./audio_files"):
        self.chunk_duration = chunk_duration * 1000  # Convert to milliseconds
        self.min_silence_len = min_silence_len
        self.silence_thresh = silence_thresh
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "chunks").mkdir(exist_ok=True)
        (self.output_dir / "temp").mkdir(exist_ok=True)
        
        # Log available features
        if HAS_LIBROSA:
            logger.info("Advanced audio processing available (librosa)")
        else:
            logger.info("Basic audio processing mode (pydub only)")
    
    async def process_audio_file(self, file_path: str, filename: str) -> Tuple[AudioFileModel, List[AudioChunk]]:
        """
        Main method to process an audio file into chunks.
        
        This demonstrates:
        - Error handling in production code
        - Progress tracking
        - Clean return types
        - Graceful degradation when libraries are missing
        """
        try:
            logger.info(f"Starting audio processing for {filename}")
            
            # Load and analyze audio file
            audio_info = await self._analyze_audio_file(file_path, filename)
            
            # Create chunks
            chunks = await self._create_intelligent_chunks(file_path, audio_info.id)
            
            # Update audio info with chunk count
            audio_info.total_chunks = len(chunks)
            audio_info.processing_status = ProcessingStatus.COMPLETED
            
            logger.info(f"Successfully processed {filename} into {len(chunks)} chunks")
            return audio_info, chunks
            
        except Exception as e:
            logger.error(f"Error processing audio file {filename}: {str(e)}")
            raise
    
    async def _analyze_audio_file(self, file_path: str, filename: str) -> AudioFileModel:
        """
        Analyze audio file properties.
        
        Educational note: This shows how to handle optional dependencies gracefully.
        """
        try:
            # Load with pydub (always available)
            audio = AudioSegment.from_file(file_path)
            
            file_id = str(uuid.uuid4())
            processed_filename = f"{file_id}_{filename}"
            
            # Move file to processed location
            processed_path = self.output_dir / processed_filename
            audio.export(processed_path, format="wav")
            
            # Use librosa for detailed analysis if available, otherwise use pydub
            if HAS_LIBROSA:
                try:
                    y, sr = librosa.load(file_path, sr=None)
                    duration = librosa.duration(y=y, sr=sr)
                    sample_rate = sr
                except Exception as e:
                    logger.warning(f"Librosa analysis failed, using pydub: {e}")
                    duration = len(audio) / 1000.0  # Convert ms to seconds
                    sample_rate = audio.frame_rate
            else:
                # Fallback to pydub analysis
                duration = len(audio) / 1000.0  # Convert ms to seconds
                sample_rate = audio.frame_rate
            
            return AudioFileModel(
                id=file_id,
                filename=processed_filename,
                original_filename=filename,
                file_size=os.path.getsize(file_path),
                duration_seconds=duration,
                format='wav',  # We always export as WAV
                sample_rate=sample_rate,
                channels=audio.channels,
                processing_status=ProcessingStatus.PROCESSING
            )
            
        except Exception as e:
            logger.error(f"Error analyzing audio file: {str(e)}")
            raise
    
    async def _create_intelligent_chunks(self, file_path: str, file_id: str) -> List[AudioChunk]:
        """
        Create intelligent audio chunks that respect word boundaries.
        
        This is the core algorithm that demonstrates:
        - Why smart chunking matters for transcription quality
        - How to balance technical constraints with user experience
        - Audio processing best practices
        - Graceful handling of missing dependencies
        """
        audio = AudioSegment.from_file(file_path)
        chunks = []
        
        # Method 1: Try silence-based splitting first
        silence_chunks = self._split_on_silence(audio)
        
        if len(silence_chunks) > 1:
            # Combine small chunks to reach target duration
            chunks = self._combine_chunks_to_target_duration(silence_chunks, file_id)
        else:
            # Method 2: Fall back to time-based chunking with overlap
            chunks = self._create_time_based_chunks(audio, file_id)
        
        return chunks
    
    def _split_on_silence(self, audio: AudioSegment) -> List[AudioSegment]:
        """
        Split audio on silence to find natural break points.
        
        Educational note: This shows how AI preprocessing
        can improve final AI results (transcription quality).
        """
        try:
            # Detect silence periods
            silence_ranges = detect_silence(
                audio,
                min_silence_len=self.min_silence_len,
                silence_thresh=self.silence_thresh
            )
            
            if not silence_ranges:
                return [audio]
            
            # Split on silence
            chunks = split_on_silence(
                audio,
                min_silence_len=self.min_silence_len,
                silence_thresh=self.silence_thresh,
                keep_silence=100  # Keep 100ms of silence for natural flow
            )
            
            # Filter out very short chunks (less than 5 seconds)
            min_chunk_duration = 5000  # 5 seconds in milliseconds
            filtered_chunks = [chunk for chunk in chunks if len(chunk) >= min_chunk_duration]
            
            return filtered_chunks if filtered_chunks else [audio]
            
        except Exception as e:
            logger.warning(f"Silence-based splitting failed: {str(e)}")
            return [audio]
    
    def _combine_chunks_to_target_duration(self, 
                                         silence_chunks: List[AudioSegment], 
                                         file_id: str) -> List[AudioChunk]:
        """
        Combine silence-based chunks to reach target duration.
        
        This demonstrates optimization algorithms in AI applications.
        """
        combined_chunks = []
        current_chunk = AudioSegment.empty()
        chunk_start_time = 0
        chunk_index = 0
        
        for i, segment in enumerate(silence_chunks):
            # Check if adding this segment would exceed target duration
            if len(current_chunk) > 0 and len(current_chunk) + len(segment) > self.chunk_duration:
                # Save current chunk
                audio_chunk = self._save_chunk(
                    current_chunk, 
                    file_id, 
                    chunk_index, 
                    chunk_start_time / 1000,  # Convert to seconds
                    (chunk_start_time + len(current_chunk)) / 1000
                )
                combined_chunks.append(audio_chunk)
                
                # Start new chunk
                current_chunk = segment
                chunk_start_time = chunk_start_time + len(current_chunk) if chunk_index > 0 else 0
                chunk_index += 1
            else:
                # Add segment to current chunk
                if len(current_chunk) == 0:
                    chunk_start_time = sum(len(chunk) for chunk in silence_chunks[:i])
                current_chunk += segment
        
        # Don't forget the last chunk
        if len(current_chunk) > 0:
            audio_chunk = self._save_chunk(
                current_chunk, 
                file_id, 
                chunk_index,
                chunk_start_time / 1000,
                (chunk_start_time + len(current_chunk)) / 1000
            )
            combined_chunks.append(audio_chunk)
        
        return combined_chunks
    
    def _create_time_based_chunks(self, audio: AudioSegment, file_id: str) -> List[AudioChunk]:
        """
        Create time-based chunks as fallback method.
        
        Educational note: Always have fallback strategies in production systems.
        """
        chunks = []
        total_duration = len(audio)
        chunk_index = 0
        
        for start_ms in range(0, total_duration, self.chunk_duration):
            end_ms = min(start_ms + self.chunk_duration, total_duration)
            chunk_audio = audio[start_ms:end_ms]
            
            audio_chunk = self._save_chunk(
                chunk_audio,
                file_id,
                chunk_index,
                start_ms / 1000,  # Convert to seconds
                end_ms / 1000
            )
            chunks.append(audio_chunk)
            chunk_index += 1
        
        return chunks
    
    def _save_chunk(self, 
                   chunk_audio: AudioSegment, 
                   file_id: str, 
                   chunk_index: int,
                   start_time: float,
                   end_time: float) -> AudioChunk:
        """
        Save audio chunk to file and create metadata.
        
        This shows proper file management in production applications.
        """
        chunk_id = str(uuid.uuid4())
        chunk_filename = f"chunk_{file_id}_{chunk_index:03d}_{chunk_id}.wav"
        chunk_path = self.output_dir / "chunks" / chunk_filename
        
        # Export chunk as WAV for consistency
        chunk_audio.export(chunk_path, format="wav")
        
        return AudioChunk(
            id=chunk_id,
            file_id=file_id,
            chunk_index=chunk_index,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            chunk_filename=chunk_filename
        )
    
    def get_chunk_file_path(self, chunk_filename: str) -> Path:
        """Get the full path to a chunk file."""
        return self.output_dir / "chunks" / chunk_filename
    
    def cleanup_temp_files(self, file_id: str):
        """Clean up temporary files for a specific file ID."""
        try:
            # Remove chunks
            chunk_pattern = f"chunk_{file_id}_*"
            for chunk_file in (self.output_dir / "chunks").glob(chunk_pattern):
                chunk_file.unlink()
            
            # Remove original processed file
            for file in self.output_dir.glob(f"{file_id}_*"):
                file.unlink()
                
            logger.info(f"Cleaned up files for {file_id}")
        except Exception as e:
            logger.error(f"Error cleaning up files for {file_id}: {str(e)}")


# Example usage and testing functions for educational purposes
async def demonstrate_chunking_strategies():
    """
    Educational function to show different chunking approaches.
    
    This helps students understand the trade-offs between different methods.
    """
    processor = AudioProcessor()
    
    print("Audio Chunking Strategies Demo")
    print("=" * 40)
    print("1. Silence-based chunking: Best for speech with natural pauses")
    print("2. Time-based chunking: Fallback for continuous audio")
    print("3. Hybrid approach: Combines both for optimal results")
    print("\nKey considerations:")
    print("- Word boundary preservation")
    print("- Transcription accuracy")
    print("- Processing efficiency")
    print("- User experience")
    print("\nAvailable features:")
    if HAS_LIBROSA:
        print("✅ Advanced audio analysis (librosa)")
    else:
        print("⚠️  Basic audio processing only (install librosa for advanced features)")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_chunking_strategies()) 