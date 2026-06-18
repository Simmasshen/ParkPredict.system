"""
ParkPredict — Database Entry Point
Run this to initialise the database standalone.

Usage:
    cd database
    python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from db.schema     import create_tables
from db.seed       import seed_zones
from db.queries    import get_all_zones
from db.admin      import get_full_audit


def main():
    print("\n" + "="*50)
    print("  ParkPredict Database Setup")
    print("="*50 + "\n")

    print("[1/2] Creating tables...")
    create_tables()

    print("[2/2] Seeding default zones...")
    seed_zones()

    print("\n[OK] Database ready.")
    zones = get_all_zones()
    print(f"\nZones loaded ({len(zones)}):")
    for z in zones:
        print(f"  Zone {z['zone_id']}: {z['zone_name']} — {z['location']} ({z['total_slots']} slots)")

    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()
