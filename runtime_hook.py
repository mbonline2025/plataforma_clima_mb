import sys
import os
from pathlib import Path

def fix_metadata():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        metadata_path = Path(base_path) / 'importlib_metadata'
        if not metadata_path.exists():
            import importlib_metadata
            source_path = Path(importlib_metadata.__file__).parent
            os.system(f'cp -r {source_path} {metadata_path}')

fix_metadata()
