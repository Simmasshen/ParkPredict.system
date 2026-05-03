const ZONES_MOCK = {
  FCI: { name: 'FCI Parking', location: 'Faculty of Computing & Informatics', total: 120, available: 80 },
  FOM: { name: 'FOM Parking', location: 'Faculty of Management',              total: 80,  available: 30 },
  DTC: { name: 'DTC Parking', location: 'Grand Hall (DTC)',                   total: 100, available: 55 },
};

// Live ZONES object — populated by fetchZones(), falls back to mock
let ZONES = { ...ZONES_MOCK };

// ── Fetch zone data from Flask API ──
async function fetchZones() {
  try {
    const res = await fetch('/api/zones');
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    Object.assign(ZONES, data);
    console.log('[ParkPredict] Zones loaded from API');
  } catch (e) {
    console.warn('[ParkPredict] API unavailable, using mock data');
    Object.assign(ZONES, ZONES_MOCK);
  }
}

// ── Fetch prediction from Flask API ──
async function fetchPrediction(day, hour, zone = 'all') {
  try {
    const res = await fetch(`/api/predict?day=${encodeURIComponent(day)}&hour=${hour}&zone=${zone}`);
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch (e) {
    const zoneKey = (zone === 'all') ? null : zone;
    const dayData = zoneKey
      ? (PEAK_MODEL[zoneKey]?.[day] || getPeakModelAvg(day))
      : getPeakModelAvg(day);
    const idx  = Math.max(0, Math.min(13, hour - 7));
    const occupancy = dayData[idx];
    return { day, hour, zone, occupancy_pct: occupancy, availability_pct: 100 - occupancy };
  }
}

// ── Fetch today's sessions from Flask API ──
async function fetchSessions() {
  try {
    const res = await fetch('/api/sessions');
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch (e) {
    return SESSIONS_DATA;
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
fetchZones();
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

const HOURLY_DATA = {
  today:     [22,55,78,82,75,70,88,92,85,72,60,45,38,28],
  yesterday: [18,50,72,80,70,65,82,88,80,68,55,42,35,25],
  average:   [20,52,75,81,72,68,85,90,82,70,57,43,36,26],
};

const HOURS_LABELS = ['7AM','8AM','9AM','10AM','11AM','12PM','1PM','2PM','3PM','4PM','5PM','6PM','7PM','8PM'];

const SESSIONS_DATA = [
  { id: 'MMU-001', zone: 'FCI', vehicle: 'WXY 1234',  type: 'Car',        in: '7:45 AM',  out: '9:15 AM',  duration: '1h 30m', status: 'done'   },
  { id: 'MMU-002', zone: 'FOM', vehicle: 'VGH 5678',  type: 'Car',        in: '8:02 AM',  out: '11:00 AM', duration: '2h 58m', status: 'done'   },
  { id: 'MMU-003', zone: 'FCI', vehicle: 'BKL 9012',  type: 'Motorcycle', in: '8:30 AM',  out: '–',        duration: '–',      status: 'active' },
  { id: 'MMU-004', zone: 'DTC', vehicle: 'JXZ 3456',  type: 'Car',        in: '9:00 AM',  out: '–',        duration: '–',      status: 'active' },
  { id: 'MMU-005', zone: 'FOM', vehicle: 'PQR 7890',  type: 'Motorcycle', in: '9:15 AM',  out: '10:45 AM', duration: '1h 30m', status: 'done'   },
  { id: 'MMU-006', zone: 'DTC', vehicle: 'TUV 2345',  type: 'Car',        in: '10:00 AM', out: '–',        duration: '–',      status: 'active' },
];

// Peak occupancy % by day/hour (7AM–8PM) — per zone
const PEAK_MODEL = {
  FCI: {
    Monday:    [20,65,88,90,80,75,85,92,87,72,60,46,36,22],
    Tuesday:   [15,60,84,88,77,72,82,90,84,70,57,43,33,20],
    Wednesday: [22,63,86,89,79,74,84,91,86,71,59,45,35,21],
    Thursday:  [18,62,85,88,78,73,83,91,85,70,58,44,34,20],
    Friday:    [25,68,90,91,82,78,88,94,89,74,63,49,39,26],
    Saturday:  [5, 18,28,35,40,45,50,48,44,38,30,22,15,8 ],
  },
  FOM: {
    Monday:    [10,50,75,78,70,85,90,88,82,68,55,40,30,18],
    Tuesday:   [8, 45,70,75,68,82,88,85,80,65,52,38,28,15],
    Wednesday: [12,52,77,80,72,86,91,89,83,69,56,41,31,19],
    Thursday:  [10,50,74,77,70,84,89,87,81,67,54,39,29,17],
    Friday:    [15,55,78,80,74,88,93,91,85,71,60,44,34,22],
    Saturday:  [3, 12,20,28,35,42,48,45,40,34,26,18,10,5 ],
  },
  DTC: {
    Monday:    [5, 20,35,40,45,60,70,65,55,45,35,25,18,10],
    Tuesday:   [5, 18,32,38,42,58,68,62,52,42,32,22,15,8 ],
    Wednesday: [8, 25,40,45,50,65,75,70,60,50,40,28,20,12],
    Thursday:  [5, 20,35,40,45,60,70,65,55,45,35,25,18,10],
    Friday:    [10,30,50,55,60,75,88,85,75,62,50,38,28,18],
    Saturday:  [2, 10,18,25,35,55,65,62,55,45,35,22,12,5 ],
  },
};

function getPeakModelAvg(day) {
  const keys = Object.keys(PEAK_MODEL);
  return Array.from({length: 14}, (_, i) =>
    Math.round(keys.reduce((sum, k) => sum + (PEAK_MODEL[k][day]?.[i] || 0), 0) / keys.length)
  );
}

function updateClock() {
  const el = document.getElementById('navTime');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#8892b0';
  Chart.defaults.borderColor = '#1e2740';
  Chart.defaults.font.family = "'DM Sans', sans-serif";
}