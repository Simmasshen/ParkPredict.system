# ParkPredict — Database Module

**Role:** Nitesh (Database)
**Tech:** Python · SQLite · No external dependencies

---

## Folder Structure

```
parkpredict/
├── main.py              ← Run this to initialise & test
├── parkpredict.db       ← SQLite file (auto-created on first run)
└── db/
    ├── __init__.py      ← Clean public API (import everything from here)
    ├── config.py        ← Database path / settings
    ├── connection.py    ← get_connection() helper
    ├── schema.py        ← CREATE TABLE statements
    ├── seed.py          ← Default MMU Cyberjaya zones
    ├── operations.py    ← check_in() and check_out()
    ├── queries.py       ← All SELECT queries
    └── admin.py         ← Admin utilities (reset, status override)
```

---

## Quick Start

```bash
python main.py
```

This creates `parkpredict.db`, seeds the 5 default zones, and runs a test check-in/check-out.

---

## How Pirai (Backend) Uses This

```python
from db import setup, check_in, check_out, get_all_zones, get_prediction_data

setup()   # call once on app startup

# Check-in
result = check_in(zone_id=1, user_id="S001", vehicle_plate="WXX1234")

# Check-out
result = check_out(log_id=1)

# Live zone status (for Bala's map)
zones = get_all_zones()

# Prediction data (feed into Pandas)
data = get_prediction_data()
```

---

## Tables

### `parking_zones`
| Column | Type | Description |
|---|---|---|
| zone_id | INTEGER PK | Auto-increment |
| zone_name | TEXT | e.g. "Zone A" |
| location | TEXT | e.g. "Near Library Block" |
| total_slots | INTEGER | Maximum capacity |
| available_slots | INTEGER | Live count |
| status | TEXT | available / full / maintenance |
| last_updated | DATETIME | Auto-updated on change |

### `parking_logs`
| Column | Type | Description |
|---|---|---|
| log_id | INTEGER PK | Auto-increment |
| zone_id | INTEGER FK | References parking_zones |
| user_id | TEXT | Student ID or session token |
| vehicle_plate | TEXT | Optional |
| check_in_time | DATETIME | Set on check-in |
| check_out_time | DATETIME | NULL while parked |
| duration_minutes | INTEGER | Calculated on check-out |
| day_of_week | TEXT | e.g. "Monday" |
| hour_of_day | INTEGER | 0–23, for peak analysis |

---

## Available Functions

| Function | File | Used by |
|---|---|---|
| `setup()` | `__init__.py` | Pirai — app startup |
| `check_in(zone_id, user_id, plate)` | `operations.py` | Pirai — POST /checkin |
| `check_out(log_id)` | `operations.py` | Pirai — POST /checkout |
| `get_all_zones()` | `queries.py` | Bala — parking map |
| `get_zone_by_id(zone_id)` | `queries.py` | Pirai — single zone API |
| `get_active_logs(zone_id)` | `queries.py` | Pirai — live occupancy |
| `get_logs_by_user(user_id)` | `queries.py` | Pirai — user history |
| `get_peak_hours(days)` | `queries.py` | Pirai — chart data |
| `get_prediction_data()` | `queries.py` | Pirai — Pandas model |
| `update_zone_status(zone_id, status)` | `admin.py` | Admin panel |
| `reset_zone_slots(zone_id)` | `admin.py` | Emergency reset |
