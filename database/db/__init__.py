"""
ParkPredict — db package
=========================
Exports every function Pirai's backend needs.

Pirai imports from here via database.py:
  - create_tables()
  - seed_zones()
  - check_in(), check_out()
  - get_all_zones(), get_zone_by_id()
  - get_active_logs(), get_logs_by_user()
  - get_peak_hours(), get_prediction_data()
  - get_daily_stats()
  - update_zone_status(), reset_zone_slots()
"""

from db.schema     import create_tables
from db.seed       import seed_zones
from db.operations import check_in, check_out
from db.queries    import (
    get_all_zones,
    get_zone_by_id,
    get_active_logs,
    get_logs_by_user,
    get_peak_hours,
    get_prediction_data,
    get_daily_stats,
)
from db.admin import (
    update_zone_status,
    reset_zone_slots,
    update_zone_capacity,
    get_admin_logs,
    get_capacity_history,
    get_full_audit,
)


def setup():
    """Initialise the database: create tables + seed default zones."""
    create_tables()
    seed_zones()


__all__ = [
    # Setup
    "setup",
    "create_tables",
    "seed_zones",
    # Operations — used by Pirai's parking.py
    "check_in",
    "check_out",
    # Queries — used by Pirai's zones.py, parking.py, analytics.py, recommendation.py
    "get_all_zones",
    "get_zone_by_id",
    "get_active_logs",
    "get_logs_by_user",
    "get_peak_hours",
    "get_prediction_data",
    "get_daily_stats",
    # Admin — used by Pirai's admin.py
    "update_zone_status",
    "reset_zone_slots",
    "update_zone_capacity",
    "get_admin_logs",
    "get_capacity_history",
    "get_full_audit",
]