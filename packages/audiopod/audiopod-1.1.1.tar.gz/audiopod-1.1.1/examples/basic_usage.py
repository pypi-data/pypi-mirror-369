"""
AudioPod SDK - Basic Usage Examples

This file demonstrates how to use the AudioPod Python SDK for various audio processing tasks.
Make sure to set your API key in the AUDIOPOD_API_KEY environment variable before running.
"""

import os
import time
import asyncio
from pathlib import Path

import audiopod
from audiopod.exceptions import AudioPodError, ProcessingError


def setup_client():
    """Setup the AudioPod client with API key"""
    api_key = os.getenv("AUDIOPOD_API_KEY")
    if not api_key:
        print("Please set your AUDIOPOD_API_KEY environment variable")
        print("Get your API key from: https://app.audiopod.ai/dashboard")
        return None
    
    return audiopod.Client(api_key=api_key, debug=True)


def check_api_health(client):
    """Check if the API is accessible"""
    print("🔍 Checking API health...")
    try:
        health = client.check_health()
        print(f"✅ API Status: {health.get('status', 'OK')}")
        
        # Get user info
        user_info = client.get_user_info()
        print(f"👤 Logged in as: {user_info.get('email', 'Unknown')}")
        
        return True
    except AudioPodError as e:
        print(f"❌ API Health Check Failed: {e.message}")
        return False


def check_credits(client):
    """Check available credits"""
    print("\n💰 Checking credit balance...")
    try:
        credits = client.credits.get_credit_balance()
        print(f"📊 Credit Balance:")
        print(f"   Subscription Credits: {credits.balance:,}")
        print(f"   Pay-as-you-go Credits: {credits.payg_balance:,}")
        print(f"   Total Available: {credits.total_available_credits:,}")
        
        if credits.total_available_credits < 100:
            print("⚠️  Warning: Low credit balance. Consider purchasing more credits.")
        
        return credits.total_available_credits > 0
    except AudioPodError as e:
        print(f"❌ Failed to check credits: {e.message}")
        return False


def voice_cloning_example(client):
    """Demonstrate voice cloning functionality"""
    print("\n🎤 Voice Cloning Example")
    print("=" * 50)
    
    # For this example, you'll need a voice sample file
    # Replace with path to your audio file
    voice_file = "examples/voice_sample.wav"
    
    if not Path(voice_file).exists():
        print(f"⚠️  Voice sample file not found: {voice_file}")
        print("   Please provide a voice sample (wav, mp3, etc.) to test voice cloning")
        return
    
    try:
        print(f"🔄 Cloning voice from: {voice_file}")
        
        # Clone voice with sample text
        job = client.voice.clone_voice(
            voice_file=voice_file,
            text="Hello! This is an example of voice cloning using the AudioPod API.",
            language="en",
            speed=1.0,
            wait_for_completion=True,
            timeout=300
        )
        
        print("✅ Voice cloning completed!")
        if 'output_url' in job:
            print(f"🎵 Generated audio: {job['output_url']}")
        
    except ProcessingError as e:
        print(f"❌ Voice cloning failed: {e.message}")
    except AudioPodError as e:
        print(f"❌ API Error: {e.message}")


def voice_profile_example(client):
    """Demonstrate creating and using voice profiles"""
    print("\n👤 Voice Profile Example")
    print("=" * 50)
    
    voice_file = "examples/voice_sample.wav"
    
    if not Path(voice_file).exists():
        print(f"⚠️  Voice sample file not found: {voice_file}")
        return
    
    try:
        # Create a voice profile
        print("🔄 Creating voice profile...")
        voice_profile = client.voice.create_voice_profile(
            name="Example Voice Profile",
            voice_file=voice_file,
            description="A test voice profile created via SDK",
            is_public=False,
            wait_for_completion=True
        )
        
        print(f"✅ Voice profile created: {voice_profile.name} (ID: {voice_profile.id})")
        
        # Use the voice profile for speech generation
        print("🔄 Generating speech with voice profile...")
        speech = client.voice.generate_speech(
            voice_id=voice_profile.id,
            text="This speech was generated using my custom voice profile!",
            language="en",
            wait_for_completion=True
        )
        
        print("✅ Speech generation completed!")
        if 'output_url' in speech:
            print(f"🎵 Generated speech: {speech['output_url']}")
        
        # List all voice profiles
        print("\n📋 Your voice profiles:")
        voices = client.voice.list_voice_profiles(limit=10)
        for voice in voices:
            status = "✅" if voice.status == "completed" else "⏳"
            visibility = "🌍" if voice.is_public else "🔒"
            print(f"   {status} {visibility} {voice.name} (ID: {voice.id})")
        
    except AudioPodError as e:
        print(f"❌ Voice profile error: {e.message}")


