import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Data directory
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Models file
MODELS_FILE = DATA_DIR / 'models.json'

# Static directory
STATIC_DIR = BASE_DIR / 'static'
STATIC_DIR.mkdir(exist_ok=True)

# Site configuration
SITE_NAME = 'AI Models Directory'
SITE_URL = 'https://raosalman504.github.io/aimodelsdirectory'

# Scraping configuration
SCRAPE_INTERVAL_MINUTES = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
