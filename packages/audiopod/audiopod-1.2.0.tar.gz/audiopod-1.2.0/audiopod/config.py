"""
AudioPod Client Configuration
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientConfig:
    """Configuration for AudioPod API client"""
    
    # API settings
    base_url: str = "https://api.audiopod.ai"
    api_version: str = "v1"
    
    # Request settings
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    
    # Client settings
    debug: bool = False
    version: str = "1.0.0"
    
    # Rate limiting
    rate_limit_per_minute: int = 600
    
    # File upload limits
    max_file_size_mb: int = 100
    supported_audio_formats: tuple = (
        ".mp3", ".wav", ".m4a", ".flac", ".ogg", 
        ".aac", ".wma", ".aiff", ".au"
    )
    supported_video_formats: tuple = (
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", 
        ".flv", ".webm", ".m4v"
    )
    
    @property
    def api_base_url(self) -> str:
        """Get full API base URL with version"""
        return f"{self.base_url}/api/{self.api_version}"
        
    def validate_file_format(self, filename: str, file_type: str = "audio") -> bool:
        """
        Validate if file format is supported
        
        Args:
            filename: Name of the file
            file_type: Type of file ('audio' or 'video')
            
        Returns:
            True if format is supported
        """
        filename = filename.lower()
        
        if file_type == "audio":
            return any(filename.endswith(fmt) for fmt in self.supported_audio_formats)
        elif file_type == "video":
            return any(filename.endswith(fmt) for fmt in self.supported_video_formats)
        else:
            return False
