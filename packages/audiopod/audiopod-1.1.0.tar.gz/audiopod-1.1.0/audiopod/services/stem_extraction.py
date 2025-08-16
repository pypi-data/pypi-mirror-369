"""
Stem Extraction Service - Audio stem separation operations
"""

from typing import List, Optional, Dict, Any, Union
from .base import BaseService
from ..models import Job
from ..exceptions import ValidationError


class StemExtractionService(BaseService):
    """Service for audio stem extraction operations"""
    
    def extract_stems(
        self,
        audio_file: Optional[str] = None,
        url: Optional[str] = None,
        stem_types: List[str] = None,
        model_name: str = "htdemucs",
        two_stems_mode: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: int = 900
    ) -> Job:
        """
        Extract stems from audio file
        
        Args:
            audio_file: Path to audio file to process
            url: URL of audio file to process (alternative to audio_file)
            stem_types: List of stems to extract (e.g., ['vocals', 'drums', 'bass', 'other'])
            model_name: Model to use for separation ('htdemucs' or 'htdemucs_6s')
            two_stems_mode: Two-stem mode for vocals/instrumental separation
            wait_for_completion: Whether to wait for completion
            timeout: Maximum time to wait
            
        Returns:
            Job object with stem extraction details
        """
        if not audio_file and not url:
            raise ValidationError("Either audio_file or url must be provided")
        
        if audio_file and url:
            raise ValidationError("Provide either audio_file or url, not both")
        
        # Set default stem types based on model
        if stem_types is None:
            if model_name == "htdemucs_6s":
                stem_types = ["vocals", "drums", "bass", "other", "piano", "guitar"]
            else:
                stem_types = ["vocals", "drums", "bass", "other"]
        
        # Validate model name
        if model_name not in ["htdemucs", "htdemucs_6s"]:
            raise ValidationError("Model name must be 'htdemucs' or 'htdemucs_6s'")
        
        # Prepare request
        files = {}
        data = {
            "stem_types": str(stem_types),  # API expects string representation
            "model_name": model_name
        }
        
        if audio_file:
            files = self._prepare_file_upload(audio_file, "file")
        
        if url:
            data["url"] = url
        
        if two_stems_mode:
            data["two_stems_mode"] = two_stems_mode
        
        if self.async_mode:
            return self._async_extract_stems(files, data, wait_for_completion, timeout)
        else:
            response = self.client.request(
                "POST", 
                "/api/v1/stem-extraction/extract",
                data=data,
                files=files if files else None
            )
            
            job = Job.from_dict(response)
            
            if wait_for_completion:
                return self._wait_for_completion(job.id, timeout)
            
            return job
    
    async def _async_extract_stems(
        self,
        files: Dict[str, Any],
        data: Dict[str, Any],
        wait_for_completion: bool,
        timeout: int
    ) -> Job:
        """Async version of extract_stems"""
        response = await self.client.request(
            "POST",
            "/api/v1/stem-extraction/extract",
            data=data,
            files=files if files else None
        )
        
        job = Job.from_dict(response)
        
        if wait_for_completion:
            return await self._async_wait_for_completion(job.id, timeout)
        
        return job
    
    def get_stem_job(self, job_id: int) -> Job:
        """
        Get stem extraction job status
        
        Args:
            job_id: ID of the stem extraction job
            
        Returns:
            Job object with current status
        """
        if self.async_mode:
            return self._async_get_stem_job(job_id)
        else:
            response = self.client.request("GET", f"/api/v1/stem-extraction/status/{job_id}")
            return Job.from_dict(response)
    
    async def _async_get_stem_job(self, job_id: int) -> Job:
        """Async version of get_stem_job"""
        response = await self.client.request("GET", f"/api/v1/stem-extraction/status/{job_id}")
        return Job.from_dict(response)
    
    def list_stem_jobs(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[Job]:
        """
        List stem extraction jobs
        
        Args:
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
            
        Returns:
            List of stem extraction jobs
        """
        params = {
            "skip": skip,
            "limit": limit
        }
        
        if self.async_mode:
            return self._async_list_stem_jobs(params)
        else:
            response = self.client.request("GET", "/api/v1/stem-extraction/jobs", params=params)
            return [Job.from_dict(job_data) for job_data in response]
    
    async def _async_list_stem_jobs(self, params: Dict[str, Any]) -> List[Job]:
        """Async version of list_stem_jobs"""
        response = await self.client.request("GET", "/api/v1/stem-extraction/jobs", params=params)
        return [Job.from_dict(job_data) for job_data in response]
    
    def delete_stem_job(self, job_id: int) -> Dict[str, str]:
        """
        Delete a stem extraction job
        
        Args:
            job_id: ID of the job to delete
            
        Returns:
            Deletion confirmation
        """
        if self.async_mode:
            return self._async_delete_stem_job(job_id)
        else:
            return self.client.request("DELETE", f"/api/v1/stem-extraction/jobs/{job_id}")
    
    async def _async_delete_stem_job(self, job_id: int) -> Dict[str, str]:
        """Async version of delete_stem_job"""
        return await self.client.request("DELETE", f"/api/v1/stem-extraction/jobs/{job_id}")
