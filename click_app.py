# %%
import click
from convscript.conversation_transcription import wav_to_transcript, \
    url_to_transcript
from convscript.model_pyannote import get_pyannote_access_token

WHISPER_MODELS = ['tiny', 'base', 'small', 'medium', 'large']

@click.group()
def transcribe():
    pass

@click.command()
@click.option('--wav_fname', type=click.Path(exists=True), 
              prompt='Please provide path to WAV file')
@click.option('--model_type', type=click.Choice(choices=WHISPER_MODELS), 
              default='base', prompt='Provide the Whisper model',
              help='Defines the model type in Whisper')

def click_wav_to_transcript(wav_fname, model_type):
    
    dotenv_path = './.env'
    pyannote_token = get_pyannote_access_token(dotenv_path)
    
    output_str = wav_to_transcript(wav_fname, model_type, pyannote_token)
    
    click.echo(output_str)


@click.command()
@click.option('--url', type=click.STRING, 
              prompt='Please provide the url to an mp3 file')
@click.option('--model_type', type=click.Choice(choices=WHISPER_MODELS), 
              default='base', prompt='Provide the Whisper model',
              help='Defines the model type in Whisper')
def click_url_to_transcript(url, model_type):

    dotenv_path = './.env'
    pyannote_token = get_pyannote_access_token(dotenv_path)
    
    output_str = url_to_transcript(url, model_type, pyannote_token)
    
    click.echo(output_str)

transcribe.add_command(click_url_to_transcript)
transcribe.add_command(click_wav_to_transcript)

if __name__ == '__main__':
    
    transcribe()
    
