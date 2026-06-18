"""
ParkPredict — Database Configuration
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "parkpredict.db")
DB_PATH  = os.path.normpath(DB_PATH)
