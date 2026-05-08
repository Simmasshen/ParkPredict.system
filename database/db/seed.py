"""
ParkPredict — Seed Data
=========================
Populates parking_zones with default MMU Cyberjaya zones.
Uses INSERT OR IGNORE so it is safe to run multiple times.
"""

from db.connection import get_connection

# Default parking zones for MMU Cyberjaya
ZONES = [
    ("Zone A", "FCI Parking", 120),
    ("Zone B", "FOM Parking", 80),
    ("Zone C", "DTC Parking", 100),
]


def seed_zones():
    """Insert default zones if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    for zone_name, location, total in ZONES:
        cursor.execute("""
            INSERT OR IGNORE INTO parking_zones
                (zone_name, location, total_slots, available_slots)
            VALUES (?, ?, ?, ?)
        """, (zone_name, location, total, total))

    conn.commit()
    conn.close()
    print("[Seed] Parking zones seeded (or already exist).")
