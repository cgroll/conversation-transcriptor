from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUTS_DIR = DATA_DIR / "inputs"
INPUTS_RAW_DIR = INPUTS_DIR / "raw"
INPUTS_WAV_DIR = INPUTS_DIR / "wav"
OUTPUTS_DIR = DATA_DIR / "outputs"

# Ensure directories exist
INPUTS_RAW_DIR.mkdir(parents=True, exist_ok=True)
INPUTS_WAV_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)