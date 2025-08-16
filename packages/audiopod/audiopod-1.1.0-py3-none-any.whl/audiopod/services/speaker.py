"""
Speaker Service - Speaker analysis and diarization
"""

from typing import Optional, Union
from .base import BaseService
from ..models import Job, SpeakerAnalysisResult


class SpeakerService(BaseService):
    """Service for speaker diarization and analysis"""
    
    def diarize_speakers(
        self,
        audio_file: str,
        num_speakers: Optional[int] = None,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, SpeakerAnalysisResult]:
        """Identify and separate speakers in audio"""
        files = self._prepare_file_upload(audio_file, "file")
        data = {}
        if num_speakers:
            data["num_speakers"] = num_speakers
            
        if self.async_mode:
            return self._async_diarize(files, data, wait_for_completion, timeout)
        else:
            response = self.client.request(
                "POST", "/api/v1/speaker/diarize", 
                data=data, files=files
            )
            job = Job.from_dict(response)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return SpeakerAnalysisResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_diarize(self, files, data, wait_for_completion, timeout):
        """Async version of diarize_speakers"""
        response = await self.client.request(
            "POST", "/api/v1/speaker/diarize",
            data=data, files=files
        )
        job = Job.from_dict(response)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return SpeakerAnalysisResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
