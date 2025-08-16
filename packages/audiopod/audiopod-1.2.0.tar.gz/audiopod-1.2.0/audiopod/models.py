"""
AudioPod API Client Models
Data structures for API responses
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum


class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VoiceType(str, Enum):
    """Voice profile types"""
    CUSTOM = "custom"
    STANDARD = "standard"


class TTSProvider(str, Enum):
    """Text-to-speech providers"""
    AUDIOPOD_SONIC = "audiopod_sonic"
    OPENAI = "openai"
    GOOGLE_GEMINI = "google_gemini"


@dataclass
class Job:
    """Base job information"""
    id: int
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create Job from API response data"""
        return cls(
            id=data['id'],
            status=JobStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at'].replace('Z', '+00:00')) if data.get('completed_at') else None,
            progress=data.get('progress', 0.0),
            error_message=data.get('error_message'),
            parameters=data.get('parameters'),
            result=data.get('result')
        )


@dataclass
class VoiceProfile:
    """Voice profile information"""
    id: int
    uuid: str
    name: str
    display_name: Optional[str]
    description: Optional[str]
    voice_type: VoiceType
    provider: TTSProvider
    is_public: bool
    language_code: Optional[str] = None
    language_name: Optional[str] = None
    gender: Optional[str] = None
    accent: Optional[str] = None
    created_at: Optional[datetime] = None
    status: Optional[JobStatus] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceProfile':
        """Create VoiceProfile from API response data"""
        return cls(
            id=data['id'],
            uuid=data['uuid'],
            name=data['name'],
            display_name=data.get('display_name'),
            description=data.get('description'),
            voice_type=VoiceType(data['voice_type']),
            provider=TTSProvider(data['provider']),
            is_public=data['is_public'],
            language_code=data.get('language_code'),
            language_name=data.get('language_name'),
            gender=data.get('gender'),
            accent=data.get('accent'),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None,
            status=JobStatus(data['status']) if data.get('status') else None
        )


@dataclass
class TranscriptionResult:
    """Transcription job result"""
    job: Job
    transcript: Optional[str] = None
    detected_language: Optional[str] = None
    confidence_score: Optional[float] = None
    segments: Optional[List[Dict[str, Any]]] = None
    audio_duration: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptionResult':
        """Create TranscriptionResult from API response data"""
        return cls(
            job=Job.from_dict(data),
            transcript=data.get('transcript'),
            detected_language=data.get('detected_language'),
            confidence_score=data.get('confidence_score'),
            segments=data.get('segments'),
            audio_duration=data.get('total_duration')
        )


@dataclass
class MusicGenerationResult:
    """Music generation job result"""
    job: Job
    output_url: Optional[str] = None
    output_urls: Optional[Dict[str, str]] = None  # Format -> URL mapping
    audio_duration: Optional[float] = None
    actual_seeds: Optional[List[int]] = None
    share_token: Optional[str] = None
    share_url: Optional[str] = None
    is_shared: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MusicGenerationResult':
        """Create MusicGenerationResult from API response data"""
        return cls(
            job=Job.from_dict(data),
            output_url=data.get('output_url'),
            output_urls=data.get('output_urls'),
            audio_duration=data.get('audio_duration'),
            actual_seeds=data.get('actual_seeds'),
            share_token=data.get('share_token'),
            share_url=data.get('share_url'),
            is_shared=data.get('is_shared', False)
        )


@dataclass
class TranslationResult:
    """Speech translation job result"""
    job: Job
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    display_name: Optional[str] = None
    audio_output_path: Optional[str] = None
    video_output_path: Optional[str] = None
    transcript_path: Optional[str] = None
    translated_audio_url: Optional[str] = None
    video_output_url: Optional[str] = None
    transcript_urls: Optional[Dict[str, str]] = None
    is_video: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationResult':
        """Create TranslationResult from API response data"""
        return cls(
            job=Job.from_dict(data),
            source_language=data.get('source_language'),
            target_language=data.get('target_language'),
            display_name=data.get('display_name'),
            audio_output_path=data.get('audio_output_path'),
            video_output_path=data.get('video_output_path'),
            transcript_path=data.get('transcript_path'),
            translated_audio_url=data.get('translated_audio_url'),
            video_output_url=data.get('video_output_url'),
            transcript_urls=data.get('transcript_urls'),
            is_video=data.get('is_video', False)
        )
    
    @property
    def audio_output_url(self) -> Optional[str]:
        """Backward compatibility property - returns translated_audio_url"""
        return self.translated_audio_url


@dataclass
class SpeakerAnalysisResult:
    """Speaker analysis job result"""
    job: Job
    num_speakers: Optional[int] = None
    speaker_segments: Optional[List[Dict[str, Any]]] = None
    output_paths: Optional[Dict[str, str]] = None
    rttm_path: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpeakerAnalysisResult':
        """Create SpeakerAnalysisResult from API response data"""
        return cls(
            job=Job.from_dict(data),
            num_speakers=data.get('num_speakers'),
            speaker_segments=data.get('speaker_segments'),
            output_paths=data.get('output_paths'),
            rttm_path=data.get('rttm_path')
        )


@dataclass
class DenoiseResult:
    """Audio denoising job result"""
    job: Job
    output_url: Optional[str] = None
    video_output_url: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    is_video: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DenoiseResult':
        """Create DenoiseResult from API response data"""
        return cls(
            job=Job.from_dict(data),
            output_url=data.get('output_path'),
            video_output_url=data.get('video_output_path'),
            stats=data.get('stats'),
            is_video=data.get('is_video', False)
        )


@dataclass
class CreditInfo:
    """User credit information"""
    balance: int
    payg_balance: int
    total_available_credits: int
    next_reset_date: Optional[datetime] = None
    total_credits_used: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreditInfo':
        """Create CreditInfo from API response data"""
        return cls(
            balance=data['balance'],
            payg_balance=data['payg_balance'],
            total_available_credits=data['total_available_credits'],
            next_reset_date=datetime.fromisoformat(data['next_reset_date'].replace('Z', '+00:00')) if data.get('next_reset_date') else None,
            total_credits_used=data.get('total_credits_used', 0)
        )
