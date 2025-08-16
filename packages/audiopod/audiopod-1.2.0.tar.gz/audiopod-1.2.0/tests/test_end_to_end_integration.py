"""
End-to-end integration tests for AudioPod Python SDK.
These tests verify the SDK works correctly with actual API endpoints.
"""

import os
import sys
import asyncio
import tempfile
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add the parent directory to path to import the SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import audiopod
from audiopod.exceptions import AudioPodError, AuthenticationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndToEndTester:
    """End-to-end tester for AudioPod SDK"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the tester
        
        Args:
            api_key: AudioPod API key. If None, will try environment variable
            base_url: API base URL. If None, uses default
        """
        self.api_key = api_key or os.getenv("AUDIOPOD_API_KEY")
        self.base_url = base_url or "https://api.audiopod.ai"
        
        if not self.api_key:
            raise ValueError(
                "API key required. Set AUDIOPOD_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        # Initialize clients
        self.client = audiopod.Client(
            api_key=self.api_key, 
            base_url=self.base_url,
            debug=True
        )
        self.async_client = audiopod.AsyncClient(
            api_key=self.api_key,
            base_url=self.base_url,
            debug=True
        )
        
        # Test results
        self.test_results = {}
        self.test_files = []
    
    def create_test_audio_file(self, filename: str = "test_audio.wav") -> str:
        """Create a test audio file for testing"""
        # Create a simple test audio file (sine wave)
        try:
            import numpy as np
            import wave
            
            # Generate a 3-second sine wave at 440 Hz
            sample_rate = 16000
            duration = 3.0
            frequency = 440.0
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio_data = np.sin(2 * np.pi * frequency * t)
            
            # Convert to 16-bit PCM
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)
            
            with wave.open(file_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            self.test_files.append(file_path)
            logger.info(f"Created test audio file: {file_path}")
            return file_path
            
        except ImportError:
            # If numpy/wave not available, create a dummy file
            logger.warning("numpy not available, creating dummy audio file")
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)
            
            # Create a small dummy WAV file header
            with open(file_path, 'wb') as f:
                # Write minimal WAV header for a 1-second 16kHz mono file
                f.write(b'RIFF')
                f.write((36).to_bytes(4, 'little'))  # File size - 8
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write((16).to_bytes(4, 'little'))  # Format chunk size
                f.write((1).to_bytes(2, 'little'))   # Audio format (PCM)
                f.write((1).to_bytes(2, 'little'))   # Number of channels
                f.write((16000).to_bytes(4, 'little'))  # Sample rate
                f.write((32000).to_bytes(4, 'little'))  # Byte rate
                f.write((2).to_bytes(2, 'little'))   # Block align
                f.write((16).to_bytes(2, 'little'))  # Bits per sample
                f.write(b'data')
                f.write((0).to_bytes(4, 'little'))   # Data chunk size
            
            self.test_files.append(file_path)
            return file_path
    
    def cleanup_test_files(self):
        """Clean up created test files"""
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up test file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {file_path}: {e}")
        self.test_files.clear()
    
    def test_client_initialization(self) -> bool:
        """Test client initialization and configuration"""
        logger.info("Testing client initialization...")
        
        try:
            # Test valid API key
            client = audiopod.Client(api_key=self.api_key)
            assert client.api_key == self.api_key
            
            # Test invalid API key format
            try:
                audiopod.Client(api_key="invalid_key")
                return False  # Should have raised exception
            except AuthenticationError:
                pass  # Expected
            
            # Test async client
            async_client = audiopod.AsyncClient(api_key=self.api_key)
            assert async_client.api_key == self.api_key
            
            self.test_results["client_initialization"] = True
            logger.info("✅ Client initialization test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Client initialization test failed: {e}")
            self.test_results["client_initialization"] = False
            return False
    
    def test_health_check(self) -> bool:
        """Test API health check endpoint"""
        logger.info("Testing health check endpoint...")
        
        try:
            result = self.client.check_health()
            assert isinstance(result, dict)
            logger.info(f"Health check response: {result}")
            
            self.test_results["health_check"] = True
            logger.info("✅ Health check test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check test failed: {e}")
            self.test_results["health_check"] = False
            return False
    
    def test_user_info(self) -> bool:
        """Test getting user information"""
        logger.info("Testing user info endpoint...")
        
        try:
            user_info = self.client.get_user_info()
            assert isinstance(user_info, dict)
            assert "id" in user_info or "email" in user_info
            
            logger.info(f"User info retrieved: {user_info.get('email', 'N/A')}")
            
            self.test_results["user_info"] = True
            logger.info("✅ User info test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ User info test failed: {e}")
            self.test_results["user_info"] = False
            return False
    
    def test_credits_service(self) -> bool:
        """Test credits service functionality"""
        logger.info("Testing credits service...")
        
        try:
            # Get credit balance
            credits = self.client.credits.get_credit_balance()
            assert hasattr(credits, 'balance') or hasattr(credits, 'total_available_credits')
            
            logger.info(f"Credit balance: {getattr(credits, 'total_available_credits', 'N/A')}")
            
            # Get usage history
            usage = self.client.credits.get_usage_history()
            assert isinstance(usage, list)
            
            logger.info(f"Usage history entries: {len(usage)}")
            
            # Get credit multipliers
            multipliers = self.client.credits.get_credit_multipliers()
            assert isinstance(multipliers, dict)
            
            logger.info(f"Credit multipliers: {list(multipliers.keys())}")
            
            self.test_results["credits_service"] = True
            logger.info("✅ Credits service test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Credits service test failed: {e}")
            self.test_results["credits_service"] = False
            return False
    
    def test_voice_service(self) -> bool:
        """Test voice service functionality"""
        logger.info("Testing voice service...")
        
        try:
            # List voice profiles
            voices = self.client.voice.list_voice_profiles(limit=5)
            assert isinstance(voices, list)
            
            logger.info(f"Found {len(voices)} voice profiles")
            
            # Create test audio file for voice operations
            test_audio = self.create_test_audio_file("test_voice.wav")
            
            # Test voice cloning (without waiting for completion)
            if os.path.exists(test_audio):
                job = self.client.voice.clone_voice(
                    voice_file=test_audio,
                    text="This is a test of voice cloning.",
                    language="en",
                    wait_for_completion=False
                )
                
                assert hasattr(job, 'id')
                logger.info(f"Voice cloning job created: {job.id}")
                
                # Check job status
                status = self.client.voice.get_job_status(job.id)
                assert hasattr(status, 'status')
                logger.info(f"Job status: {status.status}")
            
            self.test_results["voice_service"] = True
            logger.info("✅ Voice service test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Voice service test failed: {e}")
            self.test_results["voice_service"] = False
            return False
    
    def test_music_service(self) -> bool:
        """Test music service functionality"""
        logger.info("Testing music service...")
        
        try:
            # Generate music (without waiting for completion)
            job = self.client.music.generate_music(
                prompt="upbeat electronic dance music",
                duration=30.0,  # Short duration for testing
                wait_for_completion=False
            )
            
            assert hasattr(job, 'id')
            logger.info(f"Music generation job created: {job.id}")
            
            # List music jobs
            jobs = self.client.music.list_music_jobs(limit=5)
            assert isinstance(jobs, list)
            logger.info(f"Found {len(jobs)} music jobs")
            
            # Get job status
            if hasattr(job, 'id'):
                status = self.client.music.get_music_job(job.id)
                logger.info(f"Music job status: {status.job.status}")
            
            self.test_results["music_service"] = True
            logger.info("✅ Music service test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Music service test failed: {e}")
            self.test_results["music_service"] = False
            return False
    
    def test_transcription_service(self) -> bool:
        """Test transcription service functionality"""
        logger.info("Testing transcription service...")
        
        try:
            # Create test audio file
            test_audio = self.create_test_audio_file("test_transcription.wav")
            
            if os.path.exists(test_audio):
                # Test transcription (without waiting for completion)
                job = self.client.transcription.transcribe_audio(
                    audio_file=test_audio,
                    language="en",
                    enable_speaker_diarization=False,
                    wait_for_completion=False
                )
                
                assert hasattr(job, 'id')
                logger.info(f"Transcription job created: {job.id}")
                
                # Get job status
                status = self.client.transcription.get_transcription_job(job.id)
                logger.info(f"Transcription status: {status.job.status}")
            
            self.test_results["transcription_service"] = True
            logger.info("✅ Transcription service test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Transcription service test failed: {e}")
            self.test_results["transcription_service"] = False
            return False
    
    def test_translation_service(self) -> bool:
        """Test translation service functionality"""
        logger.info("Testing translation service...")
        
        try:
            # Create test audio file
            test_audio = self.create_test_audio_file("test_translation.wav")
            
            if os.path.exists(test_audio):
                # Test translation (without waiting for completion)
                job = self.client.translation.translate_audio(
                    audio_file=test_audio,
                    target_language="es",  # Translate to Spanish
                    source_language="en",
                    wait_for_completion=False
                )
                
                assert hasattr(job, 'id')
                logger.info(f"Translation job created: {job.id}")
                
                # Get job status
                status = self.client.translation.get_translation_job(job.id)
                logger.info(f"Translation status: {status.job.status}")
            
            self.test_results["translation_service"] = True
            logger.info("✅ Translation service test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Translation service test failed: {e}")
            self.test_results["translation_service"] = False
            return False
    
    def test_denoiser_service(self) -> bool:
        """Test denoiser service functionality"""
        logger.info("Testing denoiser service...")
        
        try:
            # Create test audio file
            test_audio = self.create_test_audio_file("test_denoiser.wav")
            
            if os.path.exists(test_audio):
                # Test denoising (without waiting for completion)
                job = self.client.denoiser.denoise_audio(
                    audio_file=test_audio,
                    quality_mode="balanced",
                    wait_for_completion=False
                )
                
                assert hasattr(job, 'id')
                logger.info(f"Denoiser job created: {job.id}")
            
            self.test_results["denoiser_service"] = True
            logger.info("✅ Denoiser service test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Denoiser service test failed: {e}")
            self.test_results["denoiser_service"] = False
            return False
    
    def test_speaker_service(self) -> bool:
        """Test speaker service functionality"""
        logger.info("Testing speaker service...")
        
        try:
            # Create test audio file
            test_audio = self.create_test_audio_file("test_speaker.wav")
            
            if os.path.exists(test_audio):
                # Test speaker diarization (without waiting for completion)
                job = self.client.speaker.diarize_speakers(
                    audio_file=test_audio,
                    num_speakers=2,
                    wait_for_completion=False
                )
                
                assert hasattr(job, 'id')
                logger.info(f"Speaker diarization job created: {job.id}")
            
            self.test_results["speaker_service"] = True
            logger.info("✅ Speaker service test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Speaker service test failed: {e}")
            self.test_results["speaker_service"] = False
            return False
    
    def test_karaoke_service(self) -> bool:
        """Test karaoke service functionality"""
        logger.info("Testing karaoke service...")
        
        try:
            # Create test audio file
            test_audio = self.create_test_audio_file("test_karaoke.wav")
            
            if os.path.exists(test_audio):
                # Test karaoke generation (without waiting for completion)
                job = self.client.karaoke.generate_karaoke(
                    audio_file=test_audio,
                    video_style="modern",
                    custom_lyrics="Test lyrics for karaoke",
                    wait_for_completion=False
                )
                
                assert hasattr(job, 'id')
                logger.info(f"Karaoke job created: {job.id}")
            
            self.test_results["karaoke_service"] = True
            logger.info("✅ Karaoke service test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Karaoke service test failed: {e}")
            self.test_results["karaoke_service"] = False
            return False
    
    async def test_async_functionality(self) -> bool:
        """Test async client functionality"""
        logger.info("Testing async functionality...")
        
        try:
            # Test async health check
            health = await self.async_client.check_health()
            assert isinstance(health, dict)
            
            # Test async user info
            user_info = await self.async_client.get_user_info()
            assert isinstance(user_info, dict)
            
            # Test async credits
            credits = await self.async_client.credits.get_credit_balance()
            assert hasattr(credits, 'balance') or hasattr(credits, 'total_available_credits')
            
            self.test_results["async_functionality"] = True
            logger.info("✅ Async functionality test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Async functionality test failed: {e}")
            self.test_results["async_functionality"] = False
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and exception cases"""
        logger.info("Testing error handling...")
        
        try:
            # Test invalid API key
            try:
                invalid_client = audiopod.Client(api_key="ap_invalid_key")
                invalid_client.check_health()
                return False  # Should have failed
            except (AuthenticationError, AudioPodError):
                pass  # Expected
            
            # Test invalid file path
            try:
                self.client.voice.clone_voice(
                    voice_file="non_existent_file.wav",
                    text="Test",
                    wait_for_completion=False
                )
                return False  # Should have failed
            except (FileNotFoundError, AudioPodError):
                pass  # Expected
            
            self.test_results["error_handling"] = True
            logger.info("✅ Error handling test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            self.test_results["error_handling"] = False
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        logger.info("Starting comprehensive SDK tests...")
        
        # List of all tests to run
        tests = [
            self.test_client_initialization,
            self.test_health_check,
            self.test_user_info,
            self.test_credits_service,
            self.test_voice_service,
            self.test_music_service,
            self.test_transcription_service,
            self.test_translation_service,
            self.test_denoiser_service,
            self.test_speaker_service,
            self.test_karaoke_service,
            self.test_error_handling,
        ]
        
        # Run sync tests
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
                self.test_results[test.__name__] = False
        
        # Run async tests
        try:
            asyncio.run(self.test_async_functionality())
        except Exception as e:
            logger.error(f"Async test failed: {e}")
            self.test_results["async_functionality"] = False
        
        # Clean up test files
        self.cleanup_test_files()
        
        # Close clients
        if hasattr(self.client, 'close'):
            self.client.close()
        
        return self.test_results
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("AudioPod SDK End-to-End Test Results")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<30} {status}")
            
            if result:
                passed += 1
            else:
                failed += 1
        
        print("-"*60)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")
        print("="*60)
        
        return passed, failed


def main():
    """Main function to run the tests"""
    # Check for API key
    api_key = os.getenv("AUDIOPOD_API_KEY")
    if not api_key:
        print("Error: AUDIOPOD_API_KEY environment variable not set")
        print("Please set your AudioPod API key:")
        print("export AUDIOPOD_API_KEY='ap_your_api_key_here'")
        return 1
    
    # Get base URL from environment or use default
    base_url = os.getenv("AUDIOPOD_BASE_URL", "https://api.audiopod.ai")
    
    # Create tester and run tests
    tester = EndToEndTester(api_key=api_key, base_url=base_url)
    
    try:
        results = tester.run_all_tests()
        passed, failed = tester.print_results()
        
        # Return exit code based on results
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
