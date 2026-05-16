import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
DB_NAME = "kompost.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.yaml")