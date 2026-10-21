# CLAUDE.md

Usage for transcribing audio files and URLs is documented in Readme.md, section "Usage". In short:

- URL with audio: `uv run from_url --url "<direct mp3 link>" --output_filename <name>`
- Local WAV: `uv run from_wav --wav_fname <file.wav> --output_filename <name>`. Convert other formats first with `ffmpeg -i in.mp3 -ac 1 -ar 16000 out.wav`.
- Result: `data/outputs/<name>.txt`

Before running, check that ~5.5 GB of VRAM are free (`nvidia-smi`). The pipeline is GPU-only.
