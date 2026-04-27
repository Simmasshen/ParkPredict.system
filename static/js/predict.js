

let selectedDay = 'Monday';
let selectedHour = 9;
let predictChart = null;

// Day picker
document.querySelectorAll('.day-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedDay = btn.dataset.day;
  });
});

function updateTimeDisplay(val) {
  selectedHour = parseInt(val);
  const h = selectedHour > 12 ? selectedHour - 12 : selectedHour;
  const ampm = selectedHour >= 12 ? 'PM' : 'AM';
  document.getElementById('timeSliderLabel').textContent = `${h}:00 ${ampm}`;
}

async function runPrediction() {
  const zone = document.getElementById('predictZone').value;

  // Fetch from API (falls back to local model automatically)
  const result = await fetchPrediction(selectedDay, selectedHour);
  const probability = result.availability_pct;
  const occupancyAtTime = result.occupancy_pct;
  const color = probability > 50 ? '#22c55e' : probability > 20 ? '#f59e0b' : '#ef4444';
  const bgColor = probability > 50 ? 'rgba(34,197,94,0.1)' : probability > 20 ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)';
  const label = probability > 50 ? 'GOOD TO GO' : probability > 20 ? 'MODERATE' : 'VERY BUSY';

  // Zone-level predictions
  const zoneProbs = zone === 'all'
    ? Object.entries(ZONES).map(([k, z]) => {
        const pct = z.available / z.total;
        const prob = Math.round(pct * 100 * (0.8 + Math.random() * 0.4));
        return { key: k, name: z.name, prob: Math.min(99, prob) };
      })
    : [{ key: zone, name: ZONES[zone]?.name, prob: probability }];

  // Results panel
  document.getElementById('predictResults').innerHTML = `
    <div style="width:100%">
      <div class="card-label">PREDICTION RESULT</div>
      <h2 style="font-family:var(--font-disp);font-size:1.5rem;letter-spacing:0.04em;margin-bottom:1.25rem">
        ${selectedDay} · ${selectedHour > 12 ? selectedHour - 12 : selectedHour}:00 ${selectedHour >= 12 ? 'PM' : 'AM'}
      </h2>
      <div style="text-align:center;background:${bgColor};border:1px solid ${color}33;border-radius:10px;padding:1.5rem;margin-bottom:1.25rem">
        <div style="font-family:var(--font-disp);font-size:4rem;color:${color};line-height:1">${probability}%</div>
        <div style="font-family:var(--font-mono);font-size:0.7rem;color:${color};letter-spacing:0.15em;margin-top:4px">${label}</div>
        <div style="font-size:0.82rem;color:var(--text2);margin-top:8px">Overall chance of finding parking</div>
      </div>
      <div style="margin-bottom:1rem;font-size:0.82rem;color:var(--text3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.1em">Zone Breakdown</div>
      <div class="result-zones-grid">
        ${zoneProbs.map(z => {
          const c = z.prob > 50 ? '#22c55e' : z.prob > 20 ? '#f59e0b' : '#ef4444';
          return `
            <div class="result-zone-card" style="border-color:${c}33">
              <div class="result-zone-name" style="color:${c}">${z.name}</div>
              <div class="result-zone-prob" style="color:${c}">${z.prob}%</div>
              <div class="result-zone-label">Probability</div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;

  // Show chart
  renderPredictChart();

  // Show recommendations
  renderRecommendations(probability, selectedDay, selectedHour);

  document.getElementById('predictChartCard').style.display = 'block';
  document.getElementById('recoCard').style.display = 'block';
}

function renderPredictChart() {
  const ctx = document.getElementById('predictChart');
  if (!ctx) return;
  if (predictChart) predictChart.destroy();

  const data = PEAK_MODEL[selectedDay] || PEAK_MODEL['Monday'];
  const probData = data.map(v => Math.max(0, 100 - v));
  const selectedIdx = selectedHour - 7;

  const pointBg = data.map((_, i) => i === selectedIdx ? '#ffffff' : '#3b82f6');
  const pointR = data.map((_, i) => i === selectedIdx ? 8 : 3);

  predictChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: HOURS_LABELS,
      datasets: [{
        label: 'Availability %',
        data: probData,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59,130,246,0.08)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: pointBg,
        pointRadius: pointR,
        pointHoverRadius: 8,
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
          callbacks: { label: c => ` ${c.parsed.y}% chance of parking` }
        },
        annotation: {}
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

function renderRecommendations(prob, day, hour) {
  const recoEl = document.getElementById('recoList');
  if (!recoEl) return;

  const recos = [];

  if (prob < 30) {
    recos.push({ icon: '⏰', text: `<strong>Arrive earlier.</strong> Try coming before ${hour > 8 ? (hour - 1) + ':00 ' + (hour-1 >= 12 ? 'PM' : 'AM') : '7:30 AM'} to improve your chances significantly.` });
    recos.push({ icon: '🏍', text: `<strong>Consider Zone G</strong> (Multi-Storey) – it has the most total slots and usually has space even during peak hours.` });
    recos.push({ icon: '🚌', text: `<strong>Explore alternatives.</strong> MMU shuttle service and carpooling can help avoid parking stress during ${day} peak hours.` });
  } else if (prob < 60) {
    recos.push({ icon: '🟡', text: `<strong>Moderate availability.</strong> Head to Zone A or Zone E first – they tend to have better availability on ${day}s.` });
    recos.push({ icon: '⏱', text: `<strong>Best window:</strong> Arriving 15–20 minutes before ${hour}:00 gives you a much better chance of securing a spot.` });
  } else {
    recos.push({ icon: '🟢', text: `<strong>Great time to park!</strong> ${day} at ${hour > 12 ? hour - 12 : hour}:00 ${hour >= 12 ? 'PM' : 'AM'} is typically a low-traffic period on campus.` });
    recos.push({ icon: '🅿️', text: `<strong>Zone C or Zone E</strong> are closest to the main academic buildings and should have plenty of space.` });
  }

  recos.push({ icon: '📊', text: `Based on <strong>historical data</strong>, ${day}s at this time average ${100 - prob}% campus parking occupancy.` });

  recoEl.innerHTML = recos.map(r => `
    <div class="reco-item">
      <span class="reco-icon">${r.icon}</span>
      <span class="reco-text">${r.text}</span>
    </div>
  `).join('');
}
