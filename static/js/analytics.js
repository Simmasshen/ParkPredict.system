// =============================================
// PARKPREDICT – ANALYTICS (analytics.js)
// =============================================

let hourlyChart = null;

function renderHourlyChart(dataset) {
  const ctx = document.getElementById('hourlyChart');
  if (!ctx) return;
  if (hourlyChart) hourlyChart.destroy();

  hourlyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: HOURS_LABELS,
      datasets: [{
        label: 'Occupancy %',
        data: HOURLY_DATA[dataset],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59,130,246,0.08)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#3b82f6',
        pointRadius: 4,
        pointHoverRadius: 7,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#111827',
          borderColor: '#1e2740',
          borderWidth: 1,
          callbacks: { label: c => ` ${c.parsed.y}% occupied` }
        }
      },
      scales: {
        x: { grid: { color: '#1e2740' } },
        y: {
          grid: { color: '#1e2740' },
          ticks: { callback: v => v + '%' },
          min: 0, max: 100
        }
      }
    }
  });
}

function switchDay(btn, dataset) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderHourlyChart(dataset);
}

function renderZoneChart() {
  const ctx = document.getElementById('zoneChart');
  if (!ctx) return;
  const labels = Object.values(ZONES).map(z => z.name);
  const avail = Object.values(ZONES).map(z => z.available);
  const occ = Object.values(ZONES).map(z => z.total - z.available);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Available', data: avail, backgroundColor: 'rgba(34,197,94,0.7)', borderRadius: 4 },
        { label: 'Occupied', data: occ, backgroundColor: 'rgba(239,68,68,0.5)', borderRadius: 4 }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: '#8892b0', font: { size: 11 } }
        },
        tooltip: {
          backgroundColor: '#111827',
          borderColor: '#1e2740',
          borderWidth: 1
        }
      },
      scales: {
        x: { stacked: true, grid: { color: '#1e2740' } },
        y: { stacked: true, grid: { color: '#1e2740' } }
      }
    }
  });
}

function renderDailyChart() {
  const ctx = document.getElementById('dailyChart');
  if (!ctx) return;
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const sessions = [198, 215, 231, 220, 247, 89, 42];

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: days,
      datasets: [{
        label: 'Sessions',
        data: sessions,
        backgroundColor: sessions.map((v, i) => i === 4 ? 'rgba(59,130,246,0.9)' : 'rgba(59,130,246,0.35)'),
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#111827',
          borderColor: '#1e2740',
          borderWidth: 1,
          callbacks: { label: c => ` ${c.parsed.y} sessions` }
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: '#1e2740' } }
      }
    }
  });
}

function renderVehicleChart() {
  const ctx = document.getElementById('vehicleChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Cars', 'Motorcycles'],
      datasets: [{
        data: [62, 38],
        backgroundColor: ['rgba(59,130,246,0.8)', 'rgba(139,92,246,0.8)'],
        borderColor: '#111827',
        borderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      cutout: '70%',
      plugins: {
        legend: { position: 'bottom', labels: { color: '#8892b0', padding: 16 } },
        tooltip: { backgroundColor: '#111827', borderColor: '#1e2740', borderWidth: 1 }
      }
    }
  });
}

function renderZoneUsageChart() {
  const ctx = document.getElementById('zoneUsageChart');
  if (!ctx) return;
  const labels = Object.keys(ZONES).map(k => 'Zone ' + k);
  const usage = Object.values(ZONES).map(z => z.total - z.available);
  const colors = [
    'rgba(59,130,246,0.8)', 'rgba(245,158,11,0.8)', 'rgba(34,197,94,0.8)',
    'rgba(239,68,68,0.8)', 'rgba(139,92,246,0.8)', 'rgba(20,184,166,0.8)', 'rgba(249,115,22,0.8)'
  ];
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: usage,
        backgroundColor: colors,
        borderColor: '#111827',
        borderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom', labels: { color: '#8892b0', padding: 10, font: { size: 10 } } },
        tooltip: { backgroundColor: '#111827', borderColor: '#1e2740', borderWidth: 1 }
      }
    }
  });
}

function renderHeatmap() {
  const el = document.getElementById('heatmap');
  if (!el) return;

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const hours = ['7AM','8AM','9AM','10AM','11AM','12PM','1PM','2PM','3PM','4PM','5PM','6PM'];

  let html = '<div class="heatmap-label"></div>';
  hours.forEach(h => html += `<div class="heatmap-header">${h}</div>`);

  days.forEach(day => {
    html += `<div class="heatmap-label">${day}</div>`;
    const data = PEAK_MODEL[Object.keys(PEAK_MODEL).find(k => k.startsWith(day.slice(0,-0))) || 'Monday'];
    for (let i = 0; i < 12; i++) {
      const v = data[i] || 0;
      const r = Math.round(239 * v / 100);
      const g = Math.round(68 + (197 - 68) * (1 - v / 100));
      const b = Math.round(68 * (1 - v / 100) + 94 * (v / 100));
      const alpha = 0.15 + (v / 100) * 0.75;
      const bg = v > 70 ? `rgba(239,68,68,${alpha})` :
                 v > 45 ? `rgba(245,158,11,${alpha})` :
                           `rgba(34,197,94,${alpha})`;
      html += `<div class="heatmap-cell" style="background:${bg}" title="${day} ${hours[i]}: ${v}% occupancy">${v}%</div>`;
    }
  });

  el.innerHTML = html;
}

// Init
renderHourlyChart('today');
renderZoneChart();
renderDailyChart();
renderVehicleChart();
renderZoneUsageChart();
renderHeatmap();
