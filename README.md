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
