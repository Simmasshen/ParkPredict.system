# ParkPredict – MMU Cyberjaya (Frontend_Bala)

Smart parking web app for MMU Cyberjaya — shows real-time slot availability across campus parking zones, lets students check in/out of a zone, and predicts occupancy using historical peak-hour data.

This branch contains the **frontend**: static pages, styling, and client-side logic that talk to a Flask backend API.

---

## Features

| Page | File | What it does |
|---|---|---|
| Home | `templates/index.html` | Landing page with live slot counts per zone |
| Login / Register | `templates/login.html`, `templates/register.html` | Student authentication forms (password strength check, show/hide password) |
| Check In / Out | `templates/checkin.html` | Start/end a parking session for a zone; auto checks out at 9 PM campus closing time |
| Campus Map | `templates/map.html` | Visual map with live availability per zone (FCI / FOM / DTC) |
| Predict | `templates/predict.html` | Occupancy prediction for a chosen day/hour, using either the live API or a local peak-hour model as fallback |
| Analytics | `templates/analytics.html` | Hourly occupancy charts and heatmaps |
| Admin | `templates/admin.html` | Session/activity overview for staff |

---

## Tech Stack

- Vanilla HTML / CSS / JavaScript (no framework/build step — just static files)
- [Chart.js](https://www.chartjs.org/) for charts on the Analytics and Predict pages
- Flask backend (separate branch/service) providing the JSON API this frontend calls

---

## Folder Structure

```
frontend/
├── static/
│   ├── css/          # style.css (main site), auth.css (login/register pages)
│   ├── img/           # logo, campus photo
│   └── js/
│       ├── data.js      # API calls + mock fallback data + zone name mapping
│       ├── checkin.js    # check-in/out session logic, timers, activity table
│       ├── auth.js      # login/register form behaviour
│       ├── map.js       # campus map zone rendering
│       ├── predict.js    # prediction page logic
│       ├── analytics.js  # charts for analytics page
│       └── main.js      # shared/general page logic
└── templates/         # HTML pages (Flask Jinja templates)
```

---

## Running Locally

This is a set of Flask templates, so it's meant to be served by the Flask backend rather than opened directly as static HTML (some pages use Jinja syntax).

1. Make sure the backend (Flask API) is running and reachable.
2. Update `BASE_URL` in `static/js/data.js` to point at your backend, e.g.:
   ```js
   const BASE_URL = "http://127.0.0.1:5000";
   ```
3. Run the Flask app and open the page it serves (typically `http://127.0.0.1:5000/`).

If the backend is unreachable, most pages fall back to local mock data (`ZONES_MOCK`, `SESSIONS_DATA`, `PEAK_MODEL` in `data.js`) so the UI still renders for demo purposes.

---

## Expected Backend API

The frontend expects the following endpoints from the Flask backend:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/zones/` | Returns current slot counts per zone |
| GET | `/api/recommendation/?day=&hour=&zone=` | Returns predicted occupancy for a given day/hour/zone |
| GET | `/api/parking/active` | Returns currently active parking sessions |
| POST | `/api/parking/checkin` | Starts a session — body: `{ zone_id, user_id, vehicle_plate }` |
| POST | `/api/parking/checkout` | Ends a session — body: `{ log_id }` |

Zone name ↔ ID mapping used by the frontend: `FCI → 1`, `FOM → 2`, `DTC → 3` (see `ZONE_ID_MAP` in `data.js`).

---

## Notes

- Auto checkout triggers automatically at 9 PM (campus closing time), with a warning shown at 8:45 PM.
- Check-in is blocked after 9 PM.
- `apiCheckIn()` must return the parsed JSON response (containing the session/log ID) — without it, the checkout flow has no session ID to send to the backend, so sessions never get closed server-side. This was previously a bug and has been fixed in `data.js`.
