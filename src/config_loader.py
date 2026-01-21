import configparser
import os
from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).parent.parent

def load_config():
    config = configparser.ConfigParser()
    config_path = ROOT_DIR / 'config.ini'
    
    if config_path.exists():
        config.read(config_path)
    else:
        # Fallback to defaults
        config['DEFAULT'] = {
            'output_dir': 'output',
            'log_dir': 'logs',
            'temp_dir': 'tmp'
        }
        config['server'] = {
            'port': '8000',
            'host': '0.0.0.0'
        }
        config['video'] = {
            'default_resolution': 'hd',
            'max_duration': '300'
        }
    
    return config

# Global config instance
settings = load_config()

def get_output_dir():
    path = settings.get('DEFAULT', 'output_dir')
    return ROOT_DIR / path

def get_log_dir():
    path = settings.get('DEFAULT', 'log_dir')
    return ROOT_DIR / path
