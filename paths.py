from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
INPUTS_DIR = BASE_DIR / "inputs"
INPUTS_RAW_DIR = INPUTS_DIR / "raw"
INPUTS_WAV_DIR = INPUTS_DIR / "wav"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure directories exist
INPUTS_RAW_DIR.mkdir(parents=True, exist_ok=True)
INPUTS_WAV_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)