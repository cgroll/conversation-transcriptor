# %%
import click
import os
from pathlib import Path
from convscript.conversation_transcription import wav_to_transcript
from convscript.audio_utils import download_mp3, transform_mp3_to_wav
from convscript.model_pyannote import get_pyannote_access_token
from convscript.notion import upload_transcript_to_notion, safe_filename, get_today_date
from paths import INPUTS_RAW_DIR, INPUTS_WAV_DIR, OUTPUTS_DIR

WHISPER_MODELS = ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large', 'large-v3-turbo']

@click.group()
def transcribe():
    pass

@click.command()
@click.option('--wav_fname', type=click.Path(exists=True), 
              prompt='Please provide path to WAV file')
@click.option('--model_type', type=click.Choice(choices=WHISPER_MODELS), 
              default='large-v3-turbo', prompt='Provide the Whisper model',
              help='Defines the model type in Whisper')
@click.option('--output_filename', type=click.STRING,
              help='Output filename (without .txt extension). If not provided, will be prompted.')
def click_wav_to_transcript(wav_fname, model_type, output_filename):
    
    # Prompt for output filename if not provided
    if not output_filename:
        default_name = os.path.splitext(os.path.basename(wav_fname))[0] + f"_{model_type}_transcript"
        output_filename = click.prompt('Output filename (without .txt extension)', 
                                     default=default_name)
    
    dotenv_path = './.env'
    pyannote_token = get_pyannote_access_token(dotenv_path)
    
    wav_to_transcript(wav_fname, model_type, pyannote_token, output_filename)


@click.command()
@click.option('--url', type=click.STRING, 
              prompt='Please provide the url to an mp3 file')
@click.option('--model_type', type=click.Choice(choices=WHISPER_MODELS), 
              default='large-v3-turbo', prompt='Provide the Whisper model',
              help='Defines the model type in Whisper')
@click.option('--output_filename', type=click.STRING,
              help='Output filename (without .txt extension). If not provided, will be prompted.')
def click_url_to_transcript(url, model_type, output_filename):

    # Prompt for output filename if not provided
    if not output_filename:
        default_name = f"url_{model_type}_transcript"
        output_filename = click.prompt('Output filename (without .txt extension)', 
                                     default=default_name)

    dotenv_path = './.env'
    pyannote_token = get_pyannote_access_token(dotenv_path)
    
    # Ensure directories exist
    INPUTS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_WAV_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Download file to inputs/raw
    print("Downloading file from URL...")
    raw_filename = INPUTS_RAW_DIR / f"{output_filename}.mp3"
    downloaded_file = download_mp3(url, str(raw_filename))
    print(f"Downloaded to: {downloaded_file}")
    
    # Step 2: Transform to .wav in inputs/wav
    print("Converting MP3 to WAV...")
    wav_filename = INPUTS_WAV_DIR / f"{output_filename}.wav"
    wav_file = transform_mp3_to_wav(downloaded_file, str(wav_filename))
    print(f"Converted to: {wav_file}")
    
    # Step 3: Do transcription
    print("Starting transcription...")
    wav_to_transcript(wav_file, model_type, pyannote_token, output_filename)


@click.command()
@click.option('--audio_url', type=click.STRING, 
              prompt='Audio file URL (direct link to MP3/WAV)')
@click.option('--source_url', type=click.STRING, 
              prompt='Source URL (e.g., podcast page, YouTube, etc.)',
              help='The original source URL where this content was found')
@click.option('--title', type=click.STRING,
              prompt='Title for the transcript',
              help='Title to use in Notion and for filename')
@click.option('--model_type', type=click.Choice(choices=WHISPER_MODELS), 
              default='large-v3-turbo', prompt='Provide the Whisper model',
              help='Defines the model type in Whisper')
@click.option('--skip_notion', is_flag=True, default=False,
              help='Skip uploading to Notion, just transcribe')
def click_url_to_notion(audio_url, source_url, title, model_type, skip_notion):
    """
    Download audio from URL, transcribe it, and upload to Notion.
    This command handles the full workflow: download -> transcribe -> upload to Notion.
    """
    
    print(f"\n🎯 Starting URL-to-Notion transcription workflow")
    print(f"📄 Title: '{title}'")
    print(f"🎵 Audio URL: {audio_url}")
    print(f"🔗 Source URL: {source_url}")
    print(f"🧠 Model: {model_type}")
    
    # Create safe filename from title
    safe_title = safe_filename(title)
    output_filename = f"{safe_title}_{model_type}_from_url"
    
    print(f"💾 Output filename base: {output_filename}")
    
    dotenv_path = './.env'
    pyannote_token = get_pyannote_access_token(dotenv_path)
    
    # Ensure directories exist
    INPUTS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_WAV_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Download file to inputs/raw
        print(f"\n📥 Step 1: Downloading audio file...")
        raw_filename = INPUTS_RAW_DIR / f"{output_filename}.mp3"
        downloaded_file = download_mp3(audio_url, str(raw_filename))
        print(f"✅ Downloaded to: {downloaded_file}")
        
        # Step 2: Transform to .wav in inputs/wav
        print(f"\n🔄 Step 2: Converting to WAV format...")
        wav_filename = INPUTS_WAV_DIR / f"{output_filename}.wav"
        wav_file = transform_mp3_to_wav(downloaded_file, str(wav_filename))
        print(f"✅ Converted to: {wav_file}")
        
        # Step 3: Do transcription
        print(f"\n📝 Step 3: Starting transcription...")
        transcript_result = wav_to_transcript(wav_file, model_type, pyannote_token, output_filename)
        
        # Find the generated transcript file
        transcript_file = OUTPUTS_DIR / f"{output_filename}.txt"
        if not transcript_file.exists():
            print(f"❌ Transcript file not found at: {transcript_file}")
            return
        
        print(f"✅ Transcription completed: {transcript_file}")
        
        # Step 4: Upload to Notion (if not skipped)
        if not skip_notion:
            print(f"\n📤 Step 4: Uploading to Notion...")
            today_date = get_today_date()
            
            page_url = upload_transcript_to_notion(
                file_path=str(transcript_file),
                title=title,
                date=today_date,
                url=source_url
            )
            
            if page_url:
                print(f"✅ Successfully uploaded to Notion!")
                print(f"🔗 Notion page (Part I if multi-part): {page_url}")
            else:
                print(f"❌ Failed to upload to Notion")
        else:
            print(f"\n⏭️  Skipping Notion upload (--skip_notion flag used)")
        
        print(f"\n🎉 Workflow completed successfully!")
        print(f"📄 Title: '{title}'")
        print(f"💾 Transcript file: {transcript_file}")
        
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        raise

transcribe.add_command(click_url_to_notion)
transcribe.add_command(click_url_to_transcript)
transcribe.add_command(click_wav_to_transcript)

if __name__ == '__main__':
    
    transcribe()
    
