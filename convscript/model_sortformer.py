import pandas as pd
import torch

from convscript.nemo_utils import quiet_nemo_logging

SORTFORMER_MODEL = "nvidia/diar_streaming_sortformer_4spk-v2.1"


def sortformer_inference_df(fname):
    """Diarize a whole audio file (max. 4 speakers) into a DataFrame with columns start, end, speaker.

    Runs in a single pass over the full file: the streaming speaker cache keeps
    speaker labels consistent from start to end.
    """

    quiet_nemo_logging()
    from nemo.collections.asr.models import SortformerEncLabelModel

    model = SortformerEncLabelModel.from_pretrained(SORTFORMER_MODEL).eval().cuda()

    # high-latency streaming setup from the model card, best for offline files
    modules = model.sortformer_modules
    modules.chunk_len = 340
    modules.chunk_right_context = 40
    modules.fifo_len = 40
    modules.spkcache_update_period = 300
    modules.spkcache_len = 188
    modules._check_streaming_parameters()

    segments = model.diarize(audio=[str(fname)], batch_size=1, verbose=False)[0]

    del model
    torch.cuda.empty_cache()

    rows = []
    for seg in segments:
        start, end, speaker = seg.split()
        # speaker_0 -> SPEAKER_00, matching earlier transcripts
        speaker_no = int(speaker.split("_")[-1])
        rows.append({"start": round(float(start), 2),
                     "end": round(float(end), 2),
                     "speaker": f"SPEAKER_{speaker_no:02d}"})

    return pd.DataFrame(rows, columns=["start", "end", "speaker"])
