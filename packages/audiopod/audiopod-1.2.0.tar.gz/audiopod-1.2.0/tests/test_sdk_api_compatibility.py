"""
Comprehensive test suite to validate AudioPod Python SDK compatibility with actual API endpoints.
Tests all major services and endpoints for schema compatibility and functionality.
"""

import os
import sys
import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Add the parent directory to path to import the SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import audiopod
from audiopod.client import Client, AsyncClient
from audiopod.exceptions import (
    AudioPodError, AuthenticationError, APIError, 
    RateLimitError, ValidationError, ProcessingError
)
from audiopod.models import (
    Job, VoiceProfile, TranscriptionResult, 
    MusicGenerationResult, TranslationResult
)


class TestSDKAPICompatibility:
    """Test suite for validating SDK compatibility with actual API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client with mock API key"""
        return Client(api_key="ap_test_key_12345", base_url="https://api.audiopod.ai")
    
    @pytest.fixture
    def async_client(self):
        """Create a test async client with mock API key"""
        return AsyncClient(api_key="ap_test_key_12345", base_url="https://api.audiopod.ai")
    
    def test_client_initialization(self):
        """Test client initialization with proper API key validation"""
        # Valid API key
        client = Client(api_key="ap_test_key")
        assert client.api_key == "ap_test_key"
        
        # Invalid API key format
        with pytest.raises(AuthenticationError):
            Client(api_key="invalid_key")
        
        # No API key
        with pytest.raises(AuthenticationError):
            Client()
    
    def test_api_key_formats(self):
        """Test that client accepts correct API key formats"""
        valid_keys = [
            "ap_test_key",
            "ap_live_abcd1234567890",
            "ap_dev_xyz123"
        ]
        
        for key in valid_keys:
            client = Client(api_key=key)
            assert client.api_key == key
    
    def test_client_headers(self, client):
        """Test that client generates correct headers"""
        headers = client._get_headers()
        
        assert headers["Authorization"] == "Bearer ap_test_key_12345"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "audiopod-python" in headers["User-Agent"]
    
    @patch('requests.Session.request')
    def test_health_check_endpoint(self, mock_request, client):
        """Test health check endpoint compatibility"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        mock_request.return_value = mock_response
        
        result = client.check_health()
        assert result["status"] == "healthy"
        
        # Verify request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "/api/v1/health" in kwargs["url"]


class TestVoiceServiceCompatibility:
    """Test voice service compatibility with API endpoints"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_voice_clone_endpoint_compatibility(self, mock_request, client):
        """Test voice cloning endpoint matches API specification"""
        # Mock API response based on actual endpoint schema
        mock_request.return_value = {
            "id": 123,
            "voice_id": 1,
            "status": "pending",
            "input_text": "Hello world",
            "target_language": "en",
            "created_at": "2024-01-01T12:00:00Z",
            "task_id": "abc-123-def",
            "progress": 0.0
        }
        
        # Test voice cloning request
        result = client.voice.clone_voice(
            voice_file="test_voice.wav",
            text="Hello world",
            language="en",
            speed=1.0
        )
        
        # Verify the request structure
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        # Check endpoint
        assert args[1] == "/api/v1/voice/voice-clone"
        assert args[0] == "POST"
        
        # Check that files were prepared correctly
        assert "files" in kwargs
        assert "data" in kwargs
        
        # Check data structure matches API expectations
        data = kwargs["data"]
        assert data["input_text"] == "Hello world"
        assert data["speed"] == 1.0
        assert data["target_language"] == "en"
    
    @patch('audiopod.client.Client.request')
    def test_voice_profile_creation(self, mock_request, client):
        """Test voice profile creation matches API schema"""
        mock_request.return_value = {
            "id": 1,
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Voice",
            "description": "Test description",
            "status": "pending",
            "voice_type": "custom",
            "provider": "audiopod_sonic",
            "is_public": False,
            "created_at": "2024-01-01T12:00:00Z"
        }
        
        result = client.voice.create_voice_profile(
            name="Test Voice",
            voice_file="test.wav",
            description="Test description",
            is_public=False
        )
        
        # Verify API call structure
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/voice/voice-profiles"
        assert args[0] == "POST"
        assert "files" in kwargs
        assert "data" in kwargs
        
        data = kwargs["data"]
        assert data["name"] == "Test Voice"
        assert data["description"] == "Test description"
        assert data["is_public"] is False
    
    @patch('audiopod.client.Client.request')
    def test_list_voice_profiles(self, mock_request, client):
        """Test listing voice profiles matches API response schema"""
        mock_request.return_value = [
            {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Voice 1",
                "description": "First voice",
                "status": "completed",
                "voice_type": "custom",
                "provider": "audiopod_sonic",
                "is_public": False,
                "created_at": "2024-01-01T12:00:00Z"
            },
            {
                "id": 2,
                "uuid": "550e8400-e29b-41d4-a716-446655440001",
                "name": "Voice 2",
                "description": "Second voice",
                "status": "completed",
                "voice_type": "standard",
                "provider": "openai",
                "is_public": True,
                "created_at": "2024-01-01T12:00:00Z"
            }
        ]
        
        voices = client.voice.list_voice_profiles(limit=10)
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/voice/voice-profiles"
        assert args[0] == "GET"
        assert "params" in kwargs
        assert kwargs["params"]["limit"] == 10
        
        # Verify response structure
        assert len(voices) == 2
        assert all(isinstance(voice, VoiceProfile) for voice in voices)


