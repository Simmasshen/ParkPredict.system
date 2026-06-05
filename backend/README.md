# ParkPredict — Backend
**Owner:** Pirai
**Tech:** Python · Flask · Pandas

---

## Folder Structure
```
backend/
├── app.py                        ← Run this to start the server
├── requirements.txt
└── app/
    ├── __init__.py               ← App factory + all blueprints registered
    ├── database.py               ← Bridge to Nitesh's database
    ├── routes/
    │   ├── zones.py              ← GET  /api/zones/
    │   ├── parking.py            ← POST /api/parking/checkin|checkout
    │   ├── analytics.py          ← GET  /api/analytics/
    │   ├── admin.py              ← GET/POST /api/admin/
    │   ├── recommendation.py     ← GET  /api/recommendation/
    │   └── auth.py               ← POST /api/auth/register|login|logout
    └── services/
        ├── prediction.py         ← Pandas prediction logic
        ├── analytics.py          ← Pandas peak hours & summary
        ├── recommendation.py     ← Best zone decision logic
        └── auth.py               ← User table + password hashing
```

---

## Setup
```bash
pip install -r requirements.txt
python app.py
# Server runs at http://localhost:5000
```

---

## All API Endpoints

### Zones
| Method | URL | Description |
|---|---|---|
| GET | `/api/zones/` | All zones live status |
| GET | `/api/zones/<zone_id>` | Single zone |

### Parking
| Method | URL | Body | Description |
|---|---|---|---|
| POST | `/api/parking/checkin` | `{ zone_id, user_id, vehicle_plate }` | Check in |
| POST | `/api/parking/checkout` | `{ log_id }` | Check out |
| GET | `/api/parking/active` | — | All active sessions |
| GET | `/api/parking/active/<zone_id>` | — | Active by zone |
| GET | `/api/parking/history/<user_id>` | — | User history |

### Analytics
| Method | URL | Description |
|---|---|---|
| GET | `/api/analytics/peak-hours?days=30` | Peak hour chart data |
| GET | `/api/analytics/prediction` | Availability probability |
| GET | `/api/analytics/summary` | Dashboard summary |

### Admin
| Method | URL | Description |
|---|---|---|
| GET | `/api/admin/stats` | Summary stats |
| GET | `/api/admin/zones` | All zones for admin |
| GET | `/api/admin/logs` | Active sessions |
| POST | `/api/admin/reset/<zone_id>` | Emergency reset |
| POST | `/api/admin/status` | Update zone status |

### Recommendation
| Method | URL | Description |
|---|---|---|
| GET | `/api/recommendation/` | Best zone right now |
| GET | `/api/recommendation/?user_id=S001` | Best zone for user |

### Auth
| Method | URL | Body | Description |
|---|---|---|---|
| POST | `/api/auth/register` | `{ username, password, student_id }` | Register |
| POST | `/api/auth/login` | `{ username, password }` | Login |
| POST | `/api/auth/logout` | — | Logout |
| GET | `/api/auth/me` | — | Current user |
| GET | `/api/auth/user-history` | — | Parking history |
