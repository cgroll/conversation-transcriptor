import os
from dotenv import load_dotenv
from pyannote.audio import Pipeline
import pandas as pd
import numpy as np
#

def get_pyannote_access_token(dotenv_path):

    
    load_dotenv(dotenv_path)
    pyannote_token = os.environ.get('PYANNOTE_ACCESS_TOKEN')

    return pyannote_token

def appyl_pyannote_model(pyannote_token, fname):
    
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                        use_auth_token=pyannote_token)

    # apply the pipeline to an audio file
    diarization = pipeline(fname)

    return diarization

def pyannote_inference_df(fname, pyannote_token):
    
    diarization = appyl_pyannote_model(pyannote_token, fname)
    dia_df = diarization_to_df(diarization)
    
    return dia_df

def diarization_to_df(diarization):

    seg_info_list = []
    for speech_turn, track, speaker in diarization.itertracks(yield_label=True):
        
        this_seg_info = {'start': np.round(speech_turn.start, 2),
                        'end': np.round(speech_turn.end, 2),
                        'speaker': speaker}
        this_df = pd.DataFrame.from_dict({track: this_seg_info},
                                        orient='index')
        
        seg_info_list.append(this_df)
        
    all_seg_infos_df = pd.concat(seg_info_list, axis=0)
    all_seg_infos_df = all_seg_infos_df.reset_index()
    
    return all_seg_infos_df