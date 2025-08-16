# AudioPod SDK Examples

This directory contains example code demonstrating how to use the AudioPod Python SDK.

## 📋 Files

- **`basic_usage.py`** - Comprehensive examples covering all major SDK features

## 🎯 Setup

1. **Install the SDK**:
   ```bash
   pip install audiopod
   ```

2. **Set your API key**:
   ```bash
   export AUDIOPOD_API_KEY="ap_your_api_key_here"
   ```
   
   Get your API key from: https://app.audiopod.ai/dashboard

3. **Run the examples**:
   ```bash
   python basic_usage.py
   ```

## 🎵 Audio Files

The examples reference several audio files that you should provide:

- `voice_sample.wav` - A voice sample for voice cloning (10-30 seconds recommended)
- `speech_sample.wav` - Speech audio for transcription testing
- `english_speech.wav` - English speech for translation testing
- `noisy_audio.wav` - Audio with background noise for denoising
- `conversation.wav` - Multi-speaker audio for speaker analysis

## 📚 What's Demonstrated

The examples show how to:

- ✅ **Voice Cloning** - Clone a voice from an audio sample
- ✅ **Voice Profiles** - Create and manage reusable voice profiles
- ✅ **Music Generation** - Generate music from text prompts
- ✅ **Rap Generation** - Create rap music with lyrics
- ✅ **Transcription** - Convert speech to text
- ✅ **Translation** - Translate audio between languages
- ✅ **Audio Enhancement** - Remove noise from audio
- ✅ **Speaker Analysis** - Separate different speakers
- ✅ **Job Monitoring** - Track long-running processing jobs
- ✅ **Async Usage** - Use the async client for concurrent operations

## 🔧 Error Handling

The examples include comprehensive error handling and show how to:

- Check API health and connectivity
- Verify credit balance before operations
- Handle different types of API errors
- Monitor job progress and status

## 📊 Best Practices

The examples demonstrate:

- Proper client initialization and cleanup
- Credit balance checking before expensive operations
- Appropriate timeout settings for different operations
- Job status monitoring for long-running tasks
- Using both sync and async clients effectively

## 🆘 Troubleshooting

If you encounter issues:

1. **Check your API key** - Make sure it's set correctly
2. **Verify credits** - Ensure you have sufficient credits
3. **Check file paths** - Make sure audio files exist
4. **Review errors** - The examples provide detailed error messages

For more help, visit: https://docs.audiopod.ai
