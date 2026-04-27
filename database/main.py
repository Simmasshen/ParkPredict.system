"""
ParkPredict — Main Entry Point
================================
Run this file to initialise the database and verify everything works.

Usage:
    python main.py
"""

import db

# ── 1. SETUP ──────────────────────────────────────────────────────────────
print("=" * 55)
print("  ParkPredict — Database Init & Test")
print("=" * 55)

db.setup()   # creates tables + seeds zones

# ── 2. LIVE STATUS ────────────────────────────────────────────────────────
print("\n[Zones] Live status:")
for z in db.get_all_zones():
    print(f"  {z['zone_name']:10s} | {z['available_slots']}/{z['total_slots']} slots | {z['status']}")

# ── 3. CHECK-IN ───────────────────────────────────────────────────────────
print("\n[Test] Check-in — Zone 1, user S001 ...")
result = db.check_in(zone_id=1, user_id="S001", vehicle_plate="WXX1234")
print(" ", result)

# ── 4. CHECK-OUT ──────────────────────────────────────────────────────────
if result.get("success"):
    log_id = result["log_id"]
    print(f"\n[Test] Check-out — log_id={log_id} ...")
    print(" ", db.check_out(log_id))

# ── 5. PEAK HOURS ─────────────────────────────────────────────────────────
print("\n[Analytics] Peak hours (first 3 rows):")
for row in db.get_peak_hours()[:3]:
    print(" ", row)

# ── 6. PREDICTION DATA ────────────────────────────────────────────────────
print("\n[Prediction] Avg occupancy data (first 3 rows):")
for row in db.get_prediction_data()[:3]:
    print(" ", row)

print("\n[Done] Database is ready.\n")
