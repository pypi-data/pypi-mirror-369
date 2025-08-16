"""
Karaoke Service - Karaoke video generation
"""

from typing import Optional, Union
from .base import BaseService
from ..models import Job


class KaraokeService(BaseService):
    """Service for karaoke video generation"""
    
    def generate_karaoke(
        self,
        audio_file: Optional[str] = None,
        youtube_url: Optional[str] = None,
        custom_lyrics: Optional[str] = None,
        video_style: str = "modern",
        wait_for_completion: bool = False,
        timeout: int = 1200
    ) -> Job:
        """Generate karaoke video"""
        if not audio_file and not youtube_url:
            raise ValueError("Either audio_file or youtube_url must be provided")
            
        data = {"video_style": video_style}
        files = {}
        
        if audio_file:
            files = self._prepare_file_upload(audio_file, "file")
        if youtube_url:
            data["youtube_url"] = youtube_url
        if custom_lyrics:
            data["custom_lyrics"] = custom_lyrics
            
        if self.async_mode:
            return self._async_generate_karaoke(files, data, wait_for_completion, timeout)
        else:
            response = self.client.request(
                "POST", "/api/v1/karaoke/generate",
                data=data, files=files if files else None
            )
            job = Job.from_dict(response)
            
            if wait_for_completion:
                return self._wait_for_completion(job.id, timeout)
                
            return job
            
    async def _async_generate_karaoke(self, files, data, wait_for_completion, timeout):
        """Async version of generate_karaoke"""
        response = await self.client.request(
            "POST", "/api/v1/karaoke/generate",
            data=data, files=files if files else None
        )
        job = Job.from_dict(response)
        
        if wait_for_completion:
            return await self._async_wait_for_completion(job.id, timeout)
            
        return job