class TestMusicServiceCompatibility:
    """Test music service compatibility with API endpoints"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_music_generation_text2music(self, mock_request, client):
        """Test text2music endpoint compatibility"""
        mock_request.return_value = {
            "job": {
                "id": 123,
                "task": "text2music",
                "status": "pending",
                "input_params": {
                    "prompt": "upbeat jazz music",
                    "duration": 120.0
                },
                "created_at": "2024-01-01T12:00:00Z",
                "task_id": "music-abc-123"
            },
            "message": "Music generation job created successfully"
        }
        
        result = client.music.generate_music(
            prompt="upbeat jazz music",
            duration=120.0,
            guidance_scale=7.5,
            num_inference_steps=50
        )
        
        # Verify API call structure
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/music/text2music"
        assert args[0] == "POST"
        assert "data" in kwargs
        
        data = kwargs["data"]
        assert data["prompt"] == "upbeat jazz music"
        assert data["duration"] == 120.0
        assert data["guidance_scale"] == 7.5
        assert data["num_inference_steps"] == 50
    
    @patch('audiopod.client.Client.request')
    def test_music_generation_rap(self, mock_request, client):
        """Test text2rap endpoint compatibility"""
        mock_request.return_value = {
            "job": {
                "id": 124,
                "task": "text2rap",
                "status": "pending",
                "input_params": {
                    "lyrics": "Test rap lyrics",
                    "style": "modern"
                },
                "created_at": "2024-01-01T12:00:00Z"
            },
            "message": "Rap generation job created successfully"
        }
        
        result = client.music.generate_rap(
            lyrics="Test rap lyrics",
            style="modern",
            tempo=120
        )
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/music/text2rap"
        assert args[0] == "POST"
        
        data = kwargs["data"]
        assert data["lyrics"] == "Test rap lyrics"
        assert data["style"] == "modern"
        assert data["tempo"] == 120
    
    @patch('audiopod.client.Client.request')
    def test_list_music_jobs(self, mock_request, client):
        """Test listing music jobs matches API response"""
        mock_request.return_value = [
            {
                "id": 123,
                "task": "text2music",
                "status": "completed",
                "input_params": {"prompt": "jazz music"},
                "output_url": "https://storage.example.com/music/123.wav",
                "created_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:05:00Z"
            }
        ]
        
        jobs = client.music.list_music_jobs(limit=50)
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/music/jobs"
        assert args[0] == "GET"
        assert kwargs["params"]["limit"] == 50


class TestTranscriptionServiceCompatibility:
    """Test transcription service compatibility"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_transcribe_audio_upload(self, mock_request, client):
        """Test transcription upload endpoint compatibility"""
        mock_request.return_value = {
            "job_id": 123,
            "task_id": "transcribe-abc-123",
            "status": "PENDING",
            "message": "Transcription job created successfully",
            "estimated_credits": 150,
            "estimated_duration": 3600
        }
        
        result = client.transcription.transcribe_audio(
            audio_file="test_audio.wav",
            language="en",
            model_type="whisperx",
            enable_speaker_diarization=True,
            enable_word_timestamps=True
        )
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/transcription/transcribe-upload"
        assert args[0] == "POST"
        assert "files" in kwargs
        assert "data" in kwargs
        
        data = kwargs["data"]
        assert data["language"] == "en"
        assert data["model_type"] == "whisperx"
        assert data["enable_speaker_diarization"] is True
        assert data["enable_word_timestamps"] is True
    
    @patch('audiopod.client.Client.request')
    def test_transcribe_url(self, mock_request, client):
        """Test transcription URL endpoint compatibility"""
        mock_request.return_value = {
            "job_id": 124,
            "task_id": "transcribe-url-abc-124",
            "status": "PENDING",
            "message": "Transcription job created successfully"
        }
        
        result = client.transcription.transcribe_url(
            url="https://example.com/audio.mp3",
            language="en",
            model_type="whisperx"
        )
        
        # Verify API call structure
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/transcription/transcribe"
        assert args[0] == "POST"
        
        data = kwargs["data"]
        assert data["source_urls"] == ["https://example.com/audio.mp3"]
        assert data["language"] == "en"
        assert data["model_type"] == "whisperx"


