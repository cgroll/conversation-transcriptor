# Conversation Transcriptor

A Python toolkit for downloading audio files, transcribing them using Whisper, and uploading transcripts to Notion.

## Features

- 🎵 Download audio files from URLs
- 🗣️ Transcribe audio using OpenAI Whisper with speaker diarization (pyannote)
- 📝 Upload transcripts directly to Notion databases
- 🔗 Support for linking original source URLs in Notion
- 📅 Automatic date tagging with today's date

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd conversation-transcriptor
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Set up environment variables by creating a `.env` file:
```bash
# Required for transcription
PYANNOTE_ACCESS_TOKEN=your_pyannote_token_here

# Required for Notion upload
NOTION_WRITE_API_TOKEN=your_notion_write_token_here
NOTION_TRANSCRIPTS_DATABASE_ID=your_database_id_here
```

## Available Commands

### 1. `url_to_notion` - Complete URL-to-Notion Workflow ⭐

**New!** Download audio from URL, transcribe it, and upload to Notion in one command.

```bash
url_to_notion
```

**Interactive prompts:**
- **Audio URL**: Direct link to MP3/WAV file 
- **Source URL**: Original webpage where you found the content (stored in Notion)
- **Title**: Title for both the Notion page and local filename
- **Model**: Whisper model to use (default: large-v3-turbo)

**Options:**
- `--skip_notion`: Skip Notion upload, just transcribe locally
- `--audio_url TEXT`: Provide audio URL directly
- `--source_url TEXT`: Provide source URL directly  
- `--title TEXT`: Provide title directly
- `--model_type`: Choose Whisper model

**Example:**
```bash
url_to_notion \
  --audio_url "https://example.com/podcast.mp3" \
  --source_url "https://example.com/podcast-page" \
  --title "My Podcast Episode"
```

### 2. `from_url` - URL to Transcript

Download and transcribe audio from URL (no Notion upload).

```bash
from_url
```

**Interactive prompts:**
- URL to MP3 file
- Whisper model selection
- Output filename

### 3. `from_wav` - Local WAV to Transcript

Transcribe a local WAV file.

```bash
from_wav
```

**Interactive prompts:**
- Path to WAV file
- Whisper model selection  
- Output filename

### Legacy Commands (Still Available)

For direct CLI usage with the original interface:

```bash
python click_app.py click-wav-to-transcript --wav_fname path/to/your/audio.wav
python click_app.py click-url-to-transcript --url "https://example.com/audio.mp3"
```

## Whisper Models

Available models (ordered by speed/accuracy tradeoff):
- `tiny`, `tiny.en` - Fastest, least accurate
- `base`, `base.en` - Fast
- `small`, `small.en` - Balanced
- `medium`, `medium.en` - Good accuracy
- `large-v1`, `large-v2`, `large` - High accuracy
- `large-v3-turbo` - **Recommended** - Best balance of speed and accuracy

## Notion Integration

The tool automatically:

1. **Detects Database Schema**: Finds available properties in your Notion database
2. **Smart Property Mapping**: 
   - Uses first available date property for today's date
   - Uses first available URL property for source links
   - Creates title property for transcript titles
3. **Safe Filename Generation**: 
   - Converts titles to filesystem-safe filenames
   - Handles long titles by truncating at word boundaries
   - Removes problematic characters while preserving readability
4. **Error Handling**: Gracefully falls back if properties don't exist

### Required Notion Setup

1. Create a database in Notion with these recommended properties:
   - **Title** (title property) - Auto-created
   - **Date** (date property) - Optional, will use today's date
   - **URL** (url property) - Optional, for source links

2. Get your integration token and database ID:
   - Create a Notion integration at https://developers.notion.com
   - Share your database with the integration
   - Copy the integration token and database ID to your `.env` file

## File Organization

The tool creates this directory structure:

```
data/
├── inputs/
│   ├── raw/      # Downloaded MP3 files
│   └── wav/      # Converted WAV files
├── outputs/      # Generated transcript files (.txt)
└── intermediate/ # Processing data (CSV files)
    ├── {filename}_whisper_{model}_segments.csv
    └── {filename}_speaker_segments.csv
```

## Technical Details

### How It Works

The tool uses a sophisticated two-step process:

1. **Speech Recognition**: Whisper processes the audio to extract text with precise timing
2. **Speaker Diarization**: Pyannote analyzes the audio to identify different speakers
3. **Intelligent Combination**: The system combines both outputs, matching text segments with speakers
4. **Post-processing**: Consecutive segments from the same speaker are merged for readability

### Models Used
- **Whisper**: OpenAI's speech recognition model
- **Pyannote**: Advanced speaker diarization system

### Prerequisites

1. **System Requirements**:
   - Python 3.8+
   - FFmpeg (for audio processing)
   - GPU recommended (but not required)

2. **Install FFmpeg**:
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`  
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org)

## Example Workflow

1. **Find a podcast/audio content** you want to transcribe
2. **Get the direct audio URL** (MP3/WAV download link)
3. **Run the command:**
   ```bash
   url_to_notion
   ```
4. **Provide the information:**
   - Audio URL: `https://example.com/episode.mp3`
   - Source URL: `https://example.com/podcast-page`
   - Title: `Interesting Podcast Episode`
5. **Wait for completion** - the tool will:
   - Download the audio
   - Convert to WAV format
   - Transcribe with speaker diarization
   - Upload to your Notion database

## Troubleshooting

### Notion Upload Issues
- Verify your `.env` file has correct tokens
- Check that your Notion integration has access to the database
- Run the test script: `python test_notion.py` (Cell 1) to check database properties

### Audio Download Issues
- Ensure the URL is a direct link to an audio file
- Check that the file format is supported (MP3, WAV, M4A, etc.)

### Transcription Issues  
- Verify your pyannote token is valid
- Try a smaller Whisper model if running out of memory
- Check that the audio file was downloaded correctly

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

## Development

The project uses:
- **Click** for CLI interface
- **Whisper** for transcription
- **pyannote** for speaker diarization  
- **Notion API** for database integration
- **pydub** for audio processing

### Testing

Run individual test cells in `test_notion.py` to verify Notion integration works correctly.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Future Ideas

- Extend to other formats (e.g. m4a)
- Allow YouTube Video transcription
- Use faster whisper to increase performance speed
- Use uv instead of pip
- Allow re-naming of speakers (e.g. SPEAKER_00 to "Barack Obama")
- Connect to Instapaper: -> skipped. It would require the full API which one can only use after one has registered an official app with instapaper


## License

MIT License - See LICENSE file for details