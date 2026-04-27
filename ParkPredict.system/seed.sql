-- Clear existing data to prevent duplicates during testing
DELETE FROM parking_logs;
DELETE FROM parking_zones;
DELETE FROM users;

-- Reset SQLite autoincrement counters
DELETE FROM sqlite_sequence WHERE name IN ('users', 'parking_zones', 'parking_logs');

-- 1. Seed Users
-- Using dummy passwords for development; in production, these would be hashed.
INSERT INTO users (username, password) VALUES 
('alex_driver', 'pbkdf2:sha256:password123'),
('sam_parker', 'pbkdf2:sha256:secure456'),
('taylor_swift_park', 'pbkdf2:sha256:swift789');

-- 2. Seed Parking Zones
INSERT INTO parking_zones (zone_name, capacity) VALUES 
('North Lot - Level A', 50),
('South Garage - Level B', 120),
('VIP Plaza', 10);

-- 3. Seed Parking Logs
-- user_id and zone_id correspond to the IDs generated above (1, 2, 3)
INSERT INTO parking_logs (user_id, zone_id, checkin_time, checkout_time) VALUES 
(1, 1, '2026-04-22 08:30:00', '2026-04-22 17:00:00'), -- Alex in North Lot
(2, 2, '2026-04-22 09:15:00', '2026-04-22 18:30:00'), -- Sam in South Garage
(3, 3, '2026-04-22 10:00:00', NULL),                 -- Taylor currently parked in VIP
(1, 2, '2026-04-21 07:45:00', '2026-04-21 16:00:00'); -- Alex previous day