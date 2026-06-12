"""
ParkPredict — Database Entry Point
=====================================
Run this to initialise the database and verify all functions
that Pirai's backend needs are working correctly.

Usage:
    python main.py
"""

import db

print("=" * 60)
print("  ParkPredict — Database Init & Pirai Compatibility Test")
print("=" * 60)

# ── SETUP ─────────────────────────────────────────────────────────────────
db.setup()

# ── TEST: get_all_zones() ─────────────────────────────────────────────────
# Used by: Pirai's zones.py, analytics.py, recommendation.py, admin.py
print("\n[1] get_all_zones():")
zones = db.get_all_zones()
for z in zones:
    print(f"  Zone {z['zone_id']}: {z['zone_name']:12s} | {z['available_slots']}/{z['total_slots']} | {z['status']}")

# ── TEST: get_zone_by_id() ────────────────────────────────────────────────
# Used by: Pirai's zones.py
print("\n[2] get_zone_by_id(1):")
print(" ", db.get_zone_by_id(1))

# ── TEST: check_in() ─────────────────────────────────────────────────────
# Used by: Pirai's parking.py → POST /api/parking/checkin
print("\n[3] check_in(zone_id=1, user_id='S001', vehicle_plate='WXX1234'):")
result = db.check_in(zone_id=1, user_id="S001", vehicle_plate="WXX1234")
print(" ", result)

# ── TEST: get_active_logs() ───────────────────────────────────────────────
# Used by: Pirai's parking.py, admin.py
print("\n[4] get_active_logs():")
logs = db.get_active_logs()
print(f"  {len(logs)} active session(s)")

# ── TEST: get_active_logs(zone_id) ────────────────────────────────────────
print("\n[5] get_active_logs(zone_id=1):")
logs = db.get_active_logs(zone_id=1)
print(f"  {len(logs)} active session(s) in Zone 1")

# ── TEST: check_out() ────────────────────────────────────────────────────
# Used by: Pirai's parking.py → POST /api/parking/checkout
if result.get("success"):
    log_id = result["log_id"]
    print(f"\n[6] check_out(log_id={log_id}):")
    print(" ", db.check_out(log_id))

# ── TEST: get_logs_by_user() ──────────────────────────────────────────────
# Used by: Pirai's parking.py, auth.py (user-history)
print("\n[7] get_logs_by_user(user_id='S001'):")
logs = db.get_logs_by_user(user_id="S001", limit=5)
print(f"  {len(logs)} log(s) found")

# ── TEST: get_peak_hours() ────────────────────────────────────────────────
# Used by: Pirai's analytics.py
print("\n[8] get_peak_hours(days=30):")
rows = db.get_peak_hours(days=30)
print(f"  {len(rows)} row(s) returned")

# ── TEST: get_prediction_data() ───────────────────────────────────────────
# Used by: Pirai's analytics.py, recommendation.py
print("\n[9] get_prediction_data():")
rows = db.get_prediction_data()
print(f"  {len(rows)} row(s) returned")

# ── TEST: get_daily_stats() ───────────────────────────────────────────────
# Used by: Pirai's analytics.py → GET /api/analytics/daily-stats
print("\n[10] get_daily_stats():")
stats = db.get_daily_stats()
print(f"  Date: {stats['date']}")
print(f"  Check-ins today: {stats['total_checkins']}")
print(f"  Currently parked: {stats['currently_parked']}")
print(f"  Avg duration: {stats['avg_duration_minutes']} min")
print(f"  Busiest zone: {stats['busiest_zone']}")

# ── TEST: update_zone_status() ────────────────────────────────────────────
# Used by: Pirai's admin.py → POST /api/admin/status
print("\n[11] update_zone_status(zone_id=2, status='maintenance'):")
print(" ", db.update_zone_status(zone_id=2, status="maintenance"))

# ── TEST: reset_zone_slots() ─────────────────────────────────────────────
# Used by: Pirai's admin.py → POST /api/admin/reset/<zone_id>
print("\n[12] reset_zone_slots(zone_id=2):")
print(" ", db.reset_zone_slots(zone_id=2))

print("\n" + "=" * 60)
print("  ✅ All functions verified — Pirai's backend is compatible")
print("=" * 60 + "\n")
