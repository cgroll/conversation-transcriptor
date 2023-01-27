# %%
import click
from src.models.whisper import whisper_inference_with_segments_df
from src.models.pyannote import get_pyannote_access_token, pyannote_inference_df
from src.models.conversation_transcription import combine_consecutive_speakers, \
    combine_whisper_and_pyannote, text_speaker_df_to_text
from src.audio_utils import download_mp3, transform_mp3_to_wav, crop_wav

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
def wav_to_transcript(wav_fname, model_type):
    
    text_df = whisper_inference_with_segments_df(wav_fname, model_type=model_type)
    text_df = text_df.reset_index()
    
    dotenv_path = './.env'
    pyannote_token = get_pyannote_access_token(dotenv_path)

    speaker_df = pyannote_inference_df(wav_fname, pyannote_token)
    print('done')
    
    text_speaker_df_raw = combine_whisper_and_pyannote(text_df, speaker_df)    
    text_speaker_df = combine_consecutive_speakers(text_speaker_df_raw)
    output_str = text_speaker_df_to_text(text_speaker_df)
    
    click.echo(output_str)



@click.command()
@click.option('--url', type=click.STRING, 
              prompt='Please provide the url to an mp3 file')
@click.option('--model_type', type=click.Choice(choices=WHISPER_MODELS), 
              default='base', prompt='Provide the Whisper model',
              help='Defines the model type in Whisper')
def url_to_transcript(url, model_type):
    
    ## download file, transform to wav
    mp3_fname = download_mp3(url)
    wav_fname = transform_mp3_to_wav(mp3_fname)
    crop_wav(wav_fname, wav_fname, start_frame=100000, n_frames=60000)
    
    text_df = whisper_inference_with_segments_df(wav_fname, model_type=model_type)
    text_df = text_df.reset_index()
    
    dotenv_path = './.env'
    pyannote_token = get_pyannote_access_token(dotenv_path)

    speaker_df = pyannote_inference_df(wav_fname, pyannote_token)
    print('done')
    
    text_speaker_df_raw = combine_whisper_and_pyannote(text_df, speaker_df)    
    text_speaker_df = combine_consecutive_speakers(text_speaker_df_raw)
    output_str = text_speaker_df_to_text(text_speaker_df)
    
    click.echo(output_str)

transcribe.add_command(url_to_transcript)
transcribe.add_command(wav_to_transcript)

# %%

if __name__ == '__main__':
    
    # wav_fname = 'freakonomics_tiny.wav'
    # wav_fname = 'voice.wav'
    # model_type = 'base.en'
    
    transcribe()
    