def music_generation_example(client):
    """Demonstrate music generation"""
    print("\n🎵 Music Generation Example")
    print("=" * 50)
    
    try:
        # Generate music from text prompt
        print("🔄 Generating music from prompt...")
        music_job = client.music.generate_music(
            prompt="upbeat electronic dance music with synthesizers and a strong beat",
            duration=60.0,  # 1 minute for faster processing
            guidance_scale=7.5,
            wait_for_completion=True,
            timeout=600
        )
        
        print("✅ Music generation completed!")
        print(f"🎵 Generated music: {music_job.output_url}")
        
        # Generate rap music
        print("\n🔄 Generating rap music...")
        rap_job = client.music.generate_rap(
            lyrics="""
            Welcome to AudioPod, the future is here
            AI music generation, crystal clear
            From voice cloning to beats so fresh
            AudioPod delivers, better than the rest
            """,
            style="modern",
            tempo=120,
            wait_for_completion=True
        )
        
        print("✅ Rap generation completed!")
        print(f"🎤 Generated rap: {rap_job.output_url}")
        
        # Like the generated music
        like_result = client.music.like_music_track(rap_job.job.id)
        print("👍 Liked the generated rap track")
        
    except AudioPodError as e:
        print(f"❌ Music generation error: {e.message}")


def transcription_example(client):
    """Demonstrate audio transcription"""
    print("\n📝 Transcription Example")
    print("=" * 50)
    
    audio_file = "examples/speech_sample.wav"
    
    if not Path(audio_file).exists():
        print(f"⚠️  Audio file not found: {audio_file}")
        print("   Please provide an audio file to test transcription")
        return
    
    try:
        print(f"🔄 Transcribing audio: {audio_file}")
        
        transcript_job = client.transcription.transcribe_audio(
            audio_file=audio_file,
            language="en",
            enable_speaker_diarization=True,
            enable_word_timestamps=True,
            wait_for_completion=True
        )
        
        print("✅ Transcription completed!")
        print(f"📝 Transcript: {transcript_job.transcript}")
        print(f"🗣️  Detected language: {transcript_job.detected_language}")
        print(f"🎯 Confidence score: {transcript_job.confidence_score:.2f}")
        
        if transcript_job.segments:
            print(f"👥 Found {len(transcript_job.segments)} speaker segments")
        
    except AudioPodError as e:
        print(f"❌ Transcription error: {e.message}")


def translation_example(client):
    """Demonstrate speech-to-speech translation"""
    print("\n🌍 Speech Translation Example")
    print("=" * 50)
    
    audio_file = "examples/english_speech.wav"
    
    if not Path(audio_file).exists():
        print(f"⚠️  Audio file not found: {audio_file}")
        print("   Please provide an English audio file to test translation")
        print("   Alternatively, you can use a URL - see example below")
        
        # Show URL-based translation example
        try:
            print("\n🔄 Trying URL-based translation example...")
            
            translation_job = client.translation.translate_speech(
                url="https://example.com/sample_english.wav",  # Example URL
                target_language="es",  # Spanish
                source_language="en",   # English
                wait_for_completion=False  # Don't wait for this example
            )
            
            print(f"📋 URL translation job started: {translation_job.id}")
            print("   Note: This is just an example - replace with a real audio URL")
            
        except AudioPodError as e:
            print(f"   Expected error (example URL): {e.message}")
        
        return
    
    try:
        print(f"🔄 Translating speech to Spanish (preserving voice characteristics)...")
        
        translation_job = client.translation.translate_audio(
            audio_file=audio_file,
            target_language="es",  # Spanish
            source_language="en",  # English (optional - auto-detect if not specified)
            wait_for_completion=True,
            timeout=900  # 15 minutes for translation
        )
        
        print("✅ Speech translation completed!")
        print(f"🎵 Translated audio: {translation_job.translated_audio_url}")
        print(f"🎬 Video output: {translation_job.video_output_url}")
        print(f"📝 Source language: {translation_job.source_language}")
        print(f"🎯 Target language: {translation_job.target_language}")
        print(f"📄 Display name: {translation_job.display_name}")
        
        if translation_job.transcript_urls:
            print("📋 Transcript URLs:")
            for format_type, url in translation_job.transcript_urls.items():
                print(f"   {format_type}: {url}")
        
        # Demonstrate additional translation methods
        print("\n🔄 Demonstrating job management...")
        
        # List recent translation jobs
        jobs = client.translation.list_translation_jobs(limit=5)
        print(f"📋 Found {len(jobs)} recent translation jobs")
        
        # Show job retry capability (don't actually retry)
        print(f"🔄 Job retry available for failed jobs: translation.retry_translation({translation_job.job.id})")
        
    except AudioPodError as e:
        print(f"❌ Translation error: {e.message}")


