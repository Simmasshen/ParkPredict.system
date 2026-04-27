"""
ParkPredict - Flask Backend
MMU Cyberjaya Smart Campus Parking Tracker
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
DB_PATH = 'parkpredict.db'


# ──────────────────────────────────────────────
# DATABASE SETUP
# ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            plate       TEXT NOT NULL,
            vehicle_type TEXT DEFAULT 'car',
            zone        TEXT NOT NULL,
            check_in    TEXT NOT NULL,
            check_out   TEXT,
            duration_min INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            zone_id   TEXT PRIMARY KEY,
            name      TEXT,
            location  TEXT,
            total     INTEGER,
            available INTEGER
        )
    ''')
    # Seed zones if empty
    c.execute('SELECT COUNT(*) FROM zones')
    if c.fetchone()[0] == 0:
        zones = [
            ('A', 'Zone A', 'Near FCI',       120, 80),
            ('B', 'Zone B', 'Top Right',        80, 30),
            ('C', 'Zone C', 'Left Mid',          90, 55),
            ('D', 'Zone D', 'Right Mid',         60,  8),
            ('E', 'Zone E', 'Bottom Left',      100, 70),
            ('F', 'Zone F', 'Bottom Right',      70, 25),
            ('G', 'Zone G', 'Multi-Storey',     200, 90),
        ]
        c.executemany('INSERT INTO zones VALUES (?,?,?,?,?)', zones)
    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# PAGES
# ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map_page():
    return render_template('map.html')

@app.route('/checkin')
def checkin_page():
    return render_template('checkin.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/predict')
def predict_page():
    return render_template('predict.html')


# ──────────────────────────────────────────────
# API – ZONE DATA
# ──────────────────────────────────────────────
@app.route('/api/zones')
def api_zones():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT zone_id, name, location, total, available FROM zones')
    rows = c.fetchall()
    conn.close()
    data = {row[0]: {
        'name': row[1], 'location': row[2],
        'total': row[3], 'available': row[4]
    } for row in rows}
    return jsonify(data)


# ──────────────────────────────────────────────
# API – CHECK IN
# ──────────────────────────────────────────────
@app.route('/api/checkin', methods=['POST'])
def api_checkin():
    body = request.get_json()
    student_id   = body.get('student_id', '').strip()
    plate        = body.get('plate', '').strip().upper()
    zone         = body.get('zone', '').strip().upper()
    vehicle_type = body.get('vehicle_type', 'car')

    if not (student_id and plate and zone):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check zone has space
    c.execute('SELECT available FROM zones WHERE zone_id=?', (zone,))
    row = c.fetchone()
    if not row or row[0] <= 0:
        conn.close()
        return jsonify({'error': 'No available slots in this zone'}), 409

    now = datetime.now().isoformat(timespec='seconds')
    c.execute(
        'INSERT INTO sessions (student_id,plate,vehicle_type,zone,check_in) VALUES (?,?,?,?,?)',
        (student_id, plate, vehicle_type, zone, now)
    )
    session_id = c.lastrowid
    c.execute('UPDATE zones SET available = available - 1 WHERE zone_id=?', (zone,))
    conn.commit()
    conn.close()

    return jsonify({'session_id': session_id, 'check_in': now, 'zone': zone})


# ──────────────────────────────────────────────
# API – CHECK OUT
# ──────────────────────────────────────────────
@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    body = request.get_json()
    session_id = body.get('session_id')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT zone, check_in, check_out FROM sessions WHERE id=?', (session_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    if row[2]:
        conn.close()
        return jsonify({'error': 'Already checked out'}), 409

    zone = row[0]
    check_in = datetime.fromisoformat(row[1])
    now = datetime.now()
    duration_min = int((now - check_in).total_seconds() / 60)

    c.execute(
        'UPDATE sessions SET check_out=?, duration_min=? WHERE id=?',
        (now.isoformat(timespec='seconds'), duration_min, session_id)
    )
    c.execute('UPDATE zones SET available = available + 1 WHERE zone_id=?', (zone,))
    conn.commit()
    conn.close()

    return jsonify({'check_out': now.isoformat(), 'duration_min': duration_min})


# ──────────────────────────────────────────────
# API – SESSIONS (today)
# ──────────────────────────────────────────────
@app.route('/api/sessions')
def api_sessions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute(
        'SELECT id,student_id,plate,vehicle_type,zone,check_in,check_out,duration_min FROM sessions WHERE check_in LIKE ? ORDER BY check_in DESC LIMIT 50',
        (today + '%',)
    )
    rows = c.fetchall()
    conn.close()
    sessions = [
        {
            'id': r[0], 'student_id': r[1], 'plate': r[2],
            'vehicle_type': r[3], 'zone': r[4],
            'check_in': r[5], 'check_out': r[6], 'duration_min': r[7]
        }
        for r in rows
    ]
    return jsonify(sessions)


# ──────────────────────────────────────────────
# API – PREDICTION (simple)
# ──────────────────────────────────────────────
@app.route('/api/predict')
def api_predict():
    day  = request.args.get('day', 'Monday')
    hour = int(request.args.get('hour', 9))

    PEAK_MODEL = {
        'Monday':    [15,60,82,78,74,72,90,93,85,70,58,44,35,22],
        'Tuesday':   [12,55,79,80,75,70,88,91,83,68,54,41,32,20],
        'Wednesday': [18,58,81,82,76,73,89,92,84,69,56,43,34,21],
        'Thursday':  [16,57,80,79,74,71,88,91,83,69,55,42,33,20],
        'Friday':    [20,62,84,83,78,76,91,94,87,72,61,47,38,25],
        'Saturday':  [ 8,22,35,40,45,50,55,52,48,44,38,30,22,15],
    }

    data = PEAK_MODEL.get(day, PEAK_MODEL['Monday'])
    idx  = max(0, min(13, hour - 7))
    occupancy = data[idx]
    probability = max(0, 100 - occupancy)

    return jsonify({
        'day': day, 'hour': hour,
        'occupancy_pct': occupancy,
        'availability_pct': probability,
        'verdict': 'good' if probability > 50 else 'moderate' if probability > 20 else 'busy'
    })


# ──────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
