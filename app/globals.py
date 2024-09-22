import os

def get_root_dir() -> str:
    return os.path.dirname(os.path.dirname(__file__))