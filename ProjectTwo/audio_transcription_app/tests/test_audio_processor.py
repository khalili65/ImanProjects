"""
Test file for Audio Processor Service

This demonstrates:
- Unit testing for audio processing components
- Async testing patterns
- Mock usage for external dependencies
- Test data management

Educational note: Testing is crucial for production applications.
This shows students how to write effective tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import asyncio

# Import the modules we're testing
from app.services.audio_processor import AudioProcessor
from app.models.audio_models import AudioFileModel, AudioChunk, ProcessingStatus


class TestAudioProcessor:
    """Test class for AudioProcessor service"""
    
    @pytest.fixture
    def audio_processor(self):
        """Create an AudioProcessor instance for testing"""
        return AudioProcessor(
            chunk_duration=30,
            min_silence_len=500,
            silence_thresh=-40,
            output_dir="./test_audio_files"
        )
    
    @pytest.fixture
    def sample_audio_file(self):
        """Create a temporary audio file for testing"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            # In a real test, you'd create actual audio data
            # For demo purposes, we'll just create an empty file
            temp_file.write(b"fake_audio_data")
            return temp_file.name
    
    def test_audio_processor_initialization(self, audio_processor):
        """Test that AudioProcessor initializes correctly"""
        assert audio_processor.chunk_duration == 30000  # Converted to milliseconds
        assert audio_processor.min_silence_len == 500
        assert audio_processor.silence_thresh == -40
        assert audio_processor.output_dir.name == "test_audio_files"
    
    def test_output_directory_creation(self, audio_processor):
        """Test that output directories are created"""
        # Directories should be created during initialization
        assert audio_processor.output_dir.exists()
        assert (audio_processor.output_dir / "chunks").exists()
        assert (audio_processor.output_dir / "temp").exists()
    
    @pytest.mark.asyncio
    async def test_analyze_audio_file_mock(self, audio_processor):
        """Test audio file analysis with mocked dependencies"""
        # Mock the external dependencies
        with patch('app.services.audio_processor.librosa') as mock_librosa, \
             patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
            
            # Configure mocks
            mock_librosa.load.return_value = ([1, 2, 3], 22050)  # Mock audio data and sample rate
            mock_librosa.duration.return_value = 60.0  # 60 seconds
            
            mock_audio = Mock()
            mock_audio.channels = 2
            mock_audio_segment.from_file.return_value = mock_audio
            mock_audio.export.return_value = None
            
            # Test the method
            result = await audio_processor._analyze_audio_file("/fake/path.wav", "test.wav")
            
            # Assertions
            assert isinstance(result, AudioFileModel)
            assert result.original_filename == "test.wav"
            assert result.duration_seconds == 60.0
            assert result.sample_rate == 22050
            assert result.channels == 2
            assert result.processing_status == ProcessingStatus.PROCESSING
    
    def test_chunk_file_path_generation(self, audio_processor):
        """Test chunk file path generation"""
        chunk_filename = "chunk_test_001_abc123.wav"
        expected_path = audio_processor.output_dir / "chunks" / chunk_filename
        
        result_path = audio_processor.get_chunk_file_path(chunk_filename)
        
        assert result_path == expected_path
    
    def test_cleanup_temp_files(self, audio_processor):
        """Test temporary file cleanup"""
        # Create some fake files
        test_file_id = "test123"
        chunk_dir = audio_processor.output_dir / "chunks"
        chunk_dir.mkdir(exist_ok=True)
        
        # Create test files
        test_files = [
            chunk_dir / f"chunk_{test_file_id}_001_abc.wav",
            chunk_dir / f"chunk_{test_file_id}_002_def.wav",
            audio_processor.output_dir / f"{test_file_id}_original.wav"
        ]
        
        for file_path in test_files:
            file_path.touch()  # Create empty file
        
        # Verify files exist
        for file_path in test_files:
            assert file_path.exists()
        
        # Clean up
        audio_processor.cleanup_temp_files(test_file_id)
        
        # Verify files are removed
        for file_path in test_files:
            assert not file_path.exists()
    
    @pytest.mark.asyncio
    async def test_demonstrate_chunking_strategies(self):
        """Test the educational demonstration function"""
        from app.services.audio_processor import demonstrate_chunking_strategies
        
        # This should run without errors
        await demonstrate_chunking_strategies()
        # In a real test, you might capture output and verify content
    
    def teardown_method(self):
        """Clean up after each test"""
        # Remove test directories if they exist
        import shutil
        test_dir = Path("./test_audio_files")
        if test_dir.exists():
            shutil.rmtree(test_dir)


