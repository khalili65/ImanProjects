import asyncio
import aiohttp
import time
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import os
from dotenv import load_dotenv

from ..models.audio_models import (
    AudioChunk, 
    TranscriptionResult, 
    TranscriptionStatus,
    ErrorResponse
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ElevenLabsTranscriptionService:
    """
    Service for integrating with ElevenLabs API for audio transcription.
    
    This demonstrates:
    - Professional API integration patterns
    - Rate limiting and error handling
    - Asynchronous processing
    - Configuration management
    """
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = os.getenv("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io/v1")
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.timeout = 30  # seconds
        
        if not self.api_key:
            logger.warning("ElevenLabs API key not found. Using mock service for demo.")
            self._use_mock = True
        else:
            self._use_mock = False
    
    async def transcribe_chunk(self, chunk: AudioChunk, audio_file_path: Path) -> TranscriptionResult:
        """
        Transcribe a single audio chunk.
        
        Educational note: This shows how to handle external API calls
        with proper error handling and retries.
        """
        start_time = time.time()
        
        try:
            if self._use_mock:
                # Use mock service for demonstration
                transcription_text = await self._mock_transcription(chunk, audio_file_path)
            else:
                # Use real ElevenLabs API
                transcription_text = await self._call_elevenlabs_api(audio_file_path)
            
            processing_time = time.time() - start_time
            
            return TranscriptionResult(
                chunk_id=chunk.id,
                raw_transcription=transcription_text,
                confidence_score=0.95,  # Mock confidence score
                language="en",  # Detected language
                processing_time=processing_time,
                api_response_metadata={
                    "service": "elevenlabs" if not self._use_mock else "mock",
                    "chunk_duration": chunk.duration,
                    "chunk_index": chunk.chunk_index
                }
            )
            
        except Exception as e:
            logger.error(f"Error transcribing chunk {chunk.id}: {str(e)}")
            raise
    
    async def transcribe_multiple_chunks(self, 
                                       chunks: List[AudioChunk], 
                                       audio_files_dir: Path,
                                       max_concurrent: int = 3) -> List[TranscriptionResult]:
        """
        Transcribe multiple chunks with concurrency control.
        
        This demonstrates:
        - Concurrent processing for efficiency
        - Rate limiting to respect API limits
        - Progress tracking
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []
        
        async def transcribe_with_semaphore(chunk: AudioChunk) -> TranscriptionResult:
            async with semaphore:
                chunk_path = audio_files_dir / "chunks" / chunk.chunk_filename
                return await self.transcribe_chunk(chunk, chunk_path)
        
        # Create tasks for all chunks
        tasks = [transcribe_with_semaphore(chunk) for chunk in chunks]
        
        # Execute with progress tracking
        completed = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            completed += 1
            
            progress = (completed / len(chunks)) * 100
            logger.info(f"Transcription progress: {progress:.1f}% ({completed}/{len(chunks)})")
        
        # Sort results by chunk index to maintain order
        results.sort(key=lambda r: next(
            chunk.chunk_index for chunk in chunks if chunk.id == r.chunk_id
        ))
        
        return results
    
    async def _call_elevenlabs_api(self, audio_file_path: Path) -> str:
        """
        Make actual API call to ElevenLabs.
        
        Educational note: This shows proper HTTP client usage
        with async/await and error handling.
        """
        headers = {
            "xi-api-key": self.api_key,
        }
        
        # Prepare multipart form data
        data = aiohttp.FormData()
        
        # Read audio file
        with open(audio_file_path, 'rb') as f:
            data.add_field('audio', f, filename=audio_file_path.name, content_type='audio/wav')
        
        # Add other parameters
        data.add_field('model', 'eleven_multilingual_v2')
        data.add_field('response_format', 'json')
        
        url = f"{self.base_url}/speech-to-text"
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(url, headers=headers, data=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result.get('text', '')
                        elif response.status == 429:  # Rate limited
                            if attempt < self.max_retries - 1:
                                wait_time = self.retry_delay * (2 ** attempt)
                                logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                raise Exception("Rate limited after max retries")
                        else:
                            error_text = await response.text()
                            raise Exception(f"API error {response.status}: {error_text}")
                            
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Timeout on attempt {attempt + 1}. Retrying...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception("Request timed out after max retries")
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Error on attempt {attempt + 1}: {str(e)}. Retrying...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    raise
        
        raise Exception("Max retries exceeded")
    
    async def _mock_transcription(self, chunk: AudioChunk, audio_file_path: Path) -> str:
        """
        Mock transcription service for demonstration purposes.
        
        Educational note: This shows how to create mock services
        for development and testing when external APIs aren't available.
        """
        # Simulate API processing time
        await asyncio.sleep(0.5 + (chunk.duration * 0.1))  # Simulate realistic processing time
        
        # Generate mock transcription based on chunk properties
        mock_transcriptions = [
            f"This is the transcription for audio chunk {chunk.chunk_index + 1}. ",
            f"The audio segment from {chunk.start_time:.1f} to {chunk.end_time:.1f} seconds contains speech. ",
            f"This chunk has a duration of {chunk.duration:.1f} seconds and represents part of the original audio. ",
            "In a real application, this would be the actual transcribed text from the ElevenLabs API. ",
            "The transcription quality would depend on audio clarity, language, and background noise. ",
            "Users can edit this text to correct any transcription errors. ",
            "This interactive editing feature is crucial for high-quality results. ",
            "The application demonstrates proper error handling and user feedback loops. "
        ]
        
        # Select mock text based on chunk index
        selected_text = mock_transcriptions[chunk.chunk_index % len(mock_transcriptions)]
        
        # Add some variation based on chunk properties
        if chunk.duration < 10:
            selected_text += "This is a shorter audio segment. "
        elif chunk.duration > 25:
            selected_text += "This is a longer audio segment with more content. "
        
        return selected_text
    
    async def get_api_status(self) -> Dict[str, Any]:
        """
        Check ElevenLabs API status and quota.
        
        Educational note: Monitoring API usage is crucial for production applications.
        """
        if self._use_mock:
            return {
                "status": "mock_service",
                "available": True,
                "quota_remaining": "unlimited",
                "rate_limit": "none"
            }
        
        try:
            headers = {"xi-api-key": self.api_key}
            url = f"{self.base_url}/user"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        return {
                            "status": "active",
                            "available": True,
                            "quota_remaining": user_data.get("character_count", "unknown"),
                            "rate_limit": "standard"
                        }
                    else:
                        return {
                            "status": "error",
                            "available": False,
                            "error": f"API returned status {response.status}"
                        }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }
    
    def estimate_processing_time(self, total_duration: float) -> float:
        """
        Estimate total processing time based on audio duration.
        
        Educational note: Providing time estimates improves user experience.
        """
        # Rough estimate: processing takes about 10-20% of audio duration
        base_time = total_duration * 0.15  # 15% of audio duration
        
        # Add overhead for API calls
        api_overhead = 2.0  # seconds per chunk on average
        
        return base_time + api_overhead
    
    async def validate_audio_format(self, file_path: Path) -> bool:
        """
        Validate that audio format is supported by ElevenLabs.
        
        Educational note: Input validation prevents errors and improves UX.
        """
        supported_formats = ['.wav', '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.webm']
        
        file_extension = file_path.suffix.lower()
        return file_extension in supported_formats


# Utility functions for educational purposes
def demonstrate_api_integration_concepts():
    """
    Educational function explaining API integration best practices.
    """
    concepts = {
        "Authentication": "Secure API key management with environment variables",
        "Rate Limiting": "Respect API limits to avoid service interruption",
        "Error Handling": "Graceful handling of network and API errors",
        "Retries": "Automatic retry logic for transient failures",
        "Timeout Handling": "Prevent hanging requests with appropriate timeouts",
        "Concurrent Processing": "Process multiple requests efficiently",
        "Progress Tracking": "Keep users informed of long-running operations",
        "Input Validation": "Validate data before sending to external APIs",
        "Mock Services": "Enable development without external dependencies"
    }
    
    print("API Integration Best Practices")
    print("=" * 40)
    for concept, description in concepts.items():
        print(f"{concept}: {description}")


async def demo_transcription_workflow():
    """
    Demonstrate the complete transcription workflow.
    """
    service = ElevenLabsTranscriptionService()
    
    print("\nTranscription Service Demo")
    print("=" * 30)
    
    # Check API status
    status = await service.get_api_status()
    print(f"API Status: {status}")
    
    # Show processing time estimation
    estimated_time = service.estimate_processing_time(120)  # 2 minutes of audio
    print(f"Estimated processing time for 2 minutes of audio: {estimated_time:.1f} seconds")


if __name__ == "__main__":
    demonstrate_api_integration_concepts()
    asyncio.run(demo_transcription_workflow()) 