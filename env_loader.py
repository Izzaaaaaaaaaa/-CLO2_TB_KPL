# ======================================
# AutoTicket CLI Project
# ======================================
# File: env_loader.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env(key, default=None):
    """
    Mendapatkan nilai dari environment variable.

    Args:
        key (str): Kunci environment variable
        default (any, optional): Nilai default jika kunci tidak ditemukan

    Returns:
        any: Nilai environment variable atau default jika tidak ada
    """
    return os.environ.get(key, default)

