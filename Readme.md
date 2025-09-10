# Conversation Transcriptor

A tool for extracting conversation transcripts from audio files with speaker diarization (speaker identification). This tool combines two state-of-the-art AI models to provide accurate transcriptions with speaker labels and timing information.

## What This Project Does

The Conversation Transcriptor processes audio files to create detailed transcripts that include:

- **Accurate speech-to-text transcription** using OpenAI's Whisper
- **Speaker identification** (who said what) using pyannote.audio
- **Precise timing information** for each spoken segment

## How It Works

The tool uses a sophisticated two-step process:

1. **Speech Recognition**: Whisper processes the audio to extract text with precise timing
2. **Speaker Diarization**: Pyannote analyzes the audio to identify different speakers
3. **Intelligent Combination**: The system combines both outputs, matching text segments with speakers
4. **Post-processing**: Consecutive segments from the same speaker are merged for readability

## Quick Start (If Already Set Up)

If everything is already configured, you can run transcriptions using these commands:

### Transcribe from Audio File
```bash
python click_app.py click-wav-to-transcript --wav_fname path/to/your/audio.wav
```

### Transcribe from URL
```bash
python click_app.py click-url-to-transcript --url "https://example.com/audio.mp3"
```

### Available Commands
View all available commands:
```bash
python click_app.py --help
```

Get help for a specific command:
```bash
python click_app.py click-wav-to-transcript --help
```

## Complete Setup Instructions

### Prerequisites

1. **System Requirements**:
   - Python 3.8+
   - FFmpeg (for audio processing)
   - GPU recommended (but not required)

2. **Install FFmpeg**:
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`  
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd conversation-transcriptor
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python packages**:
   ```bash
   pip install -r requirements.txt
   pip install --editable .
   ```

### Environment Variables Setup

1. **Get a HuggingFace Token**:
   - Visit [HuggingFace](https://huggingface.co)
   - Create an account and generate an access token
   - Accept the terms for pyannote/speaker-diarization

2. **Create `.env` file**:
   ```bash
   echo "PYANNOTE_ACCESS_TOKEN=your_huggingface_token_here" > .env
   ```

### Verify Installation

Test your setup:
```bash
python click_app.py click-wav-to-transcript --help
```

## Usage Examples

### Basic Transcription
```bash
python click_app.py click-wav-to-transcript \
  --wav_fname audio.wav \
  --model_type large-v3-turbo \
  --output_filename my_transcript
```

### Using Different Whisper Models
Available models: `tiny`, `base`, `small`, `medium`, `large-v1`, `large-v2`, `large-v3-turbo`

```bash
# For faster processing (less accurate)
python click_app.py click-wav-to-transcript --model_type base

# For best quality (slower)
python click_app.py click-wav-to-transcript --model_type large-v3-turbo
```

## Output Files

The tool creates organized output files in the `data/` directory:

### Main Output (`data/outputs/`)
- `{filename}_transcript.txt` - Final transcript with speakers and timing

### Intermediate Data (`data/intermediate/`)
- `{filename}_whisper_{model}_segments.csv` - Raw Whisper segments
- `{filename}_speaker_segments.csv` - Speaker diarization data

## Processing Information

During transcription, you'll see:
- Audio duration and file information
- Real-time processing progress
- Timing for each processing step:
  - Whisper inference time
  - Speaker diarization time  
  - Combination processing time
- Final statistics (processing speed, output length)

## Troubleshooting

### Common Issues

1. **"pyannote token" errors**: Ensure your HuggingFace token is valid and you've accepted the model terms
2. **FFmpeg not found**: Make sure FFmpeg is installed and in your PATH
3. **Out of memory**: Try using a smaller Whisper model (`base` instead of `large-v3-turbo`)
4. **Slow processing**: GPU acceleration significantly speeds up processing

### Performance Tips

- **GPU Usage**: The tool automatically uses GPU if available (CUDA/MPS)
- **Model Selection**: 
  - `base`: Fastest, good for quick transcripts
  - `large-v3-turbo`: Best accuracy, recommended for production
- **Audio Quality**: Higher quality audio produces better results

## Technical Details

### Models Used
- **Whisper**: OpenAI's speech recognition model
- **Pyannote**: Advanced speaker diarization system

### File Structure
```
conversation-transcriptor/
├── convscript/           # Main package
├── data/
│   ├── inputs/          # Input files
│   ├── outputs/         # Final transcripts
│   └── intermediate/    # Processing data
├── click_app.py         # Command-line interface  
└── requirements.txt     # Dependencies
```