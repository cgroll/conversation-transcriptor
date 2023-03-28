# Conversation transcriptor

This is a tool that let's you extract a conversation in an audio file into a transcription text.

## Transcription model

The tool consists of a logic that combines the output of two awesome AI models:

- whisper
- pyannote

## Usage

In order to run the tool, several components need to be set up correctly:

- the tool requires external libraries like ffmpeg to manipulate audio files
- all Python package requirements
- pyannote can only be used with an appropriate authentication token from HuggingFace
- to reduce the duration of the inference one ideally has access to a GPU

The easiest way to access the tool is by:

- creating a pyannote token
- using the Google Colab notebook


## Installation

In order to use the click command app, the package needs to be installed locally with:

```
pip install --editable .
```


## Application with Click

To see a list of available click commands, use:
```
python click_app.py --help
```

To see more details about a given click command, use e.g.:
```
python click_app.py click-wav-to-transcript --help
```

Alternatively, commands are also listed with shortcuts in `setup.py`. E.g.:
```
from_wav --help
```

