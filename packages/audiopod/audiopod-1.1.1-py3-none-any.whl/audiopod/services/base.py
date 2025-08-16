"""
Base service class for AudioPod API services
"""

import os
import time
from typing import TYPE_CHECKING, Optional, Dict, Any, Union, BinaryIO
from pathlib import Path

from ..exceptions import ValidationError, FileError, ProcessingError
from ..models import Job, JobStatus

if TYPE_CHECKING:
    from ..client import Client, AsyncClient


class BaseService:
    """Base class for all AudioPod API services"""
    
    def __init__(self, client: Union["Client", "AsyncClient"], async_mode: bool = False):
        self.client = client
        self.async_mode = async_mode
        
    def _validate_file(self, file_path: str, file_type: str = "audio") -> str:
        """
        Validate file exists and format is supported
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('audio' or 'video')
            
        Returns:
            Absolute path to the file
            
        Raises:
            FileError: If file doesn't exist or format not supported
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileError(f"File not found: {file_path}")
            
        if not self.client.config.validate_file_format(path.name, file_type):
            supported_formats = (
                self.client.config.supported_audio_formats 
                if file_type == "audio" 
                else self.client.config.supported_video_formats
            )
            raise FileError(
                f"Unsupported {file_type} format. "
                f"Supported formats: {', '.join(supported_formats)}"
            )
            
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.client.config.max_file_size_mb:
            raise FileError(
                f"File too large: {file_size_mb:.1f}MB. "
                f"Maximum size: {self.client.config.max_file_size_mb}MB"
            )
            
        return str(path.absolute())
        
    def _prepare_file_upload(self, file_path: str, field_name: str = "file") -> Dict[str, Any]:
        """
        Prepare file for upload
        
        Args:
            file_path: Path to the file
            field_name: Form field name for the file
            
        Returns:
            Files dict for requests
        """
        validated_path = self._validate_file(file_path)
        
        with open(validated_path, 'rb') as f:
            return {field_name: (Path(validated_path).name, f.read())}
            
    def _wait_for_completion(
        self, 
        job_id: int, 
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Job:
        """
        Wait for job completion with polling
        
        Args:
            job_id: Job ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds
            
        Returns:
            Completed job
            
        Raises:
            ProcessingError: If job fails or times out
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job_data = self.client.request("GET", f"/api/v1/jobs/{job_id}")
            job = Job.from_dict(job_data)
            
            if job.status == JobStatus.COMPLETED:
                return job
            elif job.status == JobStatus.FAILED:
                raise ProcessingError(
                    f"Job {job_id} failed: {job.error_message}",
                    job_id=str(job_id)
                )
            elif job.status == JobStatus.CANCELLED:
                raise ProcessingError(
                    f"Job {job_id} was cancelled",
                    job_id=str(job_id)
                )
                
            time.sleep(poll_interval)
            
        raise ProcessingError(
            f"Job {job_id} timed out after {timeout} seconds",
            job_id=str(job_id)
        )
        
    async def _async_wait_for_completion(
        self,
        job_id: int,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Job:
        """
        Async version of wait_for_completion
        
        Args:
            job_id: Job ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds
            
        Returns:
            Completed job
            
        Raises:
            ProcessingError: If job fails or times out
        """
        import asyncio
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job_data = await self.client.request("GET", f"/api/v1/jobs/{job_id}")
            job = Job.from_dict(job_data)
            
            if job.status == JobStatus.COMPLETED:
                return job
            elif job.status == JobStatus.FAILED:
                raise ProcessingError(
                    f"Job {job_id} failed: {job.error_message}",
                    job_id=str(job_id)
                )
            elif job.status == JobStatus.CANCELLED:
                raise ProcessingError(
                    f"Job {job_id} was cancelled",
                    job_id=str(job_id)
                )
                
            await asyncio.sleep(poll_interval)
            
        raise ProcessingError(
            f"Job {job_id} timed out after {timeout} seconds",
            job_id=str(job_id)
        )
        
    def _validate_language_code(self, language: str) -> str:
        """
        Validate language code format
        
        Args:
            language: Language code to validate
            
        Returns:
            Validated language code
            
        Raises:
            ValidationError: If language code is invalid
        """
        if not language or len(language) < 2:
            raise ValidationError("Language code must be at least 2 characters")
            
        # Convert to lowercase for consistency
        return language.lower()
        
    def _validate_text_input(self, text: str, max_length: int = 5000) -> str:
        """
        Validate text input
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            
        Returns:
            Validated text
            
        Raises:
            ValidationError: If text is invalid
        """
        if not text or not text.strip():
            raise ValidationError("Text input cannot be empty")
            
        if len(text) > max_length:
            raise ValidationError(f"Text too long. Maximum length: {max_length} characters")
            
        return text.strip()
