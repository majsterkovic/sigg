"""Private market-data snapshots live outside the source tree."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('SIGG_DATA_DIR', '.')).resolve()

def data_path(name):
    return DATA / name

def reference_path(name):
    local = DATA / name
    return local if local.exists() else ROOT / 'results' / name
