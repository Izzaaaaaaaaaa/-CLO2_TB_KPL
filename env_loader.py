# ======================================
# AutoTicket CLI Project
# ======================================
# File: env_loader.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env(key, default=None):

    return os.environ.get(key, default)
