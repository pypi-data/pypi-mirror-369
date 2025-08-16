"""
Voice Service - Voice cloning and TTS operations
"""

import time
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from .base import BaseService
from ..models import Job, VoiceProfile, JobStatus
from ..exceptions import ValidationError


class VoiceService(BaseService):
    """Service for voice cloning and text-to-speech operations"""
    
    def generate_voice(
        self,
        text: str,
        voice_file: Optional[str] = None,
        voice_id: Optional[Union[int, str]] = None,
        language: Optional[str] = None,
        speed: float = 1.0,
        audio_format: str = "mp3",
        generation_params: Optional[Dict[str, Any]] = None,
        wait_for_completion: bool = False,
        timeout: int = 300
    ) -> Union[Job, Dict[str, Any]]:
        """
        Generate speech using either a voice file (for cloning) or existing voice profile
        
        This unified method handles both voice cloning and text-to-speech generation:
        - For voice cloning: Provide voice_file parameter
        - For TTS with existing voice: Provide voice_id parameter
        
        Args:
            text: Text to generate speech for
            voice_file: Path to audio file for voice cloning (mutually exclusive with voice_id)
            voice_id: ID/UUID of existing voice profile (mutually exclusive with voice_file)
            language: Target language code (e.g., 'en', 'es')
            speed: Speech speed (0.25 to 4.0, provider dependent)
            audio_format: Output audio format ('mp3', 'wav', 'ogg')
            generation_params: Provider-specific parameters (speed, temperature, etc.)
            wait_for_completion: Whether to wait for job completion
            timeout: Maximum time to wait if wait_for_completion=True
            
        Returns:
            Job object if wait_for_completion=False, otherwise job result
            
        Raises:
            ValidationError: If both or neither voice_file and voice_id are provided
        """
        # Validate inputs
        if not voice_file and not voice_id:
            raise ValidationError("Either voice_file (for cloning) or voice_id (for TTS) must be provided")
        if voice_file and voice_id:
            raise ValidationError("Provide either voice_file or voice_id, not both")
            
        text = self._validate_text_input(text)
        if language:
            language = self._validate_language_code(language)
        if not 0.25 <= speed <= 4.0:
            raise ValidationError("Speed must be between 0.25 and 4.0")
        if audio_format not in ["mp3", "wav", "ogg"]:
            raise ValidationError("Audio format must be 'mp3', 'wav', or 'ogg'")
            
        # For voice cloning, we need to create a temporary voice first, then generate
        if voice_file:
            return self._generate_with_voice_file(
                voice_file, text, language, speed, audio_format, 
                generation_params, wait_for_completion, timeout
            )
        else:
            # Use existing voice profile with unified endpoint
            return self._generate_with_voice_id(
                voice_id, text, language, speed, audio_format,
                generation_params, wait_for_completion, timeout
            )
            
    def _generate_with_voice_file(
        self,
        voice_file: str,
        text: str,
        language: Optional[str],
        speed: float,
        audio_format: str,
        generation_params: Optional[Dict[str, Any]],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, Dict[str, Any]]:
        """Generate speech with voice cloning using unified endpoint"""
        # For voice cloning, we use the "clone" identifier with the unified endpoint
        files = self._prepare_file_upload(voice_file, "file")
        
        # Prepare form data for unified endpoint
        data = {
            "input_text": text,
            "speed": speed,
            "audio_format": audio_format
        }
        if language:
            data["language"] = language
        if generation_params:
            # Add generation parameters
            data.update(generation_params)
            
        if self.async_mode:
            return self._async_generate_voice("clone", data, files, wait_for_completion, timeout)
        else:
            # Use unified voice generation endpoint with "clone" identifier
            response = self.client.request(
                "POST", 
                "/api/v1/voice/voices/clone/generate",
                data=data,
                files=files
            )
            
            job = Job.from_dict(response)
            
            if wait_for_completion:
                job = self._wait_for_completion(job.id, timeout)
                return job.result if job.result else job
            
            return job
            
    def _generate_with_voice_id(
        self,
        voice_id: Union[int, str],
        text: str,
        language: Optional[str],
        speed: float,
        audio_format: str,
        generation_params: Optional[Dict[str, Any]],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, Dict[str, Any]]:
        """Generate speech with existing voice profile using unified endpoint"""
        # Prepare form data for unified endpoint
        data = {
            "input_text": text,
            "speed": speed,
            "audio_format": audio_format
        }
        if language:
            data["language"] = language
        if generation_params:
            # Add generation parameters
            data.update(generation_params)
            
        if self.async_mode:
            return self._async_generate_voice(voice_id, data, None, wait_for_completion, timeout)
        else:
            # Use unified voice generation endpoint
            response = self.client.request(
                "POST", 
                f"/api/v1/voice/voices/{voice_id}/generate",
                data=data
            )
            
            job = Job.from_dict(response)
            
            if wait_for_completion:
                job = self._wait_for_completion(job.id, timeout)
                return job.result if job.result else job
            
            return job
            
    async def _async_generate_voice(
        self,
        voice_identifier: Union[int, str],
        data: Dict[str, Any],
        files: Optional[Dict[str, Any]],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, Dict[str, Any]]:
        """Async version of unified voice generation"""
        response = await self.client.request(
            "POST", 
            f"/api/v1/voice/voices/{voice_identifier}/generate",
            data=data,
            files=files
        )
        
        job = Job.from_dict(response)
        
        if wait_for_completion:
            job = await self._async_wait_for_completion(job.id, timeout)
            return job.result if job.result else job
        
        return job
        
    def create_voice_profile(
        self,
        name: str,
        voice_file: str,
        description: Optional[str] = None,
        is_public: bool = False,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, VoiceProfile]:
        """
        Create a reusable voice profile
        
        Args:
            name: Name for the voice profile
            voice_file: Path to audio file containing voice sample
            description: Optional description
            is_public: Whether to make the voice profile public
            wait_for_completion: Whether to wait for processing completion
            timeout: Maximum time to wait if wait_for_completion=True
            
        Returns:
            Job object if wait_for_completion=False, otherwise VoiceProfile
        """
        # Validate inputs
        if not name or len(name.strip()) < 1:
            raise ValidationError("Voice profile name cannot be empty")
        if len(name) > 100:
            raise ValidationError("Voice profile name too long (max 100 characters)")
            
        # Prepare file upload
        files = self._prepare_file_upload(voice_file, "file")
        
        # Prepare form data
        data = {
            "name": name.strip(),
            "is_public": is_public
        }
        if description:
            data["description"] = description.strip()
            
        # Make request
        if self.async_mode:
            return self._async_create_voice_profile(files, data, wait_for_completion, timeout)
        else:
            response = self.client.request(
                "POST",
                "/api/v1/voice/voice-profiles",
                data=data,
                files=files
            )
            
            if wait_for_completion:
                voice_id = response["id"]
                # Poll for completion
                import time
                start_time = time.time()
                while time.time() - start_time < timeout:
                    voice_data = self.client.request("GET", f"/api/v1/voice/voice-profiles/{voice_id}")
                    if voice_data["status"] == "completed":
                        return VoiceProfile.from_dict(voice_data)
                    elif voice_data["status"] == "failed":
                        raise ValidationError(f"Voice profile creation failed: {voice_data.get('error_message')}")
                    time.sleep(5)
                raise ValidationError("Voice profile creation timed out")
            else:
                return VoiceProfile.from_dict(response)
                
    async def _async_create_voice_profile(
        self,
        files: Dict[str, Any],
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, VoiceProfile]:
        """Async version of create_voice_profile"""
        import asyncio
        
        response = await self.client.request(
            "POST",
            "/api/v1/voice/voice-profiles",
            data=data,
            files=files
        )
        
        if wait_for_completion:
            voice_id = response["id"]
            # Poll for completion
            start_time = time.time()
            while time.time() - start_time < timeout:
                voice_data = await self.client.request("GET", f"/api/v1/voice/voice-profiles/{voice_id}")
                if voice_data["status"] == "completed":
                    return VoiceProfile.from_dict(voice_data)
                elif voice_data["status"] == "failed":
                    raise ValidationError(f"Voice profile creation failed: {voice_data.get('error_message')}")
                await asyncio.sleep(5)
            raise ValidationError("Voice profile creation timed out")
        else:
            return VoiceProfile.from_dict(response)
            
    def generate_speech(
        self,
        voice_id: Union[int, str],
        text: str,
        language: Optional[str] = None,
        speed: float = 1.0,
        audio_format: str = "mp3",
        generation_params: Optional[Dict[str, Any]] = None,
        wait_for_completion: bool = False,
        timeout: int = 300
    ) -> Union[Job, Dict[str, Any]]:
        """
        Generate speech using an existing voice profile (unified endpoint)
        
        This method now uses the unified voice generation endpoint for consistency.
        
        Args:
            voice_id: ID or UUID of the voice profile
            text: Text to generate speech for
            language: Target language code
            speed: Speech speed (0.25 to 4.0, provider dependent)
            audio_format: Output audio format ('mp3', 'wav', 'ogg')
            generation_params: Additional generation parameters
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or generation result
        """
        # Use unified voice generation method
        return self.generate_voice(
            text=text,
            voice_id=voice_id,
            language=language,
            speed=speed,
            audio_format=audio_format,
            generation_params=generation_params,
            wait_for_completion=wait_for_completion,
            timeout=timeout
        )
    
    def clone_voice(
        self,
        voice_file: str,
        text: str,
        language: Optional[str] = None,
        speed: float = 1.0,
        generation_params: Optional[Dict[str, Any]] = None,
        wait_for_completion: bool = False,
        timeout: int = 300
    ) -> Union[Job, Dict[str, Any]]:
        """
        Clone a voice from an audio file (backward compatibility)
        
        This method is now a wrapper around the unified generate_voice method.
        For new code, consider using generate_voice() directly with voice_file parameter.
        
        Args:
            voice_file: Path to audio file containing voice to clone
            text: Text to generate with the cloned voice
            language: Target language code (e.g., 'en', 'es')
            speed: Speech speed (0.25 to 4.0, provider dependent)
            generation_params: Additional generation parameters
            wait_for_completion: Whether to wait for job completion
            timeout: Maximum time to wait if wait_for_completion=True
            
        Returns:
            Job object if wait_for_completion=False, otherwise job result
        """
        # Use unified voice generation method
        return self.generate_voice(
            text=text,
            voice_file=voice_file,
            language=language,
            speed=speed,
            audio_format="mp3",  # Default format for backward compatibility
            generation_params=generation_params,
            wait_for_completion=wait_for_completion,
            timeout=timeout
        )
            
    def list_voice_profiles(
        self,
        voice_type: Optional[str] = None,
        is_public: Optional[bool] = None,
        include_public: bool = True,
        limit: int = 50
    ) -> List[VoiceProfile]:
        """
        List available voice profiles
        
        Args:
            voice_type: Filter by voice type ('custom', 'standard')
            is_public: Filter by public status
            include_public: Include public voices
            limit: Maximum number of results
            
        Returns:
            List of voice profiles
        """
        params = {
            "limit": limit,
            "include_public": include_public
        }
        if voice_type:
            params["voice_type"] = voice_type
        if is_public is not None:
            params["is_public"] = is_public
            
        if self.async_mode:
            return self._async_list_voice_profiles(params)
        else:
            response = self.client.request("GET", "/api/v1/voice/voice-profiles", params=params)
            return [VoiceProfile.from_dict(voice_data) for voice_data in response]
            
    async def _async_list_voice_profiles(self, params: Dict[str, Any]) -> List[VoiceProfile]:
        """Async version of list_voice_profiles"""
        response = await self.client.request("GET", "/api/v1/voice/voice-profiles", params=params)
        return [VoiceProfile.from_dict(voice_data) for voice_data in response]
        
    def get_voice_profile(self, voice_id: Union[int, str]) -> VoiceProfile:
        """
        Get details of a specific voice profile
        
        Args:
            voice_id: ID or UUID of the voice profile
            
        Returns:
            Voice profile details
        """
        if self.async_mode:
            return self._async_get_voice_profile(voice_id)
        else:
            response = self.client.request("GET", f"/api/v1/voice/voice-profiles/{voice_id}")
            return VoiceProfile.from_dict(response)
            
    async def _async_get_voice_profile(self, voice_id: Union[int, str]) -> VoiceProfile:
        """Async version of get_voice_profile"""
        response = await self.client.request("GET", f"/api/v1/voice/voice-profiles/{voice_id}")
        return VoiceProfile.from_dict(response)
        
    def delete_voice_profile(self, voice_id: Union[int, str]) -> Dict[str, str]:
        """
        Delete a voice profile
        
        Args:
            voice_id: ID or UUID of the voice profile
            
        Returns:
            Deletion confirmation
        """
        if self.async_mode:
            return self._async_delete_voice_profile(voice_id)
        else:
            return self.client.request("DELETE", f"/api/v1/voice/voices/{voice_id}")
            
    async def _async_delete_voice_profile(self, voice_id: Union[int, str]) -> Dict[str, str]:
        """Async version of delete_voice_profile"""
        return await self.client.request("DELETE", f"/api/v1/voice/voices/{voice_id}")
        
    def get_job_status(self, job_id: int) -> Job:
        """
        Get status of a voice processing job
        
        Args:
            job_id: ID of the job
            
        Returns:
            Job status and details
        """
        if self.async_mode:
            return self._async_get_job_status(job_id)
        else:
            response = self.client.request("GET", f"/api/v1/voice/clone/{job_id}/status")
            return Job.from_dict(response)
            
    async def _async_get_job_status(self, job_id: int) -> Job:
        """Async version of get_job_status"""
        response = await self.client.request("GET", f"/api/v1/voice/clone/{job_id}/status")
        return Job.from_dict(response)
