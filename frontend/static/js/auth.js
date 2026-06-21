// ── Simulated user store (replace with Flask API) ──
const MOCK_USERS = [
  { id: '1221103456', email: 'student@student.mmu.edu.my', password: 'mmu12345', name: 'Ahmad Zulkifli' }
];

// ── Live slot count on left panel ──
window.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('liveAvail');
  if (!el) return;
  const total = Object.values(ZONES).reduce((s, z) => s + z.available, 0);
  el.textContent = `${total} slots available across campus`;
});

// ── Show/hide password ──
function togglePw(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isHidden = input.type === 'password';
  input.type = isHidden ? 'text' : 'password';
  btn.innerHTML = isHidden
    ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`
    : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
}

// ── Password strength checker ──
function checkPwStrength(val) {
  const fill  = document.getElementById('pwFill');
  const label = document.getElementById('pwLabel');
  if (!fill || !label) return;

  let score = 0;
  if (val.length >= 8) score++;
  if (/[A-Z]/.test(val)) score++;
  if (/[0-9]/.test(val)) score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;

  const levels = [
    { w: '0%',   color: 'transparent', text: '' },
    { w: '25%',  color: '#ef4444',     text: 'Weak' },
    { w: '50%',  color: '#f59e0b',     text: 'Fair' },
    { w: '75%',  color: '#3b82f6',     text: 'Good' },
    { w: '100%', color: '#22c55e',     text: 'Strong' },
  ];
  const lv = levels[score] || levels[0];
  fill.style.width     = lv.w;
  fill.style.background = lv.color;
  label.textContent    = lv.text;
  label.style.color    = lv.color;
}

// ── Toast ──
function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.className = 'toast show' + (type ? ' toast-' + type : '');
  setTimeout(() => t.className = 'toast', 3000);
}

// ── Show/hide field error ──
function showError(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
}
function clearError(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'none';
}

// =============================================
// LOGIN
// =============================================
function doLogin() {
  clearError('loginError');
  const id = document.getElementById('loginId')?.value.trim();
  const pw = document.getElementById('loginPw')?.value;

  if (!id) { showError('loginError', 'Please enter your Student ID or email.'); return; }
  if (!pw)  { showError('loginError', 'Please enter your password.'); return; }

  // Simulate API call — replace with: fetch('/api/login', {method:'POST', body: JSON.stringify({id,pw})})
  const user = MOCK_USERS.find(u => (u.id === id || u.email === id) && u.password === pw);

  if (!user) {
    showError('loginError', 'Incorrect Student ID/email or password.');
    return;
  }

  sessionStorage.setItem('pp_user', JSON.stringify(user));
  showToast(`✅ Welcome back, ${user.name}!`, 'green');
  setTimeout(() => window.location.href = 'index.html', 1200);
}

function doGuestLogin() {
  sessionStorage.setItem('pp_user', JSON.stringify({ id: 'GUEST', name: 'Guest' }));
  showToast('Continuing as guest…');
  setTimeout(() => window.location.href = 'index.html', 1000);
}

// Allow Enter key to submit login
document.getElementById('loginPw')?.addEventListener('keydown', e => {
  if (e.key === 'Enter') doLogin();
});
document.getElementById('loginId')?.addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('loginPw')?.focus();
});

// =============================================
// REGISTER – MULTI-STEP
// =============================================
let currentStep = 1;

function nextStep(from) {
  if (from === 1) {
    clearError('regError1');
    const sid = document.getElementById('regStudentId')?.value.trim();
    const email = document.getElementById('regEmail')?.value.trim();
    const pw    = document.getElementById('regPw')?.value;
    const pwc   = document.getElementById('regPwConfirm')?.value;

    if (!sid || sid.length < 8)       { showError('regError1', 'Please enter a valid Student ID (min 8 digits).'); return; }
    if (!email || !email.includes('@')) { showError('regError1', 'Please enter a valid MMU email address.'); return; }
    if (!pw || pw.length < 8)          { showError('regError1', 'Password must be at least 8 characters.'); return; }
    if (pw !== pwc)                    { showError('regError1', 'Passwords do not match.'); return; }
  }

  if (from === 2) {
    clearError('regError2');
    const name    = document.getElementById('regName')?.value.trim();
    const faculty = document.getElementById('regFaculty')?.value;
    const year    = document.getElementById('regYear')?.value;

    if (!name)    { showError('regError2', 'Please enter your full name.'); return; }
    if (!faculty) { showError('regError2', 'Please select your faculty.'); return; }
    if (!year)    { showError('regError2', 'Please select your year of study.'); return; }
  }

  setStep(from + 1);
}

function prevStep(from) {
  setStep(from - 1);
}

function setStep(step) {
  currentStep = step;
  [1,2,3].forEach(n => {
    const panel = document.getElementById(`panel${n}`);
    const dot   = document.getElementById(`rstep${n}`);
    if (panel) panel.style.display = n === step ? 'block' : 'none';
    if (dot) {
      dot.classList.remove('active', 'done');
      if (n === step) dot.classList.add('active');
      if (n < step)   dot.classList.add('done');
    }
  });
  // Update step bars
  document.querySelectorAll('.reg-step-bar').forEach((bar, i) => {
    bar.classList.toggle('done', i < step - 1);
  });
  // Scroll to top of card
  document.querySelector('.auth-right')?.scrollTo({ top: 0, behavior: 'smooth' });
}

function selectVType(el) {
  document.querySelectorAll('.vtype-card').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
}

function doRegister() {
  clearError('regError3');

  const plate = document.getElementById('regPlate')?.value.trim().toUpperCase();
  const color = document.getElementById('regColor')?.value.trim();
  const terms = document.getElementById('termsCheck')?.checked;
  const vtype = document.querySelector('.vtype-card.active')?.dataset.type || 'car';

  if (!plate) { showError('regError3', 'Please enter your vehicle plate number.'); return; }
  if (!color) { showError('regError3', 'Please enter your vehicle color.'); return; }
  if (!terms) { showError('regError3', 'Please accept the Terms of Use to continue.'); return; }

  // Gather all data
  const userData = {
    studentId:   document.getElementById('regStudentId')?.value.trim(),
    email:       document.getElementById('regEmail')?.value.trim(),
    name:        document.getElementById('regName')?.value.trim(),
    phone:       document.getElementById('regPhone')?.value.trim(),
    faculty:     document.getElementById('regFaculty')?.value,
    year:        document.getElementById('regYear')?.value,
    vehicleType: vtype,
    plate,
    color,
    model:       document.getElementById('regModel')?.value.trim(),
  };

  // In production: POST to /api/register
  // fetch('/api/register', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(userData) })

  sessionStorage.setItem('pp_user', JSON.stringify(userData));

  // Show all panels hidden, show success
  [1,2,3].forEach(n => {
    const panel = document.getElementById(`panel${n}`);
    if (panel) panel.style.display = 'none';
  });
  document.querySelectorAll('.reg-step').forEach(s => { s.classList.remove('active'); s.classList.add('done'); });
  document.querySelectorAll('.reg-step-bar').forEach(b => b.classList.add('done'));

  document.getElementById('loginLink').style.display = 'none';

  document.getElementById('successDetail').innerHTML = `
    <div class="success-row"><span>Student ID</span><span class="success-val">${userData.studentId}</span></div>
    <div class="success-row"><span>Name</span><span class="success-val">${userData.name}</span></div>
    <div class="success-row"><span>Faculty</span><span class="success-val">${userData.faculty?.split(' ')[0] || '-'}</span></div>
    <div class="success-row"><span>Vehicle</span><span class="success-val">${plate} (${color} ${vtype})</span></div>
  `;

  document.getElementById('panelSuccess').style.display = 'block';
}