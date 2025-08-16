"""
AudioPod CLI - Command Line Interface
"""

import os
import sys
import json
import click
from typing import Optional

from .client import Client
from .exceptions import AudioPodError


@click.group()
@click.option('--api-key', envvar='AUDIOPOD_API_KEY', help='AudioPod API key')
@click.option('--base-url', default='https://api.audiopod.ai', help='API base URL')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def cli(ctx, api_key: str, base_url: str, debug: bool):
    """AudioPod CLI - Professional Audio Processing powered by AI"""
    ctx.ensure_object(dict)
    
    if not api_key:
        click.echo("Error: API key is required. Set AUDIOPOD_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    try:
        ctx.obj['client'] = Client(
            api_key=api_key,
            base_url=base_url,
            debug=debug
        )
    except AudioPodError as e:
        click.echo(f"Error: {e.message}")
        sys.exit(1)


@cli.command()
@click.pass_context
def health(ctx):
    """Check API health status"""
    try:
        client = ctx.obj['client']
        status = client.check_health()
        click.echo(f"API Status: {status.get('status', 'Unknown')}")
    except AudioPodError as e:
        click.echo(f"Health check failed: {e.message}")
        sys.exit(1)


@cli.group()
def credits():
    """Credit management commands"""
    pass


@credits.command('balance')
@click.pass_context
def credits_balance(ctx):
    """Get current credit balance"""
    try:
        client = ctx.obj['client']
        credits = client.credits.get_credit_balance()
        
        click.echo("Credit Balance:")
        click.echo(f"  Subscription Credits: {credits.balance:,}")
        click.echo(f"  Pay-as-you-go Credits: {credits.payg_balance:,}")
        click.echo(f"  Total Available: {credits.total_available_credits:,}")
        click.echo(f"  Total Used: {credits.total_credits_used:,}")
        if credits.next_reset_date:
            click.echo(f"  Next Reset: {credits.next_reset_date}")
            
    except AudioPodError as e:
        click.echo(f"Failed to get credit balance: {e.message}")
        sys.exit(1)


@credits.command('usage')
@click.pass_context
def credits_usage(ctx):
    """Get credit usage history"""
    try:
        client = ctx.obj['client']
        usage = client.credits.get_usage_history()
        
        if not usage:
            click.echo("No usage history found.")
            return
            
        click.echo("Recent Credit Usage:")
        for record in usage[:10]:  # Show last 10 records
            click.echo(f"  {record['created_at']}: {record['service_type']} - {record['credits_used']} credits")
            
    except AudioPodError as e:
        click.echo(f"Failed to get usage history: {e.message}")
        sys.exit(1)


@cli.group()
def voice():
    """Voice cloning and TTS commands"""
    pass


@voice.command('clone')
@click.argument('voice_file', type=click.Path(exists=True))
@click.argument('text')
@click.option('--language', '-l', help='Target language code (e.g., en, es)')
@click.option('--speed', '-s', default=1.0, help='Speech speed (0.5-2.0)')
@click.option('--wait', is_flag=True, help='Wait for completion')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def voice_clone(ctx, voice_file: str, text: str, language: Optional[str], 
               speed: float, wait: bool, output: Optional[str]):
    """Clone a voice from audio file"""
    try:
        client = ctx.obj['client']
        
        click.echo(f"Cloning voice from {voice_file}...")
        
        job = client.voice.clone_voice(
            voice_file=voice_file,
            text=text,
            language=language,
            speed=speed,
            wait_for_completion=wait
        )
        
        if wait:
            click.echo(f"Voice cloning completed!")
            if 'output_url' in job:
                click.echo(f"Generated audio URL: {job['output_url']}")
            if output:
                # Here you could add download functionality
                click.echo(f"To download: curl -o {output} '{job['output_url']}'")
        else:
            click.echo(f"Voice cloning job started with ID: {job.id}")
            click.echo(f"Check status with: audiopod voice status {job.id}")
            
    except AudioPodError as e:
        click.echo(f"Voice cloning failed: {e.message}")
        sys.exit(1)


@voice.command('list')
@click.option('--limit', default=20, help='Maximum number of voices to show')
@click.pass_context  
def voice_list(ctx, limit: int):
    """List available voice profiles"""
    try:
        client = ctx.obj['client']
        voices = client.voice.list_voice_profiles(limit=limit)
        
        if not voices:
            click.echo("No voice profiles found.")
            return
            
        click.echo("Available Voice Profiles:")
        for voice in voices:
            status_icon = "✓" if voice.status == "completed" else "⏳"
            visibility = "Public" if voice.is_public else "Private"
            click.echo(f"  {status_icon} {voice.name} (ID: {voice.id}) - {visibility}")
            if voice.description:
                click.echo(f"    {voice.description}")
                
    except AudioPodError as e:
        click.echo(f"Failed to list voices: {e.message}")
        sys.exit(1)


@cli.group()
def music():
    """Music generation commands"""
    pass


@music.command('generate')
@click.argument('prompt')
@click.option('--duration', '-d', default=120.0, help='Duration in seconds')
@click.option('--wait', is_flag=True, help='Wait for completion')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def music_generate(ctx, prompt: str, duration: float, wait: bool, output: Optional[str]):
    """Generate music from text prompt"""
    try:
        client = ctx.obj['client']
        
        click.echo(f"Generating music: '{prompt}'...")
        
        job = client.music.generate_music(
            prompt=prompt,
            duration=duration,
            wait_for_completion=wait
        )
        
        if wait:
            click.echo("Music generation completed!")
            if hasattr(job, 'output_url') and job.output_url:
                click.echo(f"Generated music URL: {job.output_url}")
            if output:
                click.echo(f"To download: curl -o {output} '{job.output_url}'")
        else:
            click.echo(f"Music generation job started with ID: {job.id}")
            click.echo(f"Check status with: audiopod music status {job.id}")
            
    except AudioPodError as e:
        click.echo(f"Music generation failed: {e.message}")
        sys.exit(1)


@music.command('list')
@click.option('--limit', default=20, help='Maximum number of tracks to show')
@click.pass_context
def music_list(ctx, limit: int):
    """List generated music tracks"""
    try:
        client = ctx.obj['client']
        tracks = client.music.list_music_jobs(limit=limit)
        
        if not tracks:
            click.echo("No music tracks found.")
            return
            
        click.echo("Generated Music Tracks:")
        for track in tracks:
            status_icon = "✓" if track.job.status == "completed" else "⏳"
            prompt = track.job.parameters.get('prompt', 'N/A') if track.job.parameters else 'N/A'
            click.echo(f"  {status_icon} Job {track.job.id}: '{prompt[:50]}...'")
            
    except AudioPodError as e:
        click.echo(f"Failed to list music tracks: {e.message}")
        sys.exit(1)


@cli.group()
def transcription():
    """Transcription commands"""
    pass


@transcription.command('transcribe')
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--language', '-l', help='Language code (auto-detect if not specified)')
@click.option('--speakers', is_flag=True, help='Enable speaker diarization')
@click.option('--wait', is_flag=True, help='Wait for completion')
@click.option('--format', '-f', default='txt', help='Output format (txt, json, srt)')
@click.pass_context
def transcription_transcribe(ctx, audio_file: str, language: Optional[str], 
                           speakers: bool, wait: bool, format: str):
    """Transcribe audio to text"""
    try:
        client = ctx.obj['client']
        
        click.echo(f"Transcribing {audio_file}...")
        
        job = client.transcription.transcribe_audio(
            audio_file=audio_file,
            language=language,
            enable_speaker_diarization=speakers,
            wait_for_completion=wait
        )
        
        if wait:
            click.echo("Transcription completed!")
            if hasattr(job, 'transcript') and job.transcript:
                click.echo("Transcript:")
                click.echo(job.transcript)
            if speakers and hasattr(job, 'segments') and job.segments:
                click.echo(f"\nFound {len(job.segments)} speaker segments")
        else:
            click.echo(f"Transcription job started with ID: {job.id}")
            
    except AudioPodError as e:
        click.echo(f"Transcription failed: {e.message}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    cli()


if __name__ == '__main__':
    main()
