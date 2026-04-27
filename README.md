# 🅿️ ParkPredict – MMU Cyberjaya Smart Parking Tracker

A full-stack smart campus parking system with real-time availability, interactive maps, check-in/out, analytics, and AI-powered predictions.

---

## 📁 Project Structure

```
parkpredict/
├── app.py                      ← Flask backend (Python)
├── static/
│   ├── css/
│   │   └── style.css           ← All styles (dark theme)
│   └── js/
│       ├── data.js             ← Shared mock data & helpers
│       ├── main.js             ← Dashboard logic
│       ├── map.js              ← Campus map logic
│       ├── checkin.js          ← Check in/out logic
│       ├── analytics.js        ← Charts & analytics
│       └── predict.js          ← Prediction engine
└── templates/
    ├── index.html              ← Dashboard
    ├── map.html                ← Campus Map
    ├── checkin.html            ← Check In / Out
    ├── analytics.html          ← Analytics & Graphs
    └── predict.html            ← Prediction Tool
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

## 🚀 Setup Instructions

### 1. Install Requirements
```bash
pip install flask pandas
```

### 2. Run the App
```bash
cd parkpredict
python app.py
```

### 3. Open in Browser
```
http://localhost:5000
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

## 🖥️ Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Live zone status, trend chart, quick predict |
| Campus Map | `/map` | Interactive SVG map of MMU Cyberjaya |
| Check In/Out | `/checkin` | Register parking sessions |
| Analytics | `/analytics` | Charts, heatmaps, trends |
| Predictor | `/predict` | AI-style availability forecast |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Data | Pandas (extend for ML) |
| Fonts | Bebas Neue, DM Sans, JetBrains Mono |

---

## 🎨 Frontend Features

- **Dark industrial theme** with blue accent colors
- **Sticky navbar** with live clock
- **Animated zone cards** with color-coded availability (green/yellow/red)
- **SVG Campus Map** of MMU Cyberjaya with clickable parking zones
- **Live occupancy bars** updating every 30 seconds (simulated)
- **Chart.js graphs**: Line, Bar, Doughnut, Weekly Heatmap
- **Check In/Out** with live session timer
- **Responsive** — works on mobile & tablet

---

## 🔌 Connecting Frontend to Backend

The frontend currently uses **simulated data** in `data.js`. To connect to the real Flask API:

In each JS file, replace mock data with:
```javascript
// Example: load zones from Flask
const response = await fetch('/api/zones');
const zones = await response.json();
```

API Endpoints:
- `GET /api/zones` – Current zone availability
- `POST /api/checkin` – Start a parking session
- `POST /api/checkout` – End a parking session
- `GET /api/sessions` – Today's sessions
- `GET /api/predict?day=Monday&hour=9` – Prediction

---

## 👥 Team Notes

- **Frontend** (your part): `templates/` + `static/`
- **Backend**: `app.py` + database setup
- **Data/ML**: `pandas` processing + prediction model in `app.py`

---

*ParkPredict · MMU Cyberjaya · 2025*
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
