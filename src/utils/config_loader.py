## config_loader.py
import json
import os
from typing import Dict, Any

def load_config(config_type: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_type: Either 'client' or 'server'
        
    Returns:
        Dictionary containing configuration values
    """
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(base_path, "config", f"{config_type}_config.json")
    
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in configuration file: {config_path}")