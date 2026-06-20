let activeSession = null, sessionTimer = null, autoCheckoutTimer = null, checkoutWarningTimer = null;

const shortTime = d => d.toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit' });

function updateCheckinTime() {
  const el = document.getElementById('checkinTimeDisplay');
  if (el) el.textContent = new Date().toLocaleTimeString('en-MY', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateCheckinTime, 1000);
updateCheckinTime();

function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show' + (type ? ' toast-' + type : '');
  setTimeout(() => t.className = 'toast', 3000);
}

function scheduleAutoCheckout() {
  if (autoCheckoutTimer) clearTimeout(autoCheckoutTimer);
  const now = new Date(), cutoff = new Date();
  cutoff.setHours(21, 0, 0, 0);
  if (now >= cutoff) cutoff.setDate(cutoff.getDate() + 1);
  const ms = cutoff - now;
  console.log(`[ParkPredict] Auto-checkout in ${Math.round(ms / 60000)} min`);
  autoCheckoutTimer = setTimeout(() => {
    if (activeSession) {
      showToast('⏰ Auto checkout: Campus closes at 9 PM.', 'red');
      doCheckOut(true);
    }
  }, ms);
}

function scheduleCheckoutWarning() {
  if (checkoutWarningTimer) clearTimeout(checkoutWarningTimer);
  const now = new Date(), warn = new Date();
  warn.setHours(20, 45, 0, 0);
  if (now >= warn) return;
  checkoutWarningTimer = setTimeout(() => {
    if (activeSession) showToast('⚠️ Campus closes at 9 PM – please check out soon!', '');
  }, warn - now);
}

let checkInInProgress = false;

async function doCheckIn() {
  if (checkInInProgress) return;
  const studentId = document.getElementById('studentId').value.trim();
  const plate     = document.getElementById('vehiclePlate').value.trim().toUpperCase();
  const zone      = document.getElementById('zoneSelect').value;
  const type      = document.getElementById('vehicleType').value;

  if (!studentId) { showToast('Please enter your Student ID', 'red'); return; }
  if (!plate)     { showToast('Please enter your vehicle plate', 'red'); return; }
  if (!zone)      { showToast('Please select a parking zone', 'red'); return; }

  const now = new Date();
  if (now.getHours() >= 21) {
    showToast('❌ Check-in not allowed after 9 PM.', 'red'); return;
  }

  checkInInProgress = true;
  try {
    const result = await apiCheckIn({ student_id: studentId, plate, zone, vehicle_type: type });
    activeSession = { studentId, plate, zone, type, startTime: now, sessionId: result.session_id };
  } catch (err) {
    console.warn('[ParkPredict] Check-in API failed, offline:', err.message);
    activeSession = { studentId, plate, zone, type, startTime: now, sessionId: null };
    if (ZONES[zone]?.available > 0) ZONES[zone].available--;
  } finally {
    checkInInProgress = false;
  }

  document.getElementById('checkinCard').style.display = 'none';
  document.getElementById('checkoutCard').style.display = 'block';
  updateSessionStatus(now);
  updateSessionInfo();
  addActivityRow(studentId, zone, plate, type, now, null);
  showToast('✅ Checked in successfully!', 'green');
  scheduleAutoCheckout();
  scheduleCheckoutWarning();
}