class TestAudioModels:
    """Test the Pydantic models used for audio processing"""
    
    def test_audio_file_model_creation(self):
        """Test AudioFileModel creation and validation"""
        from datetime import datetime
        
        model_data = {
            "id": "test123",
            "filename": "processed_test.wav",
            "original_filename": "test.wav",
            "file_size": 1024000,
            "duration_seconds": 60.5,
            "format": "wav",
            "sample_rate": 44100,
            "channels": 2
        }
        
        audio_file = AudioFileModel(**model_data)
        
        # Test that all fields are properly set
        assert audio_file.id == "test123"
        assert audio_file.filename == "processed_test.wav"
        assert audio_file.original_filename == "test.wav"
        assert audio_file.file_size == 1024000
        assert audio_file.duration_seconds == 60.5
        assert audio_file.format == "wav"
        assert audio_file.sample_rate == 44100
        assert audio_file.channels == 2
        assert audio_file.processing_status == ProcessingStatus.PENDING
        assert isinstance(audio_file.upload_timestamp, datetime)
    
    def test_audio_chunk_model_creation(self):
        """Test AudioChunk model creation and validation"""
        chunk_data = {
            "id": "chunk123",
            "file_id": "file456",
            "chunk_index": 0,
            "start_time": 0.0,
            "end_time": 30.0,
            "duration": 30.0,
            "chunk_filename": "chunk_file456_000_chunk123.wav"
        }
        
        chunk = AudioChunk(**chunk_data)
        
        assert chunk.id == "chunk123"
        assert chunk.file_id == "file456"
        assert chunk.chunk_index == 0
        assert chunk.start_time == 0.0
        assert chunk.end_time == 30.0
        assert chunk.duration == 30.0
        assert chunk.chunk_filename == "chunk_file456_000_chunk123.wav"
    
    def test_audio_file_model_validation(self):
        """Test that AudioFileModel validates inputs correctly"""
        # Test with invalid data
        with pytest.raises(ValueError):
            AudioFileModel(
                id="",  # Empty string should fail
                filename="test.wav",
                original_filename="test.wav",
                file_size=-1,  # Negative size should fail
                duration_seconds=60.0,
                format="wav",
                sample_rate=44100,
                channels=2
            )


# Integration tests that test multiple components together
class TestAudioProcessingIntegration:
    """Integration tests for the complete audio processing workflow"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow  # Mark as slow test (can be skipped in quick test runs)
    async def test_complete_processing_workflow_mock(self):
        """Test the complete workflow with mocked audio processing"""
        processor = AudioProcessor(output_dir="./test_integration")
        
        with patch('app.services.audio_processor.librosa') as mock_librosa, \
             patch('app.services.audio_processor.AudioSegment') as mock_audio_segment:
            
            # Configure mocks for a 90-second audio file
            mock_librosa.load.return_value = ([1] * 1980000, 22050)  # 90 seconds of fake data
            mock_librosa.duration.return_value = 90.0
            
            # Mock AudioSegment
            mock_audio = Mock()
            mock_audio.channels = 1
            mock_audio_segment.from_file.return_value = mock_audio
            mock_audio.export.return_value = None
            
            # Mock chunking behavior
            with patch.object(processor, '_create_intelligent_chunks') as mock_chunk:
                # Mock 3 chunks for 90-second file
                mock_chunks = [
                    AudioChunk(
                        id=f"chunk{i}",
                        file_id="test_file",
                        chunk_index=i,
                        start_time=i * 30.0,
                        end_time=(i + 1) * 30.0,
                        duration=30.0,
                        chunk_filename=f"chunk_test_file_{i:03d}_chunk{i}.wav"
                    )
                    for i in range(3)
                ]
                mock_chunk.return_value = mock_chunks
                
                # Test processing
                audio_info, chunks = await processor.process_audio_file(
                    "/fake/path.wav", 
                    "test_90_seconds.wav"
                )
                
                # Verify results
                assert isinstance(audio_info, AudioFileModel)
                assert audio_info.original_filename == "test_90_seconds.wav"
                assert audio_info.duration_seconds == 90.0
                assert len(chunks) == 3
                assert all(isinstance(chunk, AudioChunk) for chunk in chunks)
                assert audio_info.processing_status == ProcessingStatus.COMPLETED
        
        # Cleanup
        import shutil
        test_dir = Path("./test_integration")
        if test_dir.exists():
            shutil.rmtree(test_dir)


# Performance tests
class TestAudioProcessingPerformance:
    """Performance tests for audio processing"""
    
    @pytest.mark.performance
    def test_chunking_algorithm_performance(self):
        """Test that chunking algorithms perform within acceptable limits"""
        import time
        
        processor = AudioProcessor()
        
        # Simulate processing large file metadata
        start_time = time.time()
        
        # Simulate processing 1000 metadata operations
        for i in range(1000):
            file_id = f"file_{i}"
            chunk_filename = f"chunk_{file_id}_001_abc123.wav"
            processor.get_chunk_file_path(chunk_filename)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete 1000 operations in less than 1 second
        assert processing_time < 1.0, f"Processing took {processing_time:.2f}s, expected < 1.0s"


if __name__ == "__main__":
    # Run tests when file is executed directly
    pytest.main([__file__, "-v"])


# Educational Notes for Students:
"""
Key Testing Concepts Demonstrated:

1. **Unit Tests**: Test individual functions in isolation
   - Use mocks to isolate the code under test
   - Test both happy path and error conditions

2. **Integration Tests**: Test how components work together
   - Test the complete workflow
   - Use realistic test data

3. **Performance Tests**: Ensure code meets performance requirements
   - Measure execution time
   - Test with large datasets

4. **Fixtures**: Reusable test setup code
   - @pytest.fixture creates reusable test data
   - Reduces code duplication

5. **Async Testing**: Testing asynchronous code
   - @pytest.mark.asyncio for async test functions
   - Use await in test functions

6. **Mocking**: Replace external dependencies
   - patch() replaces modules/functions temporarily
   - Mock() creates fake objects

Best Practices:
- Test should be fast, isolated, and repeatable
- Use descriptive test names
- Test edge cases and error conditions
- Keep tests simple and focused
- Use appropriate assertions
""" 