class TestTranslationServiceCompatibility:
    """Test translation service compatibility"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_translate_audio(self, mock_request, client):
        """Test audio translation endpoint compatibility"""
        mock_request.return_value = {
            "id": 123,
            "status": "pending",
            "target_language": "es",
            "source_language": "en",
            "input_path": "uploads/audio.wav",
            "created_at": "2024-01-01T12:00:00Z",
            "task_id": "translate-abc-123"
        }
        
        result = client.translation.translate_audio(
            audio_file="test_audio.wav",
            target_language="es",
            source_language="en"
        )
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/translation/translate"
        assert args[0] == "POST"
        assert "files" in kwargs
        assert "data" in kwargs
        
        data = kwargs["data"]
        assert data["target_language"] == "es"
        assert data["source_language"] == "en"


class TestCreditsServiceCompatibility:
    """Test credits service compatibility"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_get_credit_balance(self, mock_request, client):
        """Test credit balance endpoint compatibility"""
        mock_request.return_value = {
            "balance": 10000,
            "payg_balance": 500,
            "total_available_credits": 10500,
            "total_credits_used": 2000,
            "next_reset_date": "2024-02-01T00:00:00Z"
        }
        
        result = client.credits.get_credit_balance()
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/credits"
        assert args[0] == "GET"
        
        # Verify response structure
        assert result.balance == 10000
        assert result.payg_balance == 500
        assert result.total_available_credits == 10500
    
    @patch('audiopod.client.Client.request')
    def test_get_usage_history(self, mock_request, client):
        """Test credit usage history endpoint"""
        mock_request.return_value = [
            {
                "created_at": "2024-01-01T12:00:00Z",
                "service_type": "voice_cloning",
                "credits_used": 100,
                "audio_duration": 30
            },
            {
                "created_at": "2024-01-01T11:30:00Z",
                "service_type": "transcription",
                "credits_used": 50,
                "audio_duration": 120
            }
        ]
        
        result = client.credits.get_usage_history()
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/credits/usage"
        assert args[0] == "GET"
        
        # Verify response structure
        assert len(result) == 2
        assert result[0]["service_type"] == "voice_cloning"
        assert result[0]["credits_used"] == 100


class TestDenoiserServiceCompatibility:
    """Test denoiser service compatibility"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_denoise_audio(self, mock_request, client):
        """Test audio denoising endpoint compatibility"""
        mock_request.return_value = {
            "id": 123,
            "status": "pending",
            "input_path": "uploads/noisy_audio.wav",
            "created_at": "2024-01-01T12:00:00Z",
            "task_id": "denoise-abc-123"
        }
        
        result = client.denoiser.denoise_audio(
            audio_file="noisy_audio.wav",
            quality_mode="balanced"
        )
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/denoiser/denoise"
        assert args[0] == "POST"
        assert "files" in kwargs
        assert "data" in kwargs
        
        data = kwargs["data"]
        assert data["quality_mode"] == "balanced"


class TestSpeakerServiceCompatibility:
    """Test speaker service compatibility"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_diarize_speakers(self, mock_request, client):
        """Test speaker diarization endpoint compatibility"""
        mock_request.return_value = {
            "id": 123,
            "status": "pending",
            "input_path": "uploads/multi_speaker.wav",
            "job_type": "diarize",
            "created_at": "2024-01-01T12:00:00Z",
            "task_id": "speaker-abc-123"
        }
        
        result = client.speaker.diarize_speakers(
            audio_file="multi_speaker.wav",
            num_speakers=3
        )
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/speaker/diarize"
        assert args[0] == "POST"
        assert "files" in kwargs
        assert "data" in kwargs
        
        data = kwargs["data"]
        assert data["num_speakers"] == 3


class TestKaraokeServiceCompatibility:
    """Test karaoke service compatibility"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_generate_karaoke(self, mock_request, client):
        """Test karaoke generation endpoint compatibility"""
        mock_request.return_value = {
            "id": 123,
            "status": "pending",
            "input_path": "uploads/song.wav",
            "video_style": "modern",
            "created_at": "2024-01-01T12:00:00Z",
            "task_id": "karaoke-abc-123"
        }
        
        result = client.karaoke.generate_karaoke(
            audio_file="song.wav",
            video_style="modern",
            custom_lyrics="Test lyrics"
        )
        
        # Verify API call
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[1] == "/api/v1/karaoke/generate"
        assert args[0] == "POST"
        assert "files" in kwargs
        assert "data" in kwargs
        
        data = kwargs["data"]
        assert data["video_style"] == "modern"
        assert data["custom_lyrics"] == "Test lyrics"


class TestAsyncClientCompatibility:
    """Test async client functionality"""
    
    @pytest.fixture
    def async_client(self):
        return AsyncClient(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @pytest.mark.asyncio
    async def test_async_health_check(self, async_client):
        """Test async health check functionality"""
        with patch.object(async_client, 'request') as mock_request:
            mock_request.return_value = {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            result = await async_client.check_health()
            assert result["status"] == "healthy"
            
            mock_request.assert_called_once_with("GET", "/api/v1/health")
    
    @pytest.mark.asyncio
    async def test_async_voice_cloning(self, async_client):
        """Test async voice cloning functionality"""
        with patch.object(async_client.voice, '_async_clone_voice') as mock_clone:
            mock_clone.return_value = {
                "id": 123,
                "status": "pending",
                "output_url": "https://storage.example.com/voice.wav"
            }
            
            result = await async_client.voice.clone_voice(
                voice_file="test.wav",
                text="Hello world",
                wait_for_completion=False
            )
            
            mock_clone.assert_called_once()


class TestErrorHandling:
    """Test error handling and exception compatibility"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    def test_authentication_error(self):
        """Test authentication error handling"""
        with pytest.raises(AuthenticationError):
            Client(api_key="invalid_key_format")
    
    @patch('audiopod.client.Client.request')
    def test_api_error_handling(self, mock_request, client):
        """Test API error response handling"""
        from requests.exceptions import HTTPError
        from requests import Response
        
        # Create a mock response for 400 error
        mock_response = Mock(spec=Response)
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid input"}
        
        # Create HTTPError
        http_error = HTTPError()
        http_error.response = mock_response
        
        mock_request.side_effect = http_error
        
        with pytest.raises(APIError) as exc_info:
            client.check_health()
        
        assert "API request failed" in str(exc_info.value)
    
    @patch('audiopod.client.Client.request')
    def test_rate_limit_error(self, mock_request, client):
        """Test rate limit error handling"""
        from requests.exceptions import HTTPError
        from requests import Response
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 429
        
        http_error = HTTPError()
        http_error.response = mock_response
        
        mock_request.side_effect = http_error
        
        with pytest.raises(RateLimitError):
            client.check_health()


