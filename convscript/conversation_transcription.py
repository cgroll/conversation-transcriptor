import pandas as pd
import numpy as np

from convscript.audio_utils import download_mp3, transform_mp3_to_wav, crop_wav
from convscript.model_whisper import whisper_inference_with_segments_df
from convscript.model_pyannote import get_pyannote_access_token, pyannote_inference_df

def combine_whisper_and_pyannote(text_df, speaker_df):
    
    # find overlapping speakers for each text segment
    overlap_list = []
    
    for idx, this_row in speaker_df.iterrows():
        
        this_start = this_row['start']
        this_end = this_row['end']
        this_speaker = this_row['speaker']
        
        xx_inds = ~((text_df['end'] < this_start) | (text_df['start'] > this_end))
        this_overlap_texts = text_df.loc[xx_inds, :]
        this_overlap_texts['speaker_start'] = this_start
        this_overlap_texts['speaker_end'] = this_end
        this_overlap_texts['speaker'] = this_speaker
        
        overlap_list.append(this_overlap_texts)
        
    all_overlaps = pd.concat(overlap_list)
    all_overlaps = all_overlaps.reset_index(drop=True)
    
    # compute overlap durations
    all_overlaps['max_start'] = np.maximum(all_overlaps['start'], 
                                        all_overlaps['speaker_start'])
    
    all_overlaps['min_end'] = np.minimum(all_overlaps['end'], 
                                        all_overlaps['speaker_end'])
    
    all_overlaps['overlap_duration'] = all_overlaps['min_end'] - all_overlaps['max_start']
    
    # pick only one text/speaker combination for each text
    
    max_overlap_indices = all_overlaps.groupby('id')['overlap_duration'].idxmax()
    text_speaker_df = all_overlaps.loc[max_overlap_indices, :]
    
    return text_speaker_df

def combine_consecutive_speakers(text_speaker_df_raw):

    text_speaker_df = text_speaker_df_raw.copy()
    
    n_iter = text_speaker_df.shape[0]
    
    for counter in range(1, n_iter):
        
        is_same_speaker = (text_speaker_df['speaker'].iloc[counter] == text_speaker_df['speaker'].iloc[counter-1])
        
        if is_same_speaker:
            
            new_start = text_speaker_df['start'].iloc[counter-1]
            previous_text = text_speaker_df['text'].iloc[counter-1]
            new_text = previous_text + ' ' + text_speaker_df['text'].iloc[counter]
            
            text_speaker_df['start'].iloc[counter] = new_start
            text_speaker_df['text'].iloc[counter] = new_text
            text_speaker_df['start'].iloc[counter-1] = np.nan
            text_speaker_df['end'].iloc[counter-1] = np.nan
        
    text_speaker_df = text_speaker_df.dropna().loc[:, ['start', 'end', 'text', 'speaker']]
    text_speaker_df = text_speaker_df.reset_index(drop=True)
    text_speaker_df = text_speaker_df.sort_values('start')
    
    return text_speaker_df

def text_speaker_df_to_text(text_speaker_df):
    
    output_str = ''

    for idx, this_row in text_speaker_df.iterrows():
        
        this_start = np.round(this_row['start'], 2)
        this_end = np.round(this_row['end'], 2)
        this_speaker = this_row['speaker']
        this_text = this_row['text']
        
        output_str += f'{this_start} - {this_end}: {this_speaker}\n'
        output_str += f'{this_text}\n\n'
        
    return output_str

def wav_to_transcript(wav_fname, model_type, pyannote_token):
    
    text_df = whisper_inference_with_segments_df(wav_fname, model_type=model_type)
    text_df = text_df.reset_index()
    
    speaker_df = pyannote_inference_df(wav_fname, pyannote_token)
    print('done')
    
    text_speaker_df_raw = combine_whisper_and_pyannote(text_df, speaker_df)    
    text_speaker_df = combine_consecutive_speakers(text_speaker_df_raw)
    output_str = text_speaker_df_to_text(text_speaker_df)
    
    return output_str

def url_to_transcript(url, model_type, pyannote_token):

    ## download file, transform to wav
    mp3_fname = download_mp3(url)
    wav_fname = transform_mp3_to_wav(mp3_fname)
    print('TODO: remove file cropping in url_to_transcript')
    crop_wav(wav_fname, wav_fname, start_frame=100000, n_frames=60000)
    
    text_df = whisper_inference_with_segments_df(wav_fname, model_type=model_type)
    text_df = text_df.reset_index()
    
    speaker_df = pyannote_inference_df(wav_fname, pyannote_token)
    print('done')
    
    text_speaker_df_raw = combine_whisper_and_pyannote(text_df, speaker_df)    
    text_speaker_df = combine_consecutive_speakers(text_speaker_df_raw)
    output_str = text_speaker_df_to_text(text_speaker_df)
    
    return output_str


if __name__ == '__main__':
    
    import os
    from dotenv import load_dotenv
    from convscript.path import ProjPaths

    dotenv_path = ProjPaths.env_variables_path
    load_dotenv(dotenv_path)
    pyannote_token = os.environ.get('PYANNOTE_ACCESS_TOKEN')

    test_url = 'https://chtbl.com/track/736CG3/pdst.fm/e/stitcher.simplecastaudio.com/2be48404-a43c-4fa8-a32c-760a3216272e/episodes/413d1340-d75e-46ae-956c-3785e2b359b2/audio/128/default.mp3?aid=rss_feed&amp;awCollectionId=2be48404-a43c-4fa8-a32c-760a3216272e&amp;awEpisodeId=413d1340-d75e-46ae-956c-3785e2b359b2&amp;feed=Y8lFbOT4'
    
    output_str = url_to_transcript(test_url, 'base', pyannote_token)
    output_str
    
