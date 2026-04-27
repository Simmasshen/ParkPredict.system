CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
);

CREATE TABLE parking_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_name TEXT,
    capacity INTEGER
);

CREATE TABLE parking_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    zone_id INTEGER,
    checkin_time TEXT,
    checkout_time TEXT
);