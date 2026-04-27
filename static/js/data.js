

// ── Mock / fallback data ──
const ZONES_MOCK = {
  A: { name: 'Zone A', location: 'Near FCI', total: 120, available: 80 },
  B: { name: 'Zone B', location: 'Top Right', total: 80, available: 30 },
  C: { name: 'Zone C', location: 'Left Mid', total: 90, available: 55 },
  D: { name: 'Zone D', location: 'Right Mid', total: 60, available: 8 },
  E: { name: 'Zone E', location: 'Bottom Left', total: 100, available: 70 },
  F: { name: 'Zone F', location: 'Bottom Right', total: 70, available: 25 },
  G: { name: 'Zone G', location: 'Multi-Storey', total: 200, available: 90 },
};

// Live ZONES object — populated by fetchZones(), falls back to mock
let ZONES = { ...ZONES_MOCK };

// ── Fetch zone data from Flask API ──
async function fetchZones() {
  try {
    const res = await fetch('/api/zones');
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    // Merge API data into ZONES
    Object.assign(ZONES, data);
    console.log('[ParkPredict] Zones loaded from API');
  } catch (e) {
    // Silently fall back to mock data
    console.warn('[ParkPredict] API unavailable, using mock data');
    Object.assign(ZONES, ZONES_MOCK);
  }
}

// ── Fetch prediction from Flask API ──
async function fetchPrediction(day, hour) {
  try {
    const res = await fetch(`/api/predict?day=${encodeURIComponent(day)}&hour=${hour}`);
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch (e) {
    // Fall back to local model
    const data = PEAK_MODEL[day] || PEAK_MODEL['Monday'];
    const idx  = Math.max(0, Math.min(13, hour - 7));
    const occupancy = data[idx];
    return { day, hour, occupancy_pct: occupancy, availability_pct: 100 - occupancy };
  }
}

// ── Fetch today's sessions from Flask API ──
async function fetchSessions() {
  try {
    const res = await fetch('/api/sessions');
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch (e) {
    return SESSIONS_DATA; // fallback
  }
}

// ── POST check-in to Flask API ──
async function apiCheckIn(payload) {
  const res = await fetch('/api/checkin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Check-in failed');
  }
  return await res.json();
}

// ── POST check-out to Flask API ──
async function apiCheckOut(sessionId) {
  const res = await fetch('/api/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Check-out failed');
  }
  return await res.json();
}

// ── Simulate live changes (used when API is offline) ──
function simulateLiveChanges() {
  Object.keys(ZONES).forEach(k => {
    const z = ZONES[k];
    const delta = Math.floor(Math.random() * 7) - 3;
    z.available = Math.max(0, Math.min(z.total, z.available + delta));
  });
}

// ── Auto-refresh zones from API every 30 seconds ──
fetchZones(); // initial load
setInterval(fetchZones, 30000);

function getZoneColor(pct) {
  if (pct > 0.5) return 'green';
  if (pct > 0.2) return 'yellow';
  return 'red';
}

function getZoneLabel(pct) {
  if (pct > 0.5) return 'Available';
  if (pct > 0.2) return 'Moderate';
  return 'Full';
}

// Hourly occupancy data (% occupancy per hour 7am–8pm)
const HOURLY_DATA = {
  today:     [22,55,78,82,75,70,88,92,85,72,60,45,38,28],
  yesterday: [18,50,72,80,70,65,82,88,80,68,55,42,35,25],
  average:   [20,52,75,81,72,68,85,90,82,70,57,43,36,26],
};

const HOURS_LABELS = ['7AM','8AM','9AM','10AM','11AM','12PM','1PM','2PM','3PM','4PM','5PM','6PM','7PM','8PM'];

const SESSIONS_DATA = [
  { id: 'MMU-001', zone: 'A', vehicle: 'WXY 1234', type: 'Car', in: '7:45 AM', out: '9:15 AM', duration: '1h 30m', status: 'done' },
  { id: 'MMU-002', zone: 'G', vehicle: 'VGH 5678', type: 'Car', in: '8:02 AM', out: '11:00 AM', duration: '2h 58m', status: 'done' },
  { id: 'MMU-003', zone: 'B', vehicle: 'BKL 9012', type: 'Motorcycle', in: '8:30 AM', out: '-', duration: '-', status: 'active' },
  { id: 'MMU-004', zone: 'C', vehicle: 'JXZ 3456', type: 'Car', in: '9:00 AM', out: '-', duration: '-', status: 'active' },
  { id: 'MMU-005', zone: 'E', vehicle: 'PQR 7890', type: 'Motorcycle', in: '9:15 AM', out: '10:45 AM', duration: '1h 30m', status: 'done' },
  { id: 'MMU-006', zone: 'A', vehicle: 'TUV 2345', type: 'Car', in: '10:00 AM', out: '-', duration: '-', status: 'active' },
];

// Peak data by day/hour for prediction model
const PEAK_MODEL = {
  Monday:    [15,60,82,78,74,72,90,93,85,70,58,44,35,22],
  Tuesday:   [12,55,79,80,75,70,88,91,83,68,54,41,32,20],
  Wednesday: [18,58,81,82,76,73,89,92,84,69,56,43,34,21],
  Thursday:  [16,57,80,79,74,71,88,91,83,69,55,42,33,20],
  Friday:    [20,62,84,83,78,76,91,94,87,72,61,47,38,25],
  Saturday:  [8, 22,35,40,45,50,55,52,48,44,38,30,22,15],
};

// Update clock
function updateClock() {
  const el = document.getElementById('navTime');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

// Chart.js global defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#8892b0';
  Chart.defaults.borderColor = '#1e2740';
  Chart.defaults.font.family = "'DM Sans', sans-serif";
}
