"""
Denoiser Service - Audio denoising operations
"""

from typing import Optional, Union
from .base import BaseService
from ..models import Job, DenoiseResult


class DenoiserService(BaseService):
    """Service for audio denoising operations"""
    
    def denoise_audio(
        self,
        audio_file: str,
        quality_mode: str = "balanced",
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, DenoiseResult]:
        """Remove noise from audio"""
        files = self._prepare_file_upload(audio_file, "file")
        data = {"quality_mode": quality_mode}
        
        if self.async_mode:
            return self._async_denoise(files, data, wait_for_completion, timeout)
        else:
            response = self.client.request(
                "POST", "/api/v1/denoiser/denoise",
                data=data, files=files
            )
            job = Job.from_dict(response)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return DenoiseResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_denoise(self, files, data, wait_for_completion, timeout):
        """Async version of denoise_audio"""
        response = await self.client.request(
            "POST", "/api/v1/denoiser/denoise",
            data=data, files=files
        )
        job = Job.from_dict(response)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return DenoiseResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
