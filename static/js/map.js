// =============================================
// PARKPREDICT – MAP PAGE (map.js)
// =============================================

const ZONE_COLORS = {
  A: '#22c55e', B: '#f59e0b', C: '#22c55e',
  D: '#ef4444', E: '#22c55e', F: '#f59e0b', G: '#f59e0b'
};

function updateMapZones() {
  Object.entries(ZONES).forEach(([key, zone]) => {
    const pct = zone.available / zone.total;
    const color = pct > 0.5 ? '#22c55e' : pct > 0.2 ? '#f59e0b' : '#ef4444';
    const slotEl = document.getElementById(`map-slots-${key.toLowerCase()}`);
    const rectEl = document.querySelector(`[data-zone="${key}"]`);
    if (slotEl) slotEl.textContent = `${zone.available}/${zone.total}`;
    if (rectEl) {
      rectEl.setAttribute('fill', color + '22');
      rectEl.setAttribute('stroke', color);
      rectEl.previousElementSibling && (rectEl.previousElementSibling.style && (rectEl.previousElementSibling.textContent));
      // Update text color
      const group = document.getElementById(`map-zone-${key.toLowerCase()}`);
      if (group) {
        group.querySelectorAll('text').forEach(t => t.setAttribute('fill', color));
        group.querySelectorAll('circle').forEach(c => c.setAttribute('fill', color));
      }
    }
  });
}

function renderZoneList() {
  const list = document.getElementById('zoneList');
  if (!list) return;
  list.innerHTML = '';
  Object.entries(ZONES).forEach(([key, zone]) => {
    const pct = zone.available / zone.total;
    const color = getZoneColor(pct);
    const colorHex = color === 'green' ? '#22c55e' : color === 'yellow' ? '#f59e0b' : '#ef4444';
    list.innerHTML += `
      <div class="zone-list-item" onclick="showZoneInfo('${key}')">
        <span class="zname" style="color:${colorHex}">${zone.name}</span>
        <span style="font-family:var(--font-mono);font-size:0.75rem;color:${colorHex}">${zone.available}/${zone.total}</span>
      </div>
    `;
  });
}

function showZoneInfo(key) {
  const zone = ZONES[key];
  if (!zone) return;
  const pct = zone.available / zone.total;
  const color = getZoneColor(pct);
  const colorHex = color === 'green' ? '#22c55e' : color === 'yellow' ? '#f59e0b' : '#ef4444';
  const label = getZoneLabel(pct);

  document.getElementById('popupZoneName').textContent = zone.name;
  document.getElementById('popupZoneName').style.color = colorHex;
  document.getElementById('popupBody').innerHTML = `
    <div class="popup-row"><span>Location</span><span class="popup-val">${zone.location}</span></div>
    <div class="popup-row"><span>Available</span><span class="popup-val" style="color:${colorHex}">${zone.available} slots</span></div>
    <div class="popup-row"><span>Total</span><span class="popup-val">${zone.total} slots</span></div>
    <div class="popup-row"><span>Occupancy</span><span class="popup-val">${Math.round((1 - pct) * 100)}%</span></div>
    <div class="popup-row"><span>Status</span><span class="popup-val" style="color:${colorHex}">${label}</span></div>
    <div style="margin-top:8px">
      <div style="background:var(--bg);border-radius:99px;height:6px;overflow:hidden">
        <div style="background:${colorHex};width:${Math.round(pct*100)}%;height:100%;border-radius:99px"></div>
      </div>
    </div>
    <a href="checkin.html" style="display:block;text-align:center;margin-top:10px;padding:7px;background:rgba(59,130,246,0.15);border-radius:6px;color:var(--accent2);text-decoration:none;font-size:0.8rem;font-weight:600">
      Park Here →
    </a>
  `;
  document.getElementById('zonePopup').style.display = 'block';
}

// Init
updateMapZones();
renderZoneList();

setInterval(() => {
  simulateLiveChanges();
  updateMapZones();
  renderZoneList();
}, 30000);
