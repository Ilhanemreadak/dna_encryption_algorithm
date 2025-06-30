import os
from pathlib import Path

class Config:
    ROOT                = Path(__file__).parent
    UPLOAD_FOLDER       = ROOT / 'static' / 'uploads'
    ANALYZE_FOLDER      = 'static/analysis'
    EXAMPLES_FOLDER     = ROOT / 'static' / 'examples'

    ALLOWED_EXT         = {'png'}
    MAX_CONTENT_LENGTH  = 64 * 1024 * 1024        # 64 MB

    MAX_CROP_SIZE       = 2_000
    MIN_NOISE_STRENGTH  = 1e-5
    MAX_NOISE_STRENGTH  = 1.0
