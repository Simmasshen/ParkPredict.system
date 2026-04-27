
let activeSession = null;
let sessionTimer = null;

function updateCheckinTime() {
  const el = document.getElementById('checkinTimeDisplay');
  if (el) {
    el.textContent = new Date().toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }
}
setInterval(updateCheckinTime, 1000);
updateCheckinTime();

function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show' + (type ? ' toast-' + type : '');
  setTimeout(() => t.className = 'toast', 3000);
}

async function doCheckIn() {
  const studentId = document.getElementById('studentId').value.trim();
  const plate = document.getElementById('vehiclePlate').value.trim().toUpperCase();
  const zone = document.getElementById('zoneSelect').value;
  const type = document.getElementById('vehicleType').value;

  if (!studentId) { showToast('Please enter your Student ID', 'red'); return; }
  if (!plate)     { showToast('Please enter your vehicle plate', 'red'); return; }
  if (!zone)      { showToast('Please select a parking zone', 'red'); return; }

  const now = new Date();

  try {
    // Try real API first
    const result = await apiCheckIn({ student_id: studentId, plate, zone, vehicle_type: type });
    activeSession = { studentId, plate, zone, type, startTime: now, sessionId: result.session_id };
  } catch (err) {
    // Fallback: work offline if Flask not running
    console.warn('[ParkPredict] Check-in API failed, running offline:', err.message);
    activeSession = { studentId, plate, zone, type, startTime: now, sessionId: null };
    if (ZONES[zone] && ZONES[zone].available > 0) ZONES[zone].available--;
  }

  document.getElementById('checkinCard').style.display = 'none';
  document.getElementById('checkoutCard').style.display = 'block';
  updateSessionStatus(now);
  updateSessionInfo();
  addActivityRow(studentId, zone, plate, type, now, null);
  showToast('✅ Checked in successfully!', 'green');
}

async function doCheckOut() {
  if (!activeSession) return;
  const now = new Date();
  const diff = Math.floor((now - activeSession.startTime) / 1000);
  const h = Math.floor(diff / 3600);
  const m = Math.floor((diff % 3600) / 60);
  const dur = h > 0 ? `${h}h ${m}m` : `${m}m`;

  try {
    if (activeSession.sessionId) {
      await apiCheckOut(activeSession.sessionId);
    } else {
      // Offline fallback
      if (ZONES[activeSession.zone]) {
        ZONES[activeSession.zone].available = Math.min(
          ZONES[activeSession.zone].total,
          ZONES[activeSession.zone].available + 1
        );
      }
    }
  } catch (err) {
    console.warn('[ParkPredict] Check-out API failed:', err.message);
  }

  updateLastActivityRow(now, dur);
  activeSession = null;
  clearInterval(sessionTimer);

  document.getElementById('checkinCard').style.display = 'block';
  document.getElementById('checkoutCard').style.display = 'none';
  document.getElementById('studentId').value = '';
  document.getElementById('vehiclePlate').value = '';
  document.getElementById('zoneSelect').value = '';

  document.getElementById('sessionStatus').innerHTML = `
    <div class="session-idle">
      <div class="session-icon">✅</div>
      <div class="session-text">Session ended – Thanks!</div>
      <div class="session-sub">Duration: ${dur}</div>
    </div>
  `;
  showToast('✅ Checked out! Duration: ' + dur, 'green');
  setTimeout(() => {
    document.getElementById('sessionStatus').innerHTML = `
      <div class="session-idle">
        <div class="session-icon">🅿️</div>
        <div class="session-text">No active parking session</div>
        <div class="session-sub">Check in to start tracking</div>
      </div>
    `;
  }, 5000);
}

