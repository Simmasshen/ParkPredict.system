"""
ParkPredict — db package
=========================
Import everything from one place:

    from db import setup, check_in, check_out, get_all_zones, ...
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
)
from db.admin import update_zone_status, reset_zone_slots


def setup():
    """Initialise the database: create tables + seed default zones."""
    create_tables()
    seed_zones()


__all__ = [
    "setup",
    "create_tables",
    "seed_zones",
    "check_in",
    "check_out",
    "get_all_zones",
    "get_zone_by_id",
    "get_active_logs",
    "get_logs_by_user",
    "get_peak_hours",
    "get_prediction_data",
    "update_zone_status",
    "reset_zone_slots",
]
