"""
Translation Service - Audio/video translation operations
"""

from typing import Optional, Union
from .base import BaseService
from ..models import Job, TranslationResult


class TranslationService(BaseService):
    """Service for audio and video translation operations"""
    
    def translate_audio(
        self,
        audio_file: str,
        target_language: str,
        source_language: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 900
    ) -> Union[Job, TranslationResult]:
        """
        Translate audio to another language
        
        Args:
            audio_file: Path to audio file
            target_language: Target language code
            source_language: Source language (auto-detect if None)
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or translation result
        """
        target_language = self._validate_language_code(target_language)
        if source_language:
            source_language = self._validate_language_code(source_language)
            
        files = self._prepare_file_upload(audio_file, "file")
        data = {"target_language": target_language}
        if source_language:
            data["source_language"] = source_language
            
        if self.async_mode:
            return self._async_translate_audio(files, data, wait_for_completion, timeout)
        else:
            response = self.client.request(
                "POST", "/api/v1/translation/translate", data=data, files=files
            )
            job = Job.from_dict(response)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return TranslationResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_translate_audio(self, files, data, wait_for_completion, timeout):
        """Async version of translate_audio"""
        response = await self.client.request(
            "POST", "/api/v1/translation/translate", data=data, files=files
        )
        job = Job.from_dict(response)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return TranslationResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
        
    def get_translation_job(self, job_id: int) -> TranslationResult:
        """Get translation job details"""
        if self.async_mode:
            return self._async_get_translation_job(job_id)
        else:
            response = self.client.request("GET", f"/api/v1/translation/translations/{job_id}")
            return TranslationResult.from_dict(response)
            
    async def _async_get_translation_job(self, job_id: int) -> TranslationResult:
        """Async version of get_translation_job"""
        response = await self.client.request("GET", f"/api/v1/translation/translations/{job_id}")
        return TranslationResult.from_dict(response)