function updateSessionStatus(startTime) {
  const update = () => {
    const now = new Date();
    const diff = Math.floor((now - startTime) / 1000);
    const h = Math.floor(diff / 3600);
    const m = Math.floor((diff % 3600) / 60);
    const s = diff % 60;
    const timeStr = `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;

    if (!activeSession) return;
    document.getElementById('sessionStatus').innerHTML = `
      <div class="session-active">
        <div class="session-active-icon">🟢</div>
        <div class="session-active-info">
          <div class="session-active-title">ACTIVE SESSION · ZONE ${activeSession.zone}</div>
          <div class="session-active-details">
            <span>${activeSession.studentId}</span>
            <span>${activeSession.plate}</span>
            <span>${ZONES[activeSession.zone]?.location || ''}</span>
          </div>
        </div>
        <div class="session-timer">${timeStr}</div>
      </div>
    `;
  };
  update();
  sessionTimer = setInterval(update, 1000);
}

function updateSessionInfo() {
  const el = document.getElementById('sessionInfo');
  if (!el || !activeSession) return;
  const z = ZONES[activeSession.zone];
  el.innerHTML = `
    <div class="session-info-row"><span>Student ID</span><span class="session-info-val">${activeSession.studentId}</span></div>
    <div class="session-info-row"><span>Vehicle</span><span class="session-info-val">${activeSession.plate}</span></div>
    <div class="session-info-row"><span>Zone</span><span class="session-info-val">Zone ${activeSession.zone} – ${z?.location}</span></div>
    <div class="session-info-row"><span>Checked in</span><span class="session-info-val">${activeSession.startTime.toLocaleTimeString('en-MY', {hour:'2-digit',minute:'2-digit'})}</span></div>
  `;
}

function addActivityRow(id, zone, plate, type, inTime, outTime) {
  const tbody = document.getElementById('activityBody');
  if (!tbody) return;
  const row = document.createElement('tr');
  row.id = 'last-row';
  row.innerHTML = `
    <td style="font-family:var(--font-mono);font-size:0.78rem">${id}</td>
    <td><span style="font-family:var(--font-disp);font-size:1rem;color:var(--accent2)">Zone ${zone}</span></td>
    <td>${plate}</td>
    <td style="font-family:var(--font-mono)">${inTime.toLocaleTimeString('en-MY',{hour:'2-digit',minute:'2-digit'})}</td>
    <td id="lr-out">–</td>
    <td id="lr-dur">–</td>
    <td><span class="status-active">● ACTIVE</span></td>
  `;
  tbody.prepend(row);
}

function updateLastActivityRow(outTime, dur) {
  const outEl = document.getElementById('lr-out');
  const durEl = document.getElementById('lr-dur');
  if (outEl) outEl.textContent = outTime.toLocaleTimeString('en-MY',{hour:'2-digit',minute:'2-digit'});
  if (durEl) durEl.textContent = dur;
  const statusEl = document.getElementById('last-row')?.querySelector('.status-active');
  if (statusEl) { statusEl.className = 'status-done'; statusEl.textContent = 'DONE'; }
}

// Load activity table — tries API first, falls back to mock
async function renderActivityTable() {
  const tbody = document.getElementById('activityBody');
  if (!tbody) return;

  let sessions;
  try {
    sessions = await fetchSessions();
    // Normalize API format to display format
    sessions = sessions.map(s => {
      if (s.check_in) {
        // API format
        const inTime  = new Date(s.check_in);
        const outTime = s.check_out ? new Date(s.check_out) : null;
        return {
          id:       s.student_id || `#${s.id}`,
          zone:     s.zone,
          vehicle:  s.plate,
          type:     s.vehicle_type,
          in:       inTime.toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit' }),
          out:      outTime ? outTime.toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit' }) : '–',
          duration: s.duration_min ? `${Math.floor(s.duration_min/60)}h ${s.duration_min%60}m` : '–',
          status:   s.check_out ? 'done' : 'active'
        };
      }
      return s; // already mock format
    });
  } catch (e) {
    sessions = SESSIONS_DATA;
  }

  sessions.forEach(s => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td style="font-family:var(--font-mono);font-size:0.78rem">${s.id}</td>
      <td><span style="font-family:var(--font-disp);font-size:1rem;color:var(--accent2)">Zone ${s.zone}</span></td>
      <td>${s.vehicle}</td>
      <td style="font-family:var(--font-mono)">${s.in}</td>
      <td style="font-family:var(--font-mono)">${s.out}</td>
      <td>${s.duration}</td>
      <td><span class="status-${s.status}">${s.status === 'active' ? '● ACTIVE' : 'DONE'}</span></td>
    `;
    tbody.appendChild(row);
  });
}

renderActivityTable();