class TestSchemaValidation:
    """Test data schema validation and model compatibility"""
    
    def test_job_model_creation(self):
        """Test Job model creation from API response"""
        job_data = {
            "id": 123,
            "status": "completed",
            "created_at": "2024-01-01T12:00:00Z",
            "progress": 100.0,
            "result": {"output_url": "https://example.com/output.wav"}
        }
        
        job = Job.from_dict(job_data)
        assert job.id == 123
        assert job.status == "completed"
        assert job.progress == 100.0
    
    def test_voice_profile_model(self):
        """Test VoiceProfile model creation"""
        voice_data = {
            "id": 1,
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Voice",
            "description": "Test description",
            "voice_type": "custom",
            "provider": "audiopod_sonic",
            "is_public": False,
            "created_at": "2024-01-01T12:00:00Z",
            "status": "completed"
        }
        
        voice = VoiceProfile.from_dict(voice_data)
        assert voice.id == 1
        assert voice.name == "Test Voice"
        assert voice.voice_type == "custom"
    
    def test_music_generation_result_model(self):
        """Test MusicGenerationResult model creation"""
        result_data = {
            "id": 123,
            "status": "completed",
            "created_at": "2024-01-01T12:00:00Z",
            "output_url": "https://example.com/music.wav",
            "audio_duration": 120.5,
            "actual_seeds": [12345, 67890]
        }
        
        result = MusicGenerationResult.from_dict(result_data)
        assert result.job.id == 123
        assert result.output_url == "https://example.com/music.wav"
        assert result.audio_duration == 120.5


class TestEndToEndWorkflow:
    """End-to-end workflow tests simulating real usage scenarios"""
    
    @pytest.fixture
    def client(self):
        return Client(api_key="ap_test_key", base_url="https://api.audiopod.ai")
    
    @patch('audiopod.client.Client.request')
    def test_complete_voice_cloning_workflow(self, mock_request, client):
        """Test complete voice cloning workflow"""
        # Mock sequence of API calls
        mock_responses = [
            # 1. Create voice profile
            {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "My Voice",
                "status": "completed",
                "voice_type": "custom",
                "provider": "audiopod_sonic",
                "is_public": False,
                "created_at": "2024-01-01T12:00:00Z"
            },
            # 2. Clone voice
            {
                "id": 123,
                "voice_id": 1,
                "status": "pending",
                "input_text": "Hello world",
                "created_at": "2024-01-01T12:00:00Z",
                "task_id": "clone-abc-123"
            },
            # 3. Check job status
            {
                "id": 123,
                "status": "completed",
                "output_url": "https://storage.example.com/clone_123.wav",
                "completed_at": "2024-01-01T12:05:00Z"
            }
        ]
        
        mock_request.side_effect = mock_responses
        
        # Step 1: Create voice profile
        voice = client.voice.create_voice_profile(
            name="My Voice",
            voice_file="voice_sample.wav",
            wait_for_completion=False
        )
        assert voice.id == 1
        assert voice.name == "My Voice"
        
        # Step 2: Clone voice
        job = client.voice.clone_voice(
            voice_file="voice_sample.wav",
            text="Hello world",
            wait_for_completion=False
        )
        assert job.id == 123
        assert job.status == "pending"
        
        # Step 3: Check job status (simulate polling)
        status = client.voice.get_job_status(job.id)
        assert status.status == "completed"
    
    @patch('audiopod.client.Client.request')
    def test_complete_music_generation_workflow(self, mock_request, client):
        """Test complete music generation workflow"""
        # Mock sequence for music generation
        mock_responses = [
            # 1. Generate music
            {
                "job": {
                    "id": 456,
                    "task": "text2music",
                    "status": "pending",
                    "input_params": {"prompt": "jazz music"},
                    "created_at": "2024-01-01T12:00:00Z"
                },
                "message": "Music generation started"
            },
            # 2. Check status
            {
                "id": 456,
                "status": "completed",
                "output_url": "https://storage.example.com/music_456.wav",
                "audio_duration": 120.0,
                "completed_at": "2024-01-01T12:10:00Z"
            },
            # 3. Like the track
            {
                "success": True,
                "message": "Track liked successfully",
                "like_count": 1,
                "user_has_liked": True
            }
        ]
        
        mock_request.side_effect = mock_responses
        
        # Step 1: Generate music
        job = client.music.generate_music(
            prompt="jazz music",
            duration=120.0,
            wait_for_completion=False
        )
        assert job.id == 456
        
        # Step 2: Check status
        result = client.music.get_music_job(job.id)
        assert result.job.status == "completed"
        assert result.output_url is not None
        
        # Step 3: Like the track
        like_result = client.music.like_music_track(job.id)
        assert like_result["success"] is True
        assert like_result["like_count"] == 1


if __name__ == "__main__":
    # Run specific test sections
    pytest.main([
        __file__ + "::TestSDKAPICompatibility",
        "-v", "--tb=short"
    ])
