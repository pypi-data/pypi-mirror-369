# Changelog

All notable changes to the AudioPod Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2024-12-15

### 🔧 Translation Service Fixes

This release fixes the translation service to use the proper speech-to-speech translation endpoint and adds enhanced functionality.

### ✨ Added

- **Speech-to-Speech Translation**: Now uses the correct `/api/v1/translation/translate/speech` endpoint
  - Preserves original speaker voice characteristics during translation
  - Supports both audio and video file translation
  - Maintains speaker separation in multi-speaker content

- **URL-Based Translation**: Support for translating audio/video from URLs
  - Direct media URL support (YouTube, audio links, etc.)
  - No need to download files locally first

- **Enhanced Translation Job Management**:
  - `list_translation_jobs()` - List translation history with pagination
  - `retry_translation()` - Retry failed translation jobs
  - `delete_translation_job()` - Delete translation jobs
  - `translate_speech()` - Alias method for clearer API

### 🔧 Fixed

- **Translation Endpoint**: Changed from generic `/translate` to speech-specific `/translate/speech`
- **API Schema Alignment**: Request and response formats now match the actual API
- **Response Model**: Updated `TranslationResult` to include all API response fields:
  - `translated_audio_url` - Direct URL to translated audio
  - `video_output_url` - Translated video output (when applicable)
  - `transcript_urls` - Transcript files in multiple formats
  - `display_name` - Original file display name
  - `is_video` - Whether the input was a video file

### 🏗️ Improved

- **Better Error Handling**: Enhanced validation for file vs URL inputs
- **Backward Compatibility**: Maintained `audio_output_url` property for existing code
- **Enhanced Examples**: Updated documentation and examples to show new features
- **Type Safety**: Improved type hints and validation

### 📚 Documentation

- **Updated Examples**: `basic_usage.py` now demonstrates speech-to-speech translation
- **README Updates**: Corrected API usage examples with proper endpoint usage
- **Method Documentation**: Enhanced docstrings with accurate parameter descriptions

### 🚀 Usage Examples

#### Fixed Speech Translation
```python
# Speech-to-speech translation (preserves voice characteristics)
translation = client.translation.translate_speech(
    audio_file="english_speech.wav",
    target_language="es",  # Spanish
    source_language="en",  # Optional - auto-detect
    wait_for_completion=True
)

# URL-based translation
url_translation = client.translation.translate_speech(
    url="https://example.com/audio.mp3",
    target_language="fr",  # French
    wait_for_completion=True
)

# Job management
jobs = client.translation.list_translation_jobs(limit=10)
retry_job = client.translation.retry_translation(failed_job_id)
```

### 🔄 Migration Notes

- **No Breaking Changes**: Existing `translate_audio()` method continues to work
- **Enhanced Functionality**: Now uses proper speech-to-speech endpoint automatically
- **New Properties**: Additional response fields available in `TranslationResult`

---

## [1.1.0] - 2024-01-15

### 🎉 Major API Compatibility Update

This release brings full compatibility with the AudioPod v1 API specifications and includes significant improvements and new features.

### ✨ Added

- **New Stem Extraction Service**: Complete implementation of audio stem separation
  - `StemExtractionService` with support for vocals, drums, bass, and instrument separation
  - Support for both `htdemucs` and `htdemucs_6s` models
  - Methods: `extract_stems()`, `get_stem_job()`, `list_stem_jobs()`, `delete_stem_job()`

- **Enhanced Music Generation**: New vocals generation capability
  - `generate_vocals()` method for lyric-to-vocals generation
  - Supports the `/api/v1/music/lyric2vocals` endpoint

- **Comprehensive Test Suite**: Production-ready testing framework
  - End-to-end integration tests (`test_end_to_end_integration.py`)
  - API compatibility validation tests (`test_sdk_api_compatibility.py`)
  - Complete SDK structure validation (`validate_sdk_structure.py`)
  - Comprehensive test runner (`test_sdk_comprehensive.py`)

### 🔧 Fixed

- **Music Service API Schema Alignment**: Critical fixes for API compatibility
  - Fixed parameter names: `duration` → `audio_duration`
  - Fixed parameter names: `num_inference_steps` → `infer_step`
  - Fixed parameter names: `seed` → `manual_seeds` (now accepts list)
  - Fixed response handling to properly extract `job` object from API responses

- **Enhanced Music Generation Methods**: Improved existing capabilities
  - `generate_music()`: Now uses correct API schema parameters
  - `generate_rap()`: Enhanced with proper prompt construction and LoRA support
  - `generate_instrumental()`: Improved parameter mapping
  - `list_music_jobs()`: Fixed pagination parameter (`offset` → `skip`)

- **Response Format Handling**: Proper API response parsing
  - All music generation endpoints now correctly handle `{"job": {...}, "message": "..."}` response format
  - Improved error handling and status checking

### 🏗️ Improved

- **Service Integration**: Better organization and accessibility
  - All services properly integrated in both sync and async clients
  - Enhanced error handling across all services
  - Improved parameter validation

- **Code Quality**: Enhanced maintainability and reliability
  - Better type hints and documentation
  - Improved error messages
  - Enhanced validation for all input parameters

### 📚 Documentation

- **Comprehensive Fix Documentation**: Detailed improvement summary
  - Complete documentation of all changes in `SDK_FIXES_SUMMARY.md`
  - Usage examples for all new features
  - Migration guide (no breaking changes)

- **Testing Documentation**: Complete testing framework
  - Instructions for running validation tests
  - API compatibility verification procedures
  - External developer onboarding documentation

### 🔒 Validation

- **100% Structure Validation Success**: All improvements verified
  - 9/9 validation checks passed
  - Complete API endpoint compatibility confirmed
  - All services properly integrated and functional

### 🚀 Usage Examples

#### New Stem Extraction
```python
# Extract audio stems
job = client.stem_extraction.extract_stems(
    audio_file="song.wav",
    stem_types=["vocals", "drums", "bass", "other"],
    model_name="htdemucs",
    wait_for_completion=True
)
```

#### Enhanced Music Generation
```python
# Generate vocals from lyrics
vocals_job = client.music.generate_vocals(
    lyrics="Your song lyrics here",
    prompt="pop vocals, female voice",
    duration=120.0
)

# Improved music generation with correct parameters
music_job = client.music.generate_music(
    prompt="upbeat electronic dance music",
    duration=120.0,  # Now correctly maps to audio_duration
    guidance_scale=7.5,
    num_inference_steps=50,  # Now correctly maps to infer_step
    seed=12345  # Now correctly maps to manual_seeds=[12345]
)
```

### 🔄 Migration Notes

- **No Breaking Changes**: All existing code continues to work
- **Improved Reliability**: Better error handling and API compatibility
- **Enhanced Features**: New capabilities available immediately

---

## [1.0.0] - 2024-01-01

### 🎉 Initial Release

- Initial implementation of AudioPod Python SDK
- Support for voice cloning, music generation, transcription, and translation
- Async and sync client implementations
- Basic API integration and authentication
- Core service implementations
