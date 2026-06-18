"""
ParkPredict — Seed Data
Populates parking_zones with default MMU Cyberjaya zones.
"""

from db.connection import get_connection

ZONES = [
    ("Zone A", "FCI Parking – Faculty of Computing & Informatics", 120),
    ("Zone B", "FOM Parking – Faculty of Management", 80),
    ("Zone C", "DTC Parking – Chancellor Hall / DTC", 100),
]


def seed_zones():
    """Insert default zones if they don't already exist."""
    conn   = get_connection()
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
