import os
from dotenv import load_dotenv

# Fix for PyTorch 2.6+ weights_only=True default breaking pyannote model loading
# pyannote/pytorch-lightning haven't updated their torch.load() calls yet
import torch
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    # Handle both missing key AND explicit None value
    if kwargs.get('weights_only') is None:
        kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

from pyannote.audio import Pipeline
import pandas as pd
import numpy as np
#

def get_pyannote_access_token(dotenv_path):

    load_dotenv(dotenv_path)
    pyannote_token = os.environ.get('PYANNOTE_ACCESS_TOKEN')

    return pyannote_token

def appyl_pyannote_model(pyannote_token, fname):

    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                        token=pyannote_token)

    # apply the pipeline to an audio file
    diarization = pipeline(fname)

    return diarization

def pyannote_inference_df(fname, pyannote_token):

    diarization = appyl_pyannote_model(pyannote_token, fname)

    # pyannote.audio 4.0+ returns a DiarizeOutput dataclass
    # Extract the Annotation object from it
    if hasattr(diarization, 'speaker_diarization'):
        # New API (pyannote.audio >= 4.0)
        annotation = diarization.speaker_diarization
    else:
        # Legacy API (pyannote.audio < 4.0)
        annotation = diarization

    dia_df = diarization_to_df(annotation)

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