def audio_enhancement_example(client):
    """Demonstrate audio denoising"""
    print("\n🔧 Audio Enhancement Example")
    print("=" * 50)
    
    noisy_audio = "examples/noisy_audio.wav"
    
    if not Path(noisy_audio).exists():
        print(f"⚠️  Audio file not found: {noisy_audio}")
        print("   Please provide a noisy audio file to test denoising")
        return
    
    try:
        print(f"🔄 Denoising audio: {noisy_audio}")
        
        denoise_job = client.denoiser.denoise_audio(
            audio_file=noisy_audio,
            quality_mode="balanced",
            wait_for_completion=True
        )
        
        print("✅ Audio denoising completed!")
        print(f"🎵 Cleaned audio: {denoise_job.output_url}")
        
        if denoise_job.stats:
            print("📊 Denoising statistics:")
            for key, value in denoise_job.stats.items():
                print(f"   {key}: {value}")
        
    except AudioPodError as e:
        print(f"❌ Denoising error: {e.message}")


def speaker_analysis_example(client):
    """Demonstrate speaker diarization"""
    print("\n👥 Speaker Analysis Example")
    print("=" * 50)
    
    multi_speaker_audio = "examples/conversation.wav"
    
    if not Path(multi_speaker_audio).exists():
        print(f"⚠️  Audio file not found: {multi_speaker_audio}")
        print("   Please provide a multi-speaker audio file to test diarization")
        return
    
    try:
        print(f"🔄 Analyzing speakers in: {multi_speaker_audio}")
        
        speaker_job = client.speaker.diarize_speakers(
            audio_file=multi_speaker_audio,
            num_speakers=None,  # Auto-detect
            wait_for_completion=True
        )
        
        print("✅ Speaker analysis completed!")
        print(f"👥 Detected speakers: {speaker_job.num_speakers}")
        
        if speaker_job.output_paths:
            print("🎵 Separated audio files:")
            for speaker, path in speaker_job.output_paths.items():
                print(f"   {speaker}: {path}")
        
    except AudioPodError as e:
        print(f"❌ Speaker analysis error: {e.message}")


async def async_example():
    """Demonstrate async usage"""
    print("\n⚡ Async Usage Example")
    print("=" * 50)
    
    try:
        async with audiopod.AsyncClient() as client:
            # Check health asynchronously
            health = await client.check_health()
            print(f"✅ Async API Status: {health.get('status', 'OK')}")
            
            # Get credits asynchronously
            credits = await client.credits.get_credit_balance()
            print(f"💰 Available credits: {credits.total_available_credits:,}")
            
            # List voice profiles asynchronously
            voices = await client.voice.list_voice_profiles(limit=5)
            print(f"🎤 Found {len(voices)} voice profiles")
            
    except AudioPodError as e:
        print(f"❌ Async error: {e.message}")


def job_monitoring_example(client):
    """Demonstrate job monitoring and status checking"""
    print("\n📊 Job Monitoring Example")
    print("=" * 50)
    
    try:
        # Start a music generation job without waiting
        print("🔄 Starting music generation job...")
        job = client.music.generate_music(
            prompt="relaxing ambient music",
            duration=30.0,
            wait_for_completion=False  # Don't wait
        )
        
        print(f"📋 Job started with ID: {job.id}")
        
        # Monitor job progress
        print("👀 Monitoring job progress...")
        while True:
            current_job = client.music.get_music_job(job.id)
            
            print(f"   Status: {current_job.job.status} | Progress: {current_job.job.progress:.1f}%")
            
            if current_job.job.status == "completed":
                print("✅ Job completed!")
                print(f"🎵 Result: {current_job.output_url}")
                break
            elif current_job.job.status == "failed":
                print(f"❌ Job failed: {current_job.job.error_message}")
                break
            elif current_job.job.status == "cancelled":
                print("⏹️  Job was cancelled")
                break
            
            time.sleep(5)  # Wait 5 seconds before checking again
        
    except AudioPodError as e:
        print(f"❌ Job monitoring error: {e.message}")


def main():
    """Run all examples"""
    print("🎉 AudioPod SDK Examples")
    print("=" * 50)
    
    # Setup client
    client = setup_client()
    if not client:
        return
    
    # Check API health and credits
    if not check_api_health(client):
        return
    
    if not check_credits(client):
        print("❌ Insufficient credits to run examples")
        return
    
    # Run examples
    try:
        voice_cloning_example(client)
        voice_profile_example(client)
        music_generation_example(client)
        transcription_example(client)
        translation_example(client)
        audio_enhancement_example(client)
        speaker_analysis_example(client)
        job_monitoring_example(client)
        
        # Run async example
        print("\n" + "=" * 50)
        asyncio.run(async_example())
        
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        client.close()
    
    print("\n🎉 Examples completed!")
    print("Visit https://docs.audiopod.ai for more documentation")


if __name__ == "__main__":
    main()
