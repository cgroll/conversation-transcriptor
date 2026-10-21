# Conversation Transcriptor

Transcribes podcasts and other conversations (German, English and 23 more European languages) with speaker labels, on a local NVIDIA GPU, and optionally uploads the transcript to Notion.

- **Speech recognition:** NVIDIA [Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Speaker diarization ("who said what"):** NVIDIA [Sortformer 4spk v2.1](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1), max. 4 speakers

## Usage

Run all commands from the project root. `uv run` uses the project environment in `.venv`.

### Transcribe audio from a URL

```bash
uv run from_url --url "https://example.com/episode.mp3" --output_filename my_episode
```

- `--url` must be a **direct link to the audio file** (MP3), not a podcast web page.
- Always pass `--output_filename`. Without it, the name defaults to `url_transcript` and the previous result gets overwritten.
- The download is saved to `data/inputs/raw/<output_filename>.mp3` and converted to `data/inputs/wav/<output_filename>.wav` (16 kHz mono).

### Transcribe a local audio file

```bash
uv run from_wav --wav_fname path/to/audio.wav --output_filename my_recording
```

`from_wav` only accepts **WAV** files, at any sample rate and channel count. Convert other formats (MP3, M4A, ...) with ffmpeg first:

```bash
ffmpeg -i audio.mp3 -ac 1 -ar 16000 audio.wav
```

Use ffmpeg for this, not pydub's `set_frame_rate()`: its resampling has no anti-aliasing filter, and its output made Sortformer split one speaker into two.

### Transcribe from a URL and upload to Notion

```bash
uv run url_to_notion \
  --audio_url "https://example.com/episode.mp3" \
  --source_url "https://www.listennotes.com/podcasts/show/episode" \
  --title "Show - Episode title"

# same, without the Notion upload (--source_url and --title are still required)
uv run url_to_notion --audio_url "..." --source_url "..." --title "..." --skip_notion
```

The output name is derived from the title: `<safe_title>_parakeet_from_url`. Long transcripts are split across several Notion pages. The upload needs the Notion tokens in `.env` (see Setup).

A good source for direct audio links is [Listen Notes](https://www.listennotes.com): open an episode and use "Download Audio" for `--audio_url` and the page URL for `--source_url`.

### Output

- **Transcript:** `data/outputs/<output_filename>.txt`
- **Intermediate CSVs** (named after the WAV file): `data/intermediate/<wav_name>_parakeet_segments.csv` (text segments: id, start, end, text) and `data/intermediate/<wav_name>_sortformer_speaker_segments.csv` (speaker turns: start, end, speaker)

The transcript merges consecutive segments of the same speaker. Times are in seconds:

```
4.24 - 6.96: SPEAKER_01
Herzlich willkommen. Mein Name ist ...

7.12 - 8.24: SPEAKER_00
Und ich bin ...
```

Speakers are labelled `SPEAKER_00` ... `SPEAKER_03` in order of first appearance. They are not mapped to names.

### Runtime and GPU

- **Speed:** A 74 minute podcast takes about 1.5 minutes on an RTX 3070 Laptop GPU (8 GB), including ~30-60 s of model loading. Expect about half the speed when the laptop runs on battery. Each run prints a processing summary at the end.
- **GPU memory:** A run needs about 5.5 GB of free VRAM. A CUDA out-of-memory error usually means another process is holding GPU memory; check with `nvidia-smi`. There is no CPU fallback.
- **First run:** The first run downloads both models (~3 GB) to `~/.cache/huggingface`.
- **Long files:** Parakeet transcribes long files in ~5 minute chunks, cut at the quietest moment nearby, so that it fits into 8 GB VRAM. Sortformer runs in one pass over the whole file, so speaker labels stay consistent across chunks.

## Setup

```bash
uv sync
```

Requirements:
- Python 3.10+
- an NVIDIA GPU with a CUDA 13 capable driver
- `ffmpeg` (`sudo apt install ffmpeg`)

Transcription needs no tokens. The Notion upload needs a `.env` file in the project root:

```bash
NOTION_WRITE_API_TOKEN=your_notion_integration_token_here
NOTION_TRANSCRIPTS_DATABASE_ID=your_notion_database_id_here
```

To get the token, create an integration at [Notion Developers](https://developers.notion.com) and share the database with it.

## Code Overview

```
click_app.py                          CLI commands (from_wav, from_url, url_to_notion)
convscript/
├── conversation_transcription.py     pipeline: wav_to_transcript(), url_to_transcript(), speaker/text merging
├── model_parakeet.py                 speech recognition (chunked)
├── model_sortformer.py               speaker diarization
├── audio_utils.py                    download, MP3 -> 16 kHz mono WAV (ffmpeg)
└── notion.py                         Notion upload
data/                                 inputs/raw, inputs/wav, intermediate, outputs (git-ignored)
```

## Future Ideas

- Accept other audio formats (MP3, M4A) directly in `from_wav`
- Allow YouTube video transcription
- Assign speakers per word (Parakeet provides word timestamps) instead of per sentence segment
- Allow re-naming of speakers (e.g. SPEAKER_00 to "Barack Obama")
- Connect to Instapaper: skipped, because it requires the full API, which is only available after registering an official app with Instapaper

## License

MIT License - See LICENSE file for details
