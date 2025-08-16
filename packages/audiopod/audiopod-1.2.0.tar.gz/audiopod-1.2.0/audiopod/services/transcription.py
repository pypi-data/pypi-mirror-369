"""
Transcription Service - Speech-to-text operations
"""

from typing import List, Optional, Dict, Any, Union

from .base import BaseService
from ..models import Job, TranscriptionResult
from ..exceptions import ValidationError


class TranscriptionService(BaseService):
    """Service for audio transcription operations"""
    
    def transcribe_audio(
        self,
        audio_file: str,
        language: Optional[str] = None,
        model_type: str = "whisperx",
        enable_speaker_diarization: bool = False,
        enable_word_timestamps: bool = True,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, TranscriptionResult]:
        """
        Transcribe audio to text
        
        Args:
            audio_file: Path to audio file
            language: Language code (auto-detect if None)
            model_type: Model to use ('whisperx', 'faster-whisper')
            enable_speaker_diarization: Enable speaker identification
            enable_word_timestamps: Include word-level timestamps
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or transcription result
        """
        # Validate inputs
        if language:
            language = self._validate_language_code(language)
        if model_type not in ["whisperx", "faster-whisper"]:
            raise ValidationError("Model type must be 'whisperx' or 'faster-whisper'")
            
        # Prepare file upload
        files = self._prepare_file_upload(audio_file, "files")
        
        # Prepare form data
        data = {
            "model_type": model_type,
            "enable_speaker_diarization": enable_speaker_diarization,
            "enable_word_timestamps": enable_word_timestamps
        }
        if language:
            data["language"] = language
            
        # Make request
        if self.async_mode:
            return self._async_transcribe_audio(files, data, wait_for_completion, timeout)
        else:
            response = self.client.request(
                "POST",
                "/api/v1/transcription/transcribe-upload",
                data=data,
                files=files
            )
            
            job = Job.from_dict(response)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return TranscriptionResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_transcribe_audio(
        self,
        files: Dict[str, Any],
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, TranscriptionResult]:
        """Async version of transcribe_audio"""
        response = await self.client.request(
            "POST",
            "/api/v1/transcription/transcribe-upload",
            data=data,
            files=files
        )
        
        job = Job.from_dict(response)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return TranscriptionResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
        
    def transcribe_url(
        self,
        url: str,
        language: Optional[str] = None,
        model_type: str = "whisperx",
        enable_speaker_diarization: bool = False,
        wait_for_completion: bool = False,
        timeout: int = 600
    ) -> Union[Job, TranscriptionResult]:
        """
        Transcribe audio from URL (YouTube, etc.)
        
        Args:
            url: URL to audio/video content
            language: Language code
            model_type: Model to use
            enable_speaker_diarization: Enable speaker identification
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object or transcription result
        """
        if language:
            language = self._validate_language_code(language)
            
        data = {
            "source_urls": [url],
            "model_type": model_type,
            "enable_speaker_diarization": enable_speaker_diarization
        }
        if language:
            data["language"] = language
            
        if self.async_mode:
            return self._async_transcribe_url(data, wait_for_completion, timeout)
        else:
            response = self.client.request("POST", "/api/v1/transcription/transcribe", data=data)
            job = Job.from_dict(response)
            
            if wait_for_completion:
                completed_job = self._wait_for_completion(job.id, timeout)
                return TranscriptionResult.from_dict(completed_job.result or completed_job.__dict__)
                
            return job
            
    async def _async_transcribe_url(
        self,
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Union[Job, TranscriptionResult]:
        """Async version of transcribe_url"""
        response = await self.client.request("POST", "/api/v1/transcription/transcribe", data=data)
        job = Job.from_dict(response)
        
        if wait_for_completion:
            completed_job = await self._async_wait_for_completion(job.id, timeout)
            return TranscriptionResult.from_dict(completed_job.result or completed_job.__dict__)
            
        return job
        
    def get_transcription_job(self, job_id: int) -> TranscriptionResult:
        """Get transcription job details"""
        if self.async_mode:
            return self._async_get_transcription_job(job_id)
        else:
            response = self.client.request("GET", f"/api/v1/transcription/jobs/{job_id}")
            return TranscriptionResult.from_dict(response)
            
    async def _async_get_transcription_job(self, job_id: int) -> TranscriptionResult:
        """Async version of get_transcription_job"""
        response = await self.client.request("GET", f"/api/v1/transcription/jobs/{job_id}")
        return TranscriptionResult.from_dict(response)
        
    def download_transcript(
        self,
        job_id: int,
        format: str = "json"
    ) -> str:
        """
        Download transcript in specified format
        
        Args:
            job_id: Transcription job ID
            format: Output format ('json', 'txt', 'srt', 'vtt', 'pdf')
            
        Returns:
            Transcript content
        """
        if format not in ["json", "txt", "srt", "vtt", "pdf", "docx", "html"]:
            raise ValidationError("Format must be one of: json, txt, srt, vtt, pdf, docx, html")
            
        params = {"format": format}
        
        if self.async_mode:
            return self._async_download_transcript(job_id, params)
        else:
            response = self.client.request(
                "GET", 
                f"/api/v1/transcription/jobs/{job_id}/transcript",
                params=params
            )
            return response
            
    async def _async_download_transcript(self, job_id: int, params: Dict[str, str]) -> str:
        """Async version of download_transcript"""
        response = await self.client.request(
            "GET",
            f"/api/v1/transcription/jobs/{job_id}/transcript", 
            params=params
        )
        return response
