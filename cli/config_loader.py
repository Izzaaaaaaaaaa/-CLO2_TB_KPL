import json
import os
from env_loader import get_env

def load_api_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Api.json")
    with open(config_path, "r") as f:
        return json.load(f)

def get_config(key, default=None):
    """
    Mendapatkan nilai konfigurasi API dari environment variables.

    Args:
        key: Kunci konfigurasi API
        default: Nilai default jika kunci tidak ditemukan

    Returns:
        Nilai konfigurasi atau nilai default jika tidak ditemukan
    """
    return get_env(key, default)
