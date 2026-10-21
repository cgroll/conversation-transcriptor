import numpy as np
import pandas as pd
import soundfile as sf
import torch

from convscript.nemo_utils import quiet_nemo_logging

PARAKEET_MODEL = "nvidia/parakeet-tdt-0.6b-v3"
SAMPLE_RATE = 16000

# Full attention over a whole podcast does not fit into 8 GB VRAM, so the
# audio is transcribed in chunks of about this length (peak ~5.2 GB).
CHUNK_SECONDS = 300
# Chunk borders are moved to the quietest 50 ms frame within this window,
# so that words are not cut in half.
CUT_SEARCH_SECONDS = 15
CUT_FRAME_SAMPLES = 800


def load_mono_16k(fname):

    audio, sample_rate = sf.read(fname, dtype="float32", always_2d=True)
    audio = audio.mean(axis=1)

    if sample_rate != SAMPLE_RATE:
        import librosa
        audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=SAMPLE_RATE)

    return audio


def find_chunk_borders(audio, chunk_seconds=CHUNK_SECONDS):

    chunk_len = chunk_seconds * SAMPLE_RATE
    search_len = CUT_SEARCH_SECONDS * SAMPLE_RATE

    borders = [0]
    pos = chunk_len
    while pos < len(audio) - 60 * SAMPLE_RATE:
        window = audio[pos - search_len:pos + search_len]
        frames = window.reshape(-1, CUT_FRAME_SAMPLES)
        quietest = int(np.argmin((frames ** 2).mean(axis=1)))
        borders.append(pos - search_len + quietest * CUT_FRAME_SAMPLES + CUT_FRAME_SAMPLES // 2)
        pos = borders[-1] + chunk_len
    borders.append(len(audio))

    return borders


def parakeet_inference_df(fname):
    """Transcribe an audio file into a DataFrame with columns id, start, end, text."""

    quiet_nemo_logging()
    from nemo.collections.asr.models import ASRModel

    audio = load_mono_16k(fname)
    borders = find_chunk_borders(audio)

    model = ASRModel.from_pretrained(PARAKEET_MODEL).eval().cuda()

    rows = []
    with torch.autocast("cuda", dtype=torch.bfloat16):
        for chunk_start, chunk_end in zip(borders[:-1], borders[1:]):
            hyp = model.transcribe([audio[chunk_start:chunk_end]], timestamps=True, verbose=False)[0]
            offset = chunk_start / SAMPLE_RATE
            for seg in hyp.timestamp["segment"]:
                rows.append({"id": len(rows),
                             "start": seg["start"] + offset,
                             "end": seg["end"] + offset,
                             "text": seg["segment"]})

    del model
    torch.cuda.empty_cache()

    return pd.DataFrame(rows, columns=["id", "start", "end", "text"])
