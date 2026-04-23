from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import sqlite3

app = Flask(__name__)
CORS(app)  # This lets the UI teammate connect easily

# --- STEP 4: DATABASE CONNECTION UTILITY (PASTED HERE) ---
def get_db_connection():
    # 'parking_system.db' is the file Member 2 will create
    conn = sqlite3.connect('parking_system.db')
    conn.row_factory = sqlite3.Row 
    return conn

# --- 1. ROUTE FOR CHECK-IN ---
@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json() 
    plate = data.get('car_plate')
    zone = data.get('zone')
    
    # Example of how you will use the connection later:
    # db = get_db_connection()
    # db.execute('INSERT INTO parking_logs (plate, zone) VALUES (?, ?)', (plate, zone))
    # db.commit()
    # db.close()

    print(f"Car {plate} checked into {zone}")
    return jsonify({"message": f"Successfully checked in {plate}"}), 201

# --- 2. ROUTE FOR PARKING STATUS ---
@app.route('/status', methods=['GET'])
def get_status():
    example_status = {"available_spots": 15, "occupied_spots": 5}
    return jsonify(example_status), 200

if __name__ == '__main__':
    app.run(debug=True)
