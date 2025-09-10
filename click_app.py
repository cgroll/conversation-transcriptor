# %%
import click
import os
from pathlib import Path
from convscript.conversation_transcription import wav_to_transcript
from convscript.audio_utils import download_mp3, transform_mp3_to_wav
from convscript.model_pyannote import get_pyannote_access_token
from paths import INPUTS_RAW_DIR, INPUTS_WAV_DIR

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

transcribe.add_command(click_url_to_transcript)
transcribe.add_command(click_wav_to_transcript)

if __name__ == '__main__':
    
    transcribe()
    
