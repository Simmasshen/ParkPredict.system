# ParkPredict — Database
**Owner:** Nitesh  
**Tech:** Python · SQLite

---

## Folder Structure
```
database/
├── main.py        ← Run to initialise & test the database
├── .gitignore     ← parkpredict.db is excluded from GitHub
└── db/
    ├── config.py      ← DB file path setting
    ├── connection.py  ← get_connection() helper
    ├── schema.py      ← CREATE TABLE statements
    ├── seed.py        ← Default MMU zones
    ├── operations.py  ← check_in(), check_out()
    ├── queries.py     ← All SELECT queries
    ├── admin.py       ← Admin utilities
    └── __init__.py    ← Package exports
```

---

## Quick Start
```bash
python main.py
```

---

## GitHub Note
The `parkpredict.db` file is in `.gitignore` — it will NOT be pushed to GitHub.  
The database is created fresh on each machine by running `python main.py`.