async function doCheckOut(isAuto = false) {
  if (!activeSession) return;
  const now  = new Date();
  const diff = Math.floor((now - activeSession.startTime) / 1000);
  const h    = Math.floor(diff / 3600);
  const m    = Math.floor((diff % 3600) / 60);
  const dur  = h > 0 ? `${h}h ${m}m` : `${m}m`;

  try {
    if (activeSession.sessionId) {
      await apiCheckOut(activeSession.sessionId);
    } else if (ZONES[activeSession.zone]) {
      const z = ZONES[activeSession.zone];
      z.available = Math.min(z.total, z.available + 1);
    }
  } catch (err) {
    console.warn('[ParkPredict] Check-out API failed:', err.message);
  }

  updateLastActivityRow(now, dur);
  activeSession = null;
  clearInterval(sessionTimer);
  if (autoCheckoutTimer) { clearTimeout(autoCheckoutTimer); autoCheckoutTimer = null; }
  if (checkoutWarningTimer) { clearTimeout(checkoutWarningTimer); checkoutWarningTimer = null; }

  document.getElementById('checkinCard').style.display = 'block';
  document.getElementById('checkoutCard').style.display = 'none';
  ['studentId', 'vehiclePlate', 'zoneSelect'].forEach(id => document.getElementById(id).value = '');

  const autoMsg = isAuto ? '⏰ Auto-checked out at 9 PM' : '✅ Session ended – Thanks!';
  document.getElementById('sessionStatus').innerHTML = `
    <div class="session-idle">
      <div class="session-icon">${isAuto ? '⏰' : '✅'}</div>
      <div class="session-text">${autoMsg}</div>
      <div class="session-sub">Duration: ${dur}</div>
    </div>`;

  if (!isAuto) showToast('✅ Checked out! Duration: ' + dur, 'green');
  setTimeout(() => {
    document.getElementById('sessionStatus').innerHTML = `
      <div class="session-idle">
        <div class="session-icon">🅿️</div>
        <div class="session-text">No active parking session</div>
        <div class="session-sub">Check in to start tracking</div>
      </div>`;
  }, 5000);
}

function updateSessionStatus(startTime) {
  if (sessionTimer) clearInterval(sessionTimer);
  const update = () => {
    if (!activeSession) return;
    const now  = new Date();
    const diff = Math.floor((now - startTime) / 1000);
    const h = Math.floor(diff / 3600), m = Math.floor((diff % 3600) / 60), s = diff % 60;
    const timeStr = [h, m, s].map(v => String(v).padStart(2, '0')).join(':');
    const isLate = now.getHours() >= 20 && now.getMinutes() >= 45;
    const timerColor = isLate ? 'var(--yellow)' : 'var(--accent2)';
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
          ${isLate ? '<div style="font-size:0.72rem;color:var(--yellow);margin-top:4px">⚠️ Campus closes at 9 PM – please check out soon</div>' : ''}
        </div>
        <div class="session-timer" style="color:${timerColor}">${timeStr}</div>
      </div>`;
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
    <div class="session-info-row"><span>Checked in</span><span class="session-info-val">${shortTime(activeSession.startTime)}</span></div>
    <div class="session-info-row"><span>Auto-checkout</span><span class="session-info-val" style="color:var(--yellow)">9:00 PM</span></div>`;
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
    <td style="font-family:var(--font-mono)">${shortTime(inTime)}</td>
    <td id="lr-out">–</td>
    <td id="lr-dur">–</td>
    <td><span class="status-active">● ACTIVE</span></td>`;
  tbody.prepend(row);
}

function updateLastActivityRow(outTime, dur) {
  const outEl = document.getElementById('lr-out'), durEl = document.getElementById('lr-dur');
  if (outEl) outEl.textContent = shortTime(outTime);
  if (durEl) durEl.textContent = dur;
  const st = document.getElementById('last-row')?.querySelector('.status-active');
  if (st) { st.className = 'status-done'; st.textContent = 'DONE'; }
}

async function renderActivityTable() {
  const tbody = document.getElementById('activityBody');
  if (!tbody) return;

  let sessions;
  try {
    sessions = await fetchSessions();
    sessions = sessions.map(s => {
      if (!s.check_in) return s;
      const inTime  = new Date(s.check_in);
      const outTime = s.check_out ? new Date(s.check_out) : null;
      return {
        id:       s.student_id || `#${s.id}`,
        zone:     s.zone,
        vehicle:  s.plate,
        type:     s.vehicle_type,
        in:       shortTime(inTime),
        out:      outTime ? shortTime(outTime) : '–',
        duration: s.duration_min ? `${Math.floor(s.duration_min / 60)}h ${s.duration_min % 60}m` : '–',
        status:   s.check_out ? 'done' : 'active'
      };
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
      <td><span class="status-${s.status}">${s.status === 'active' ? '● ACTIVE' : 'DONE'}</span></td>`;
    tbody.appendChild(row);
  });
}

renderActivityTable();
