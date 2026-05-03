"""
ParkPredict - Flask Backend
MMU Cyberjaya Smart Campus Parking Tracker
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
DB_PATH = 'parkpredict.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   TEXT NOT NULL,
            plate        TEXT NOT NULL,
            vehicle_type TEXT DEFAULT 'car',
            zone         TEXT NOT NULL,
            check_in     TEXT NOT NULL,
            check_out    TEXT,
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
    c.execute('SELECT COUNT(*) FROM zones')
    if c.fetchone()[0] == 0:
        zones = [
            ('FCI', 'FCI Parking', 'Faculty of Computing & Informatics', 120, 80),
            ('FOM', 'FOM Parking', 'Faculty of Management',               80,  30),
            ('DTC', 'DTC Parking', 'Grand Hall (DTC)',                   100,  55),
        ]
        c.executemany('INSERT INTO zones VALUES (?,?,?,?,?)', zones)
    conn.commit()
    conn.close()


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


@app.route('/api/zones')
def api_zones():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT zone_id, name, location, total, available FROM zones')
    rows = c.fetchall()
    conn.close()
    return jsonify({row[0]: {'name': row[1], 'location': row[2], 'total': row[3], 'available': row[4]} for row in rows})


@app.route('/api/checkin', methods=['POST'])
def api_checkin():
    body         = request.get_json()
    student_id   = body.get('student_id', '').strip()
    plate        = body.get('plate', '').strip().upper()
    zone         = body.get('zone', '').strip().upper()
    vehicle_type = body.get('vehicle_type', 'car')

    if not (student_id and plate and zone):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT available FROM zones WHERE zone_id=?', (zone,))
    row = c.fetchone()
    if not row or row[0] <= 0:
        conn.close()
        return jsonify({'error': 'No available slots in this zone'}), 409

    now = datetime.now().isoformat(timespec='seconds')
    c.execute('INSERT INTO sessions (student_id,plate,vehicle_type,zone,check_in) VALUES (?,?,?,?,?)',
              (student_id, plate, vehicle_type, zone, now))
    session_id = c.lastrowid
    c.execute('UPDATE zones SET available = available - 1 WHERE zone_id=?', (zone,))
    conn.commit()
    conn.close()
    return jsonify({'session_id': session_id, 'check_in': now, 'zone': zone})


@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    body       = request.get_json()
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

    zone         = row[0]
    check_in     = datetime.fromisoformat(row[1])
    now          = datetime.now()
    duration_min = int((now - check_in).total_seconds() / 60)

    c.execute('UPDATE sessions SET check_out=?, duration_min=? WHERE id=?',
              (now.isoformat(timespec='seconds'), duration_min, session_id))
    c.execute('UPDATE zones SET available = available + 1 WHERE zone_id=?', (zone,))
    conn.commit()
    conn.close()
    return jsonify({'check_out': now.isoformat(), 'duration_min': duration_min})


@app.route('/api/sessions')
def api_sessions():
    conn  = sqlite3.connect(DB_PATH)
    c     = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute(
        'SELECT id,student_id,plate,vehicle_type,zone,check_in,check_out,duration_min FROM sessions WHERE check_in LIKE ? ORDER BY check_in DESC LIMIT 50',
        (today + '%',)
    )
    rows = c.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'student_id': r[1], 'plate': r[2], 'vehicle_type': r[3],
                     'zone': r[4], 'check_in': r[5], 'check_out': r[6], 'duration_min': r[7]} for r in rows])


@app.route('/api/predict')
def api_predict():
    day  = request.args.get('day', 'Monday')
    hour = int(request.args.get('hour', 9))
    zone = request.args.get('zone', 'all')

    PEAK_MODEL = {
        'FCI': {
            'Monday':    [20,65,88,90,80,75,85,92,87,72,60,46,36,22],
            'Tuesday':   [15,60,84,88,77,72,82,90,84,70,57,43,33,20],
            'Wednesday': [22,63,86,89,79,74,84,91,86,71,59,45,35,21],
            'Thursday':  [18,62,85,88,78,73,83,91,85,70,58,44,34,20],
            'Friday':    [25,68,90,91,82,78,88,94,89,74,63,49,39,26],
            'Saturday':  [ 5,18,28,35,40,45,50,48,44,38,30,22,15, 8],
        },
        'FOM': {
            'Monday':    [10,50,75,78,70,85,90,88,82,68,55,40,30,18],
            'Tuesday':   [ 8,45,70,75,68,82,88,85,80,65,52,38,28,15],
            'Wednesday': [12,52,77,80,72,86,91,89,83,69,56,41,31,19],
            'Thursday':  [10,50,74,77,70,84,89,87,81,67,54,39,29,17],
            'Friday':    [15,55,78,80,74,88,93,91,85,71,60,44,34,22],
            'Saturday':  [ 3,12,20,28,35,42,48,45,40,34,26,18,10, 5],
        },
        'DTC': {
            'Monday':    [ 5,20,35,40,45,60,70,65,55,45,35,25,18,10],
            'Tuesday':   [ 5,18,32,38,42,58,68,62,52,42,32,22,15, 8],
            'Wednesday': [ 8,25,40,45,50,65,75,70,60,50,40,28,20,12],
            'Thursday':  [ 5,20,35,40,45,60,70,65,55,45,35,25,18,10],
            'Friday':    [10,30,50,55,60,75,88,85,75,62,50,38,28,18],
            'Saturday':  [ 2,10,18,25,35,55,65,62,55,45,35,22,12, 5],
        },
    }

    if zone in PEAK_MODEL:
        data = PEAK_MODEL[zone].get(day, PEAK_MODEL[zone]['Monday'])
    else:
        all_days = [PEAK_MODEL[z].get(day, PEAK_MODEL[z]['Monday']) for z in PEAK_MODEL]
        data = [round(sum(h[i] for h in all_days) / len(all_days)) for i in range(14)]

    idx         = max(0, min(13, hour - 7))
    occupancy   = data[idx]
    probability = max(0, 100 - occupancy)

    return jsonify({
        'day': day, 'hour': hour, 'zone': zone,
        'occupancy_pct': occupancy,
        'availability_pct': probability,
        'verdict': 'good' if probability > 50 else 'moderate' if probability > 20 else 'busy'
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)