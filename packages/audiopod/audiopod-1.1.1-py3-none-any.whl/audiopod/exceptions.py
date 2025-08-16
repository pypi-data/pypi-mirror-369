"""
AudioPod API Client Exceptions
"""

from typing import Optional, Dict, Any


class AudioPodError(Exception):
    """Base exception for AudioPod API client"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        
    def __str__(self) -> str:
        return self.message


class AuthenticationError(AudioPodError):
    """Raised when API key authentication fails"""
    pass


class APIError(AudioPodError):
    """Raised when API returns an error response"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.status_code = status_code


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after


class ValidationError(AudioPodError):
    """Raised when input validation fails"""
    pass


class ProcessingError(APIError):
    """Raised when audio processing fails"""
    
    def __init__(
        self,
        message: str,
        job_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details=details)
        self.job_id = job_id


class FileError(AudioPodError):
    """Raised when file operations fail"""
    pass


class NetworkError(AudioPodError):
    """Raised when network operations fail"""
    pass


class TimeoutError(AudioPodError):
    """Raised when operations timeout"""
    pass


class InsufficientCreditsError(APIError):
    """Raised when user has insufficient credits"""
    
    def __init__(
        self,
        message: str = "Insufficient credits",
        credits_needed: Optional[int] = None,
        credits_available: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=402, details=details)
        self.credits_needed = credits_needed
        self.credits_available = credits_available
