# Conversation Transcriptor

A Python toolkit for downloading audio files, transcribing them using Whisper with speaker diarization, and uploading transcripts to Notion.

## Quick Start (If Already Set Up)

### How to Transcribe a Podcast from Listen Notes

1. **Find your podcast**: Go to [Listen Notes](https://www.listennotes.com)
2. **Search for the podcast** you want to transcribe
3. **Get the audio URL**: Click "Download Audio" to get the direct MP3/WAV link
4. **Copy the page URL**: Save the Listen Notes page URL for reference
5. **Create a meaningful title**: Come up with a descriptive title for your transcript

**Example workflow:**
```bash
url_to_notion
```

When prompted, provide:
- **Audio URL**: `https://content.production.cdn.art19.com/episodes/example.mp3`
- **Source URL**: `https://www.listennotes.com/podcasts/show-name/episode-title`
- **Title**: `Tech Talk with John Doe - AI in Healthcare`

### Complete Command-Line Usage

```bash
# One-command transcription with all parameters
url_to_notion \
  --audio_url "https://example.com/podcast.mp3" \
  --source_url "https://listennotes.com/podcasts/..." \
  --title "My Podcast Episode"

# Just transcribe locally (skip Notion upload)
url_to_notion --skip_notion

# Use different Whisper model for speed
url_to_notion --model_type base
```

## Installation & Setup

### 1. Install the Project

```bash
git clone <repository-url>
cd conversation-transcriptor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 2. Required Environment Variables

Create a `.env` file with these tokens:

```bash
# Required for transcription (get from HuggingFace)
PYANNOTE_ACCESS_TOKEN=your_huggingface_token_here

# Required for Notion upload (get from Notion integrations)
NOTION_WRITE_API_TOKEN=your_notion_integration_token_here
NOTION_TRANSCRIPTS_DATABASE_ID=your_notion_database_id_here
```

**Getting tokens:**
- **HuggingFace Token**: Visit [HuggingFace](https://huggingface.co), create account, generate token, accept pyannote/speaker-diarization terms
- **Notion Token**: Create integration at [Notion Developers](https://developers.notion.com), share database with integration

### 3. System Requirements

- **Python 3.8+**
- **FFmpeg** (for audio processing):
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`  
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org)

## What This Project Does

The Conversation Transcriptor combines two AI models to create detailed transcripts:

### 🧠 **Two-Step AI Process**
1. **Speech Recognition**: OpenAI's Whisper extracts text with precise timing
2. **Speaker Diarization**: Pyannote identifies different speakers ("who said what")
3. **Smart Combination**: Matches text segments with speakers
4. **Auto-Upload**: Creates organized Notion pages with metadata

### 📊 **Features**
- 🎵 Download audio from any URL
- 🗣️ Identify different speakers automatically  
- 📝 Generate timestamped transcripts
- 📚 **Multi-part uploads** - automatically splits long transcripts across multiple Notion pages
- 🔗 Link back to original sources
- 📅 Automatic date tagging

### 🏗️ **File Organization**
```
data/
├── inputs/
│   ├── raw/         # Downloaded MP3 files
│   └── wav/         # Converted WAV files  
├── outputs/         # Final transcript files
└── intermediate/    # Processing data (CSV)
```

## Alternative Commands

### Other Available Commands

```bash
# Transcribe from URL (no Notion upload)
from_url

# Transcribe local audio file
from_wav

# Legacy direct commands
python click_app.py click-wav-to-transcript --wav_fname audio.wav
python click_app.py click-url-to-transcript --url "https://example.com/audio.mp3"
```

### Available Whisper Models

Choose based on your speed vs accuracy needs:
- `tiny`, `tiny.en` - Fastest, least accurate
- `base`, `base.en` - Good for quick transcripts  
- `small`, `small.en` - Balanced option
- `medium`, `medium.en` - Good accuracy
- `large-v1`, `large-v2`, `large` - High accuracy
- `large-v3-turbo` - **Recommended** - Best balance of speed and accuracy

## Future Ideas

- Extend to other formats (e.g. m4a)
- Allow YouTube Video transcription
- Use faster whisper to increase performance speed
- Use uv instead of pip
- Allow re-naming of speakers (e.g. SPEAKER_00 to "Barack Obama")
- Connect to Instapaper: -> skipped. It would require the full API which one can only use after one has registered an official app with instapaper

## License

MIT License - See LICENSE file for details