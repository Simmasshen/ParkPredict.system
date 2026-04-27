

function renderZones() {
  const grid = document.getElementById('zonesGrid');
  if (!grid) return;
  grid.innerHTML = '';
  let totalAvail = 0, totalOcc = 0;

  Object.entries(ZONES).forEach(([key, zone]) => {
    const pct = zone.available / zone.total;
    const color = getZoneColor(pct);
    const label = getZoneLabel(pct);
    totalAvail += zone.available;
    totalOcc += (zone.total - zone.available);

    grid.innerHTML += `
      <div class="zone-card" onclick="window.location.href='map.html'">
        <div class="zone-stripe stripe-${color}"></div>
        <div class="zone-card-top">
          <span class="zone-name" style="color:var(--${color === 'green' ? 'green' : color === 'yellow' ? 'yellow' : 'red'})">${zone.name}</span>
          <span class="zone-badge badge-${color}">${label}</span>
        </div>
        <div class="zone-bar-wrap">
          <div class="zone-bar bar-${color}" style="width:${Math.round(pct*100)}%"></div>
        </div>
        <div class="zone-info">
          <span class="zone-avail">${zone.available} / ${zone.total} available · ${zone.location}</span>
          <span class="zone-pct" style="color:var(--${color === 'green' ? 'green' : color === 'yellow' ? 'yellow' : 'red'})">${Math.round(pct*100)}%</span>
        </div>
      </div>
    `;
  });

  const total = totalAvail + totalOcc;
  document.getElementById('totalAvail').textContent = totalAvail;
  document.getElementById('totalOccupied').textContent = totalOcc;
  document.getElementById('occupancyRate').textContent = Math.round((totalOcc / total) * 100) + '%';
}

function renderTrendChart() {
  const ctx = document.getElementById('trendChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: HOURS_LABELS,
      datasets: [
        {
          label: 'Occupancy %',
          data: HOURLY_DATA.today,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59,130,246,0.1)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#3b82f6',
          pointRadius: 4,
          pointHoverRadius: 7,
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#111827',
          borderColor: '#1e2740',
          borderWidth: 1,
          callbacks: {
            label: ctx => ` ${ctx.parsed.y}% occupied`
          }
        }
      },
      scales: {
        x: {
          grid: { color: '#1e2740' },
          ticks: { color: '#8892b0' }
        },
        y: {
          grid: { color: '#1e2740' },
          ticks: { color: '#8892b0', callback: v => v + '%' },
          min: 0, max: 100,
          // highlight peak zone
          afterDraw(chart) {
            const ctx2 = chart.ctx;
            const yAxis = chart.scales.y;
            const xAxis = chart.scales.x;
            ctx2.save();
            ctx2.fillStyle = 'rgba(239,68,68,0.06)';
            const x1 = xAxis.getPixelForValue(1); // 8AM
            const x2 = xAxis.getPixelForValue(2); // 9AM
            ctx2.fillRect(x1, yAxis.top, x2-x1, yAxis.bottom-yAxis.top);
            ctx2.restore();
          }
        }
      }
    }
  });
}

function quickPredict() {
  const day = document.getElementById('qDay').value;
  const timeStr = document.getElementById('qTime').value;
  const hour = parseInt(timeStr);
  const ampm = timeStr.includes('PM') && hour !== 12 ? 12 : 0;
  const h = hour + ampm - 7; // offset to array index (7AM = 0)
  const idx = Math.max(0, Math.min(13, h));

  const data = PEAK_MODEL[day] || PEAK_MODEL['Monday'];
  const occupancy = data[idx];
  const probability = 100 - occupancy;
  const color = probability > 50 ? '#22c55e' : probability > 20 ? '#f59e0b' : '#ef4444';
  const emoji = probability > 50 ? '🟢' : probability > 20 ? '🟡' : '🔴';
  const verdict = probability > 50 ? 'Good chance of parking!' : probability > 20 ? 'Moderate availability' : 'Very crowded – consider alternatives';

  // Find best zones
  const bestZones = Object.entries(ZONES)
    .sort((a, b) => (b[1].available / b[1].total) - (a[1].available / a[1].total))
    .slice(0, 3);

  document.getElementById('qResult').innerHTML = `
    <div class="predict-output">
      <div class="predict-prob" style="color:${color}">${probability}%</div>
      <div class="predict-prob-label">Chance of finding parking</div>
      <div class="predict-suggestions">
        <div class="predict-suggestion">${emoji} ${verdict}</div>
        ${bestZones.map(([k, z]) => `<div class="predict-suggestion">🅿️ ${z.name} – ${z.available} slots available</div>`).join('')}
      </div>
    </div>
  `;
}

// Init
renderZones();
renderTrendChart();

// Refresh every 30 seconds
setInterval(() => {
  simulateLiveChanges();
  renderZones();
}, 30000);
