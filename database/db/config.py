"""
ParkPredict — Database Configuration
=====================================
Central place for all database settings.
Change DB_PATH here to move the database file.
"""

import os

# Path to the SQLite database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "parkpredict.db")
DB_PATH  = os.path.normpath(DB_PATH)
