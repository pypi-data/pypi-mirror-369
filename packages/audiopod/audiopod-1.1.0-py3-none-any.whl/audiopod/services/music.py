"""
Music Service - Music generation operations
"""

from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from .base import BaseService
from ..models import Job, MusicGenerationResult
from ..exceptions import ValidationError


class MusicService(BaseService):
    """Service for music generation operations"""
    
    def generate_music(
        self,
        prompt: str,
        duration: float = 120.0,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50,
        seed: Optional[int] = None,
        display_name: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, MusicGenerationResult]:
        """
        Generate music from text prompt
        
        Args:
            prompt: Text description of the music to generate
            duration: Duration in seconds (10-600)
            guidance_scale: How closely to follow the prompt (1.0-20.0)
            num_inference_steps: Number of denoising steps (20-100)
            seed: Random seed for reproducible results
            display_name: Custom name for the generated track
            wait_for_completion: Whether to wait for generation completion
            timeout: Maximum time to wait if wait_for_completion=True
            
        Returns:
            Job object if wait_for_completion=False, otherwise MusicGenerationResult
        """
        # Validate inputs
        prompt = self._validate_text_input(prompt, max_length=1000)
        if not 10.0 <= duration <= 600.0:
            raise ValidationError("Duration must be between 10 and 600 seconds")
        if not 1.0 <= guidance_scale <= 20.0:
            raise ValidationError("Guidance scale must be between 1.0 and 20.0")
        if not 20 <= num_inference_steps <= 100:
            raise ValidationError("Inference steps must be between 20 and 100")
        if seed is not None and (seed < 0 or seed > 2**32 - 1):
            raise ValidationError("Seed must be between 0 and 2^32 - 1")
            
        # Prepare request data - FIXED: Use correct parameter names matching API schema
        data = {
            "prompt": prompt,
            "audio_duration": duration,  # FIXED: API expects "audio_duration" not "duration"
            "guidance_scale": guidance_scale,
            "infer_step": num_inference_steps  # FIXED: API expects "infer_step" not "num_inference_steps"
        }
        if seed is not None:
            data["manual_seeds"] = [seed]  # FIXED: API expects "manual_seeds" list not "seed"
        if display_name:
            data["display_name"] = display_name.strip()
            
        # Make request
        if self.async_mode:
            return self._async_generate_music(data, wait_for_completion, timeout)
        else:
            response = self.client.request("POST", "/api/v1/music/text2music", data=data)
            # FIXED: Handle response format correctly - API returns {"job": {...}, "message": "..."}
            job_data = response.get("job", response)
            job = Job.from_dict(job_data)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_generate_music(
        self,
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, MusicGenerationResult]:
        """Async version of generate_music"""
        response = await self.client.request("POST", "/api/v1/music/text2music", data=data)
        # FIXED: Handle response format correctly
        job_data = response.get("job", response)
        job = Job.from_dict(job_data)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
        
    def generate_rap(
        self,
        lyrics: str,
        style: str = "modern",
        tempo: int = 120,
        display_name: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, MusicGenerationResult]:
        """
        Generate rap music with lyrics
        
        Args:
            lyrics: Rap lyrics
            style: Style of rap ('modern', 'classic', 'trap')
            tempo: Beats per minute (80-200)
            display_name: Custom name for the track
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or generation result
        """
        # Validate inputs
        lyrics = self._validate_text_input(lyrics, max_length=2000)
        if not 80 <= tempo <= 200:
            raise ValidationError("Tempo must be between 80 and 200 BPM")
        if style not in ["modern", "classic", "trap"]:
            raise ValidationError("Style must be 'modern', 'classic', or 'trap'")
            
        # Prepare request data - FIXED: Match API schema for text2rap
        data = {
            "prompt": f"rap music, {style} style",  # FIXED: API expects "prompt" field
            "lyrics": lyrics,
            "audio_duration": 120.0,  # Default duration
            "guidance_scale": 7.5,
            "infer_step": 50,
            "lora_name_or_path": "ACE-Step/ACE-Step-v1-chinese-rap-LoRA"  # Rap-specific LoRA
        }
        if display_name:
            data["display_name"] = display_name.strip()
            
        # Make request
        if self.async_mode:
            return self._async_generate_rap(data, wait_for_completion, timeout)
        else:
            response = self.client.request("POST", "/api/v1/music/text2rap", data=data)
            # FIXED: Handle response format correctly
            job_data = response.get("job", response)
            job = Job.from_dict(job_data)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_generate_rap(
        self,
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, MusicGenerationResult]:
        """Async version of generate_rap"""
        response = await self.client.request("POST", "/api/v1/music/text2rap", data=data)
        # FIXED: Handle response format correctly
        job_data = response.get("job", response)
        job = Job.from_dict(job_data)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
        
    def generate_instrumental(
        self,
        prompt: str,
        duration: float = 120.0,
        instruments: Optional[List[str]] = None,
        key: Optional[str] = None,
        tempo: Optional[int] = None,
        display_name: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, MusicGenerationResult]:
        """
        Generate instrumental music
        
        Args:
            prompt: Description of the instrumental
            duration: Duration in seconds
            instruments: List of instruments to include
            key: Musical key (e.g., 'C', 'Am', 'F#')
            tempo: Beats per minute
            display_name: Custom name for the track
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or generation result
        """
        # Validate inputs
        prompt = self._validate_text_input(prompt, max_length=1000)
        if not 10.0 <= duration <= 600.0:
            raise ValidationError("Duration must be between 10 and 600 seconds")
        if tempo is not None and not 60 <= tempo <= 200:
            raise ValidationError("Tempo must be between 60 and 200 BPM")
            
        # Prepare request data - FIXED: Match API schema for prompt2instrumental
        data = {
            "prompt": prompt,
            "audio_duration": duration,  # FIXED: API expects "audio_duration"
            "guidance_scale": 7.5,
            "infer_step": 50
        }
        if instruments:
            data["instruments"] = instruments
        if key:
            data["key"] = key
        if tempo:
            data["tempo"] = tempo
        if display_name:
            data["display_name"] = display_name.strip()
            
        # Make request
        if self.async_mode:
            return self._async_generate_instrumental(data, wait_for_completion, timeout)
        else:
            response = self.client.request("POST", "/api/v1/music/prompt2instrumental", data=data)
            # FIXED: Handle response format correctly
            job_data = response.get("job", response)
            job = Job.from_dict(job_data)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_generate_instrumental(
        self,
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, MusicGenerationResult]:
        """Async version of generate_instrumental"""
        response = await self.client.request("POST", "/api/v1/music/prompt2instrumental", data=data)
        # FIXED: Handle response format correctly
        job_data = response.get("job", response)
        job = Job.from_dict(job_data)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
    
    def generate_vocals(
        self,
        lyrics: str,
        prompt: str = "vocals",
        duration: float = 120.0,
        display_name: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, MusicGenerationResult]:
        """
        Generate vocals from lyrics - NEW METHOD matching API lyric2vocals endpoint
        
        Args:
            lyrics: Song lyrics
            prompt: Vocal style description
            duration: Duration in seconds
            display_name: Custom name for the track
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or generation result
        """
        # Validate inputs
        lyrics = self._validate_text_input(lyrics, max_length=10000)
        prompt = self._validate_text_input(prompt, max_length=2000)
        if not 10.0 <= duration <= 600.0:
            raise ValidationError("Duration must be between 10 and 600 seconds")
            
        # Prepare request data - Match API schema for lyric2vocals
        data = {
            "prompt": prompt,
            "lyrics": lyrics,
            "audio_duration": duration,
            "guidance_scale": 7.5,
            "infer_step": 50
        }
        if display_name:
            data["display_name"] = display_name.strip()
            
        # Make request
        if self.async_mode:
            return self._async_generate_vocals(data, wait_for_completion, timeout)
        else:
            response = self.client.request("POST", "/api/v1/music/lyric2vocals", data=data)
            job_data = response.get("job", response)
            job = Job.from_dict(job_data)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
    
    async def _async_generate_vocals(
        self,
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, MusicGenerationResult]:
        """Async version of generate_vocals"""
        response = await self.client.request("POST", "/api/v1/music/lyric2vocals", data=data)
        job_data = response.get("job", response)
        job = Job.from_dict(job_data)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
        
    def extend_music(
        self,
        source_job_id: int,
        extend_duration: float = 30.0,
        display_name: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, MusicGenerationResult]:
        """
        Extend an existing music track
        
        Args:
            source_job_id: ID of the original music generation job
            extend_duration: How many seconds to extend
            display_name: Custom name for the extended track
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or generation result
        """
        # Validate inputs
        if not 5.0 <= extend_duration <= 120.0:
            raise ValidationError("Extend duration must be between 5 and 120 seconds")
            
        # Prepare request data
        data = {
            "source_job_id": source_job_id,
            "extend_duration": extend_duration
        }
        if display_name:
            data["display_name"] = display_name.strip()
            
        # Make request
        if self.async_mode:
            return self._async_extend_music(data, wait_for_completion, timeout)
        else:
            response = self.client.request("POST", "/api/v1/music/extend", data=data)
            job = Job.from_dict(response)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_extend_music(
        self,
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, MusicGenerationResult]:
        """Async version of extend_music"""
        response = await self.client.request("POST", "/api/v1/music/extend", data=data)
        job = Job.from_dict(response)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return MusicGenerationResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
        
    def list_music_jobs(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        task: Optional[str] = None,
        liked: Optional[bool] = None
    ) -> List[MusicGenerationResult]:
        """
        List music generation jobs
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            status: Filter by job status
            task: Filter by task type
            liked: Filter by liked status
            
        Returns:
            List of music generation results
        """
        params = {
            "limit": limit,
            "skip": offset  # FIXED: API uses "skip" parameter for offset
        }
        if status:
            params["status"] = status
        if task:
            params["task"] = task
        if liked is not None:
            params["liked"] = liked
            
        if self.async_mode:
            return self._async_list_music_jobs(params)
        else:
            response = self.client.request("GET", "/api/v1/music/jobs", params=params)
            return [MusicGenerationResult.from_dict(job_data) for job_data in response]
            
    async def _async_list_music_jobs(self, params: Dict[str, Any]) -> List[MusicGenerationResult]:
        """Async version of list_music_jobs"""
        response = await self.client.request("GET", "/api/v1/music/jobs", params=params)
        return [MusicGenerationResult.from_dict(job_data) for job_data in response]
        
    def get_music_job(self, job_id: int) -> MusicGenerationResult:
        """
        Get details of a specific music generation job
        
        Args:
            job_id: ID of the music job
            
        Returns:
            Music generation result
        """
        if self.async_mode:
            return self._async_get_music_job(job_id)
        else:
            response = self.client.request("GET", f"/api/v1/music/jobs/{job_id}/status")
            return MusicGenerationResult.from_dict(response)
            
    async def _async_get_music_job(self, job_id: int) -> MusicGenerationResult:
        """Async version of get_music_job"""
        response = await self.client.request("GET", f"/api/v1/music/jobs/{job_id}/status")
        return MusicGenerationResult.from_dict(response)
        
    def like_music_track(self, job_id: int) -> Dict[str, Any]:
        """
        Like a music track
        
        Args:
            job_id: ID of the music job
            
        Returns:
            Like response
        """
        if self.async_mode:
            return self._async_like_music_track(job_id)
        else:
            return self.client.request("POST", f"/api/v1/music/jobs/{job_id}/like")
            
    async def _async_like_music_track(self, job_id: int) -> Dict[str, Any]:
        """Async version of like_music_track"""
        return await self.client.request("POST", f"/api/v1/music/jobs/{job_id}/like")
        
    def share_music_track(
        self,
        job_id: int,
        platform: Optional[str] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Share a music track
        
        Args:
            job_id: ID of the music job
            platform: Platform to share on
            message: Optional message to include
            
        Returns:
            Share response with shareable URL
        """
        data = {}
        if platform:
            data["platform"] = platform
        if message:
            data["message"] = message
            
        if self.async_mode:
            return self._async_share_music_track(job_id, data)
        else:
            return self.client.request("POST", f"/api/v1/music/jobs/{job_id}/share", data=data)
            
    async def _async_share_music_track(self, job_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Async version of share_music_track"""
        return await self.client.request("POST", f"/api/v1/music/jobs/{job_id}/share", data=data)
        
    def delete_music_job(self, job_id: int) -> Dict[str, str]:
        """
        Delete a music generation job
        
        Args:
            job_id: ID of the music job
            
        Returns:
            Deletion confirmation
        """
        if self.async_mode:
            return self._async_delete_music_job(job_id)
        else:
            return self.client.request("DELETE", f"/api/v1/music/jobs/{job_id}")
            
    async def _async_delete_music_job(self, job_id: int) -> Dict[str, str]:
        """Async version of delete_music_job"""
        return await self.client.request("DELETE", f"/api/v1/music/jobs/{job_id}")
