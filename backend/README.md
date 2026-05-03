# ParkPredict — Backend
**Owner:** Pirai  
**Tech:** Python · Flask · Pandas

---

## Folder Structure
```
backend/
├── app.py              ← Run this to start the server
├── requirements.txt
├── .gitignore
└── app/
    ├── __init__.py         ← App factory + CORS
    ├── database.py         ← Bridge to Nitesh's database
    ├── routes/
    │   ├── zones.py        ← GET /api/zones/
    │   ├── parking.py      ← POST /api/parking/checkin|checkout
    │   └── analytics.py    ← GET /api/analytics/
    └── services/
        ├── prediction.py   ← Pandas prediction logic
        └── analytics.py    ← Pandas peak hours & summary
```

---

## Setup
```bash
pip install -r requirements.txt
python app.py
# Server runs at http://localhost:5000
```

---

## Connecting to Nitesh's Database (via GitHub)
See the full GitHub guide in the shared repo's README.  
After cloning, your folder must look like:
```
parkpredict/
├── backend/     ← this project
└── database/    ← Nitesh's project
```
Then `app/database.py` will automatically find Nitesh's `db/` folder.
