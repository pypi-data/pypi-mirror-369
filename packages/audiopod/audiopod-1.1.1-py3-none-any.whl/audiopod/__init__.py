"""
AudioPod API Client
Professional Audio Processing SDK for Python

This package provides a comprehensive Python SDK for the AudioPod API,
enabling developers to integrate advanced audio processing capabilities
into their applications.

Basic Usage:
    >>> import audiopod
    >>> client = audiopod.Client(api_key="your-api-key")
    >>> 
    >>> # Voice cloning
    >>> job = client.voice.clone_voice(
    ...     voice_file="path/to/voice.wav",
    ...     text="Hello, this is a cloned voice!"
    ... )
    >>> 
    >>> # Music generation
    >>> music = client.music.generate(
    ...     prompt="upbeat electronic dance music"
    ... )
    >>> 
    >>> # Audio transcription
    >>> transcript = client.transcription.transcribe(
    ...     audio_file="path/to/audio.mp3",
    ...     language="en"
    ... )

For more examples and documentation, visit: https://docs.audiopod.ai
"""

from .client import Client, AsyncClient
from .exceptions import (
    AudioPodError,
    AuthenticationError, 
    APIError,
    RateLimitError,
    ValidationError,
    ProcessingError
)
from .models import (
    Job,
    VoiceProfile,
    TranscriptionResult,
    MusicGenerationResult,
    TranslationResult
)

__version__ = "1.1.1"
__author__ = "AudioPod AI"
__email__ = "support@audiopod.ai"
__license__ = "MIT"

# Public API
__all__ = [
    # Main clients
    "Client",
    "AsyncClient",
    
    # Exceptions
    "AudioPodError",
    "AuthenticationError",
    "APIError", 
    "RateLimitError",
    "ValidationError",
    "ProcessingError",
    
    # Models
    "Job",
    "VoiceProfile",
    "TranscriptionResult", 
    "MusicGenerationResult",
    "TranslationResult",
]

# Package metadata
__all__.extend([
    "__version__",
    "__author__", 
    "__email__",
    "__license__"
])
