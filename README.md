# ParkPredict — Database Project (Nitesh)

SQLite database layer for ParkPredict. Owns the schema, seed data, and all read/write logic for parking zones, check-in/check-out sessions, admin actions, and user accounts.

This project is consumed by the Flask backend (`backend/app/database.py` imports directly from `db/`), so it **must** be placed as a sibling folder to `backend/`, named exactly `database`.

---

## 1. Folder Structure

```
database/
├── main.py            ← standalone entry point (creates + seeds tables)
├── parkpredict.db      ← the SQLite database file (shared with backend)
└── db/
    ├── __init__.py     ← re-exports every function below for the backend to import
    ├── config.py       ← DB_PATH definition
    ├── connection.py   ← get_connection()
    ├── schema.py       ← create_tables()
    ├── seed.py         ← seed_zones()
    ├── operations.py   ← check_in(), check_out()
    ├── queries.py       ← get_all_zones(), get_active_logs(), get_logs_by_user(), etc.
    └── admin.py         ← update_zone_status(), reset_zone_slots(), get_admin_logs(), etc.
```

Must sit alongside the backend project:

```
parkpredict/
├── backend/
└── database/   ← this project
```

---

## 2. Setup

### Standalone (creates/seeds the database without running Flask)

```bash
cd parkpredict/database
python main.py
```

Output:
```
[1/2] Creating tables...
[2/2] Seeding default zones...
[OK] Database ready.

Zones loaded (3):
  Zone 1: Zone A — FCI Parking – Faculty of Computing & Informatics (120 slots)
  Zone 2: Zone B — FOM Parking – Faculty of Management (80 slots)
  Zone 3: Zone C — DTC Parking – Chancellor Hall / DTC (100 slots)
```

### Via the backend

No manual step needed — `backend/app/database.py` calls `create_tables()` and `seed_zones()` automatically on Flask startup. Re-running is always safe: seeding uses `INSERT OR IGNORE`, so existing zones are never duplicated or overwritten.

---

## 3. Schema

### `parking_zones`
| Column | Type | Notes |
|---|---|---|
| `zone_id` | INTEGER PK | Auto-increment |
| `zone_name` | TEXT | Unique (e.g. "Zone A") |
| `location` | TEXT | Display name (e.g. "FCI Parking – Faculty of Computing & Informatics") |
| `total_slots` | INTEGER | > 0 |
| `available_slots` | INTEGER | >= 0 |
| `status` | TEXT | `available` \| `full` \| `maintenance` |
| `last_updated` | DATETIME | Auto-updated on every write |

### `parking_logs`
| Column | Type | Notes |
|---|---|---|
| `log_id` | INTEGER PK | Auto-increment |
| `zone_id` | INTEGER | FK → `parking_zones` |
| `user_id` | TEXT | Student ID |
| `vehicle_plate` | TEXT | |
| `check_in_time` | DATETIME | |
| `check_out_time` | DATETIME | `NULL` = session still active |
| `duration_minutes` | INTEGER | Set on checkout |
| `day_of_week` | TEXT | e.g. "Monday" |
| `hour_of_day` | INTEGER | 0–23 |

### `admin_logs`
| Column | Type | Notes |
|---|---|---|
| `action_id` | INTEGER PK | |
| `zone_id` | INTEGER | FK → `parking_zones`, nullable |
| `action` | TEXT | e.g. `STATUS_CHANGE`, `EMERGENCY_RESET`, `CAPACITY_UPDATE` |
| `old_value` / `new_value` | TEXT | |
| `performed_by` | TEXT | Defaults to `"admin"` |
| `action_time` | DATETIME | |

### `zone_capacity_history`
| Column | Type | Notes |
|---|---|---|
| `history_id` | INTEGER PK | |
| `zone_id` | INTEGER | FK → `parking_zones` |
| `available_slots` / `total_slots` | INTEGER | Snapshot taken on every check-in/check-out |
| `recorded_at` | DATETIME | |

### `users`
| Column | Type | Notes |
|---|---|---|
| `user_id` | INTEGER PK | |
| `username` | TEXT | Unique |
| `password_hash` | TEXT | |
| `student_id` | TEXT | |
| `email` | TEXT | |
| `role` | TEXT | `user` \| `admin` |
| `created_at` | DATETIME | |

---

## 4. Default Seed Data

| zone_id | zone_name | location | total_slots |
|---|---|---|---|
| 1 | Zone A | FCI Parking – Faculty of Computing & Informatics | 120 |
| 2 | Zone B | FOM Parking – Faculty of Management | 80 |
| 3 | Zone C | DTC Parking – Chancellor Hall / DTC | 100 |

Zone IDs 1/2/3 correspond to FCI/FOM/DTC respectively — this ordering is depended on by both the backend's zone-name lookup and the frontend's zone mapping, so don't reorder `ZONES` in `seed.py` without updating those too.

---

## 5. Function Reference

All functions below are re-exported from `db/__init__.py` and imported directly by the backend.

### `schema.py`
- `create_tables()` — creates all 5 tables + indexes, `IF NOT EXISTS` (safe to call repeatedly)

### `seed.py`
- `seed_zones()` — inserts the 3 default zones, `INSERT OR IGNORE`

### `operations.py`
- `check_in(zone_id, user_id, vehicle_plate=None) -> dict`
  Validates zone has capacity, blocks double check-in per user, inserts log, decrements `available_slots`, records a capacity snapshot.
  Returns `{ success, log_id, zone_name, check_in, slots_left }` or `{ success: False, error }`.
- `check_out(log_id) -> dict`
  Closes the open log, calculates `duration_minutes`, restores the zone's slot, records a capacity snapshot.
  Returns `{ success, log_id, zone_name, check_out, duration_minutes }` or `{ success: False, error }`.

### `queries.py`
- `get_all_zones() -> list` — live status of every zone
- `get_zone_by_id(zone_id) -> dict | None`
- `get_active_logs(zone_id=None) -> list` — currently-parked vehicles, optionally filtered by zone
- `get_logs_by_user(user_id, limit=20) -> list` — a user's parking history
- `get_peak_hours(days=30) -> list` — check-in counts grouped by zone/day/hour
- `get_prediction_data() -> list` — avg occupancy per zone/day/hour, for the prediction model
- `get_daily_stats(date=None) -> dict` — dashboard summary for a given day (defaults to today)

### `admin.py`
- `update_zone_status(zone_id, status, performed_by="admin") -> dict`
- `reset_zone_slots(zone_id, performed_by="admin") -> dict` — restores full capacity and force-closes any dangling active sessions
- `update_zone_capacity(zone_id, new_total, performed_by="admin") -> dict`
- `get_admin_logs(zone_id=None, limit=50) -> list` — audit trail
- `get_capacity_history(zone_id, hours=24) -> list` — slot snapshots over time, for charts
- `get_full_audit(limit=100) -> list` — all admin actions across all zones

---

## 6. Notes

- `db/config.py` resolves `DB_PATH` relative to its own file location (`database/db/../parkpredict.db`), so `parkpredict.db` must stay directly inside `database/`, not inside `database/db/`.
- Every write path (`check_in`, `check_out`, all of `admin.py`) wraps its transaction in try/except/finally with `conn.rollback()` on error and `conn.close()` always — safe to call concurrently from Flask's threaded dev server.
- If sessions get stuck as "active" (e.g. a client never sent the checkout request), use `reset_zone_slots(zone_id)` to force-close them and restore the zone's slot count.
