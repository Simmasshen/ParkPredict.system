const ZONE_COLORS = {
  FCI: '#3b82f6', FOM: '#f59e0b', DTC: '#22c55e'
};
 
// Map the ZONES keys (FCI, FOM, DTC) to SVG element IDs
const ZONE_SVG_MAP = {
  FCI: 'map-zone-fci',
  FOM: 'map-zone-fom',
  DTC: 'map-zone-dtc'
};
 
function updateMapZones() {
  Object.entries(ZONES).forEach(([key, zone]) => {
    const pct = zone.available / zone.total;
    const color = pct > 0.5 ? '#22c55e' : pct > 0.2 ? '#f59e0b' : '#ef4444';
 
    // Update slot text badge inside SVG
    const slotEl = document.getElementById(`map-slots-${key.toLowerCase()}`);
    if (slotEl) slotEl.textContent = `${zone.available}/${zone.total}`;
 
    // Update clickable zone border/fill colors
    const svgId = ZONE_SVG_MAP[key];
    if (svgId) {
      const group = document.getElementById(svgId);
      if (group) {
        const rect = group.querySelector('.zone-rect');
        if (rect) {
          rect.setAttribute('fill', color + '14');
          rect.setAttribute('stroke', color);
        }
        // Update badge rect color
        const badges = group.querySelectorAll('rect:not(.zone-rect)');
        badges.forEach(b => {
          if (!b.hasAttribute('class')) b.setAttribute('fill', color);
        });
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
      <div class="zone-list-item" onclick="showZoneInfo('${key}')" style="cursor:pointer">
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
  const occupiedPct = Math.round((1 - pct) * 100);
 
  // Badge for primary zones
  const isPrimary = ['FCI','FOM','DTC'].includes(key);
  const badgeHtml = isPrimary
    ? `<div style="margin-bottom:8px"><span style="background:${colorHex}22;color:${colorHex};border:1px solid ${colorHex}44;border-radius:99px;padding:2px 10px;font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.1em">${label.toUpperCase()}</span></div>`
    : '';
 
  // Trend hint for primary zones
  const trendHints = {
    FCI: 'Busiest during 8–10 AM & 2–4 PM',
    FOM: 'Peak usage during lunch hours',
    DTC: 'Usually quieter – best alternative'
  };
  const trendHtml = trendHints[key]
    ? `<div style="margin-top:6px;font-size:0.72rem;color:var(--text3);display:flex;align-items:center;gap:5px"><span>📈</span>${trendHints[key]}</div>`
    : '';
 
  document.getElementById('popupZoneName').textContent = zone.name;
  document.getElementById('popupZoneName').style.color = colorHex;
  document.getElementById('popupBody').innerHTML = `
    ${badgeHtml}
    <div class="popup-row"><span>Location</span><span class="popup-val">${zone.location}</span></div>
    <div class="popup-row"><span>Available</span><span class="popup-val" style="color:${colorHex}">${zone.available} slots</span></div>
    <div class="popup-row"><span>Total</span><span class="popup-val">${zone.total} slots</span></div>
    <div class="popup-row"><span>Occupancy</span><span class="popup-val">${occupiedPct}%</span></div>
    <div class="popup-row"><span>Status</span><span class="popup-val" style="color:${colorHex}">${label}</span></div>
    <div style="margin-top:8px">
      <div style="background:var(--bg);border-radius:99px;height:6px;overflow:hidden">
        <div style="background:${colorHex};width:${Math.round(pct*100)}%;height:100%;border-radius:99px;transition:width 0.5s"></div>
      </div>
    </div>
    ${trendHtml}
    <a href="checkin.html" style="display:block;text-align:center;margin-top:12px;padding:8px;background:rgba(59,130,246,0.15);border-radius:6px;color:var(--accent2);text-decoration:none;font-size:0.82rem;font-weight:600;border:1px solid rgba(59,130,246,0.25);transition:all 0.2s">
      🅿️ Park Here →
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