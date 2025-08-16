"""
Translation Service - Speech-to-speech translation operations
"""

from typing import Optional, Union
from .base import BaseService
from ..models import Job, TranslationResult
from ..exceptions import ValidationError


class TranslationService(BaseService):
    """Service for speech-to-speech translation operations"""
    
    def translate_audio(
        self,
        audio_file: Optional[str] = None,
        url: Optional[str] = None,
        target_language: str = "en",
        source_language: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 900
    ) -> Union[Job, TranslationResult]:
        """
        Translate speech from audio/video file to another language while preserving voice characteristics
        
        Args:
            audio_file: Path to audio/video file (required if no URL)
            url: Direct media URL (required if no file)
            target_language: Target language code (ISO 639-1, e.g., 'es' for Spanish)
            source_language: Source language code (auto-detect if None)
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or translation result
        """
        if not audio_file and not url:
            raise ValidationError("Either audio_file or url must be provided")
        
        if audio_file and url:
            raise ValidationError("Provide either audio_file or url, not both")
            
        target_language = self._validate_language_code(target_language)
        if source_language:
            source_language = self._validate_language_code(source_language)
            
        # Prepare request data
        files = {}
        data = {"target_language": target_language}
        
        if audio_file:
            files = self._prepare_file_upload(audio_file, "file")
        
        if url:
            data["url"] = url
            
        if source_language:
            data["source_language"] = source_language
            
        if self.async_mode:
            return self._async_translate_audio(files, data, wait_for_completion, timeout)
        else:
            response = self.client.request(
                "POST", 
                "/api/v1/translation/translate/speech",  # FIXED: Use correct speech-to-speech endpoint
                data=data, 
                files=files if files else None
            )
            job = Job.from_dict(response)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return TranslationResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
    
    def translate_speech(
        self,
        audio_file: Optional[str] = None,
        url: Optional[str] = None,
        target_language: str = "en",
        source_language: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 900
    ) -> Union[Job, TranslationResult]:
        """
        Alias for translate_audio - more descriptive method name for speech translation
        """
        return self.translate_audio(
            audio_file=audio_file,
            url=url,
            target_language=target_language,
            source_language=source_language,
            wait_for_completion=wait_for_completion,
            timeout=timeout
        )
            
    async def _async_translate_audio(self, files, data, wait_for_completion, timeout):
        """Async version of translate_audio"""
        response = await self.client.request(
            "POST", 
            "/api/v1/translation/translate/speech",  # FIXED: Use correct speech-to-speech endpoint
            data=data, 
            files=files if files else None
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
    
    def list_translation_jobs(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> list:
        """
        List translation jobs
        
        Args:
            skip: Number of jobs to skip (pagination offset)
            limit: Maximum number of jobs to return (max 100)
            
        Returns:
            List of translation jobs
        """
        params = {
            "skip": skip,
            "limit": min(limit, 100)  # API max is 100
        }
        
        if self.async_mode:
            return self._async_list_translation_jobs(params)
        else:
            response = self.client.request("GET", "/api/v1/translation/translations", params=params)
            return [TranslationResult.from_dict(job_data) for job_data in response]
    
    async def _async_list_translation_jobs(self, params: dict) -> list:
        """Async version of list_translation_jobs"""
        response = await self.client.request("GET", "/api/v1/translation/translations", params=params)
        return [TranslationResult.from_dict(job_data) for job_data in response]
    
    def retry_translation(self, job_id: int) -> Job:
        """
        Retry a failed translation job
        
        Args:
            job_id: ID of the failed translation job to retry
            
        Returns:
            New job object for the retry attempt
        """
        if self.async_mode:
            return self._async_retry_translation(job_id)
        else:
            response = self.client.request("POST", f"/api/v1/translation/translations/{job_id}/retry")
            return Job.from_dict(response)
    
    async def _async_retry_translation(self, job_id: int) -> Job:
        """Async version of retry_translation"""
        response = await self.client.request("POST", f"/api/v1/translation/translations/{job_id}/retry")
        return Job.from_dict(response)
    
    def delete_translation_job(self, job_id: int) -> dict:
        """
        Delete a translation job
        
        Args:
            job_id: ID of the translation job to delete
            
        Returns:
            Deletion confirmation
        """
        if self.async_mode:
            return self._async_delete_translation_job(job_id)
        else:
            return self.client.request("DELETE", f"/api/v1/translation/translations/{job_id}")
    
    async def _async_delete_translation_job(self, job_id: int) -> dict:
        """Async version of delete_translation_job"""
        return await self.client.request("DELETE", f"/api/v1/translation/translations/{job_id}")
