/**
 * SurakshaVision AI - Industrial Safety Command Center Client Script
 * Zero-Overlapping, Accessible, and 8 Indian Languages Localization Engine.
 * Features:
 *  1. 4-Camera Video Wall (SCADA Control Room Grid)
 *  2. Interactive Calibrated Polygon Danger Geofence Drawer
 *  3. Live Laptop Webcam / Mobile Video Edge AI Inspection Mode
 *  4. Automated EHS Emergency SMS/LoRaWAN Dispatch Simulator
 */

// Application State
const state = {
  currentCamId: 1,
  currentCamData: null,
  selectedLanguage: 'te', // Default to Telangana (Telugu)
  detectedState: 'Telangana',
  currentTheme: 'default',
  currentAudio: null,
  isInspecting: false,
  customFile: null,
  allCameras: [],
  viewMode: 'single', // 'single' | 'wall' | 'webcam'
  
  // Geofence Drawer State
  isDrawingGeofence: false,
  customGeofencePoints: [],

  // Live Webcam State
  webcamStream: null,
  webcamAutoScanTimer: null
};

// Accurate Centroids for Indian States
const INDIAN_STATES = [
  { name: "Telangana", code: "te", lat: 17.3850, lon: 78.4867, label: "Telangana (తెలుగు)" },
  { name: "Andhra Pradesh", code: "te", lat: 16.5062, lon: 80.6480, label: "Andhra Pradesh (తెలుగు)" },
  { name: "Karnataka", code: "kn", lat: 12.9716, lon: 77.5946, label: "Karnataka (ಕನ್ನಡ)" },
  { name: "Tamil Nadu", code: "ta", lat: 13.0827, lon: 80.2707, label: "Tamil Nadu (தமிழ்)" },
  { name: "Maharashtra", code: "mr", lat: 19.7515, lon: 75.7139, label: "Maharashtra (मराठी)" },
  { name: "Odisha", code: "or", lat: 20.2961, lon: 85.8245, label: "Odisha (ଓଡ଼ିଆ)" },
  { name: "Assam", code: "as", lat: 26.1445, lon: 91.7362, label: "Assam (অসমীয়া)" },
  { name: "North India (Delhi/UP/MP)", code: "hi", lat: 28.6139, lon: 77.2090, label: "North India (हिन्दी)" }
];

function findClosestIndianState(userLat, userLon) {
  let closest = INDIAN_STATES[0]; // Default to Telangana
  let minDistanceSq = Infinity;

  for (const st of INDIAN_STATES) {
    const dLat = st.lat - userLat;
    const dLon = st.lon - userLon;
    const distSq = dLat * dLat + dLon * dLon;
    if (distSq < minDistanceSq) {
      minDistanceSq = distSq;
      closest = st;
    }
  }
  return closest;
}

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', async () => {
  initThemeAndControls();
  initGeofenceCanvas();
  await detectLocationAndLanguage();
  await loadCameras();
  await runInspection(1);
  await loadShiftAudit();
});

// 1. Controls & Theme Switcher
function initThemeAndControls() {
  const themeSelect = document.getElementById('theme-select');
  if (themeSelect) {
    themeSelect.addEventListener('change', (e) => {
      document.body.className = '';
      if (e.target.value !== 'default') {
        document.body.classList.add(e.target.value);
      }
      state.currentTheme = e.target.value;
    });
  }

  const langSelect = document.getElementById('lang-select');
  if (langSelect) {
    langSelect.addEventListener('change', (e) => {
      applyLanguage(e.target.value);
    });
  }

  const stateSelect = document.getElementById('state-select');
  if (stateSelect) {
    stateSelect.addEventListener('change', (e) => {
      const selectedName = e.target.value;
      const found = INDIAN_STATES.find(s => s.name === selectedName);
      if (found) {
        state.detectedState = found.name;
        updateLocationBadge(found.name, true);
        applyLanguage(found.code);
      }
    });
  }

  const fileInput = document.getElementById('custom-frame-input');
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        state.customFile = e.target.files[0];
        runInspection(null, state.customFile);
      }
    });
  }
}

// 2. View Mode Tabs (Single Zone vs Video Wall vs Live Webcam)
function switchViewMode(mode) {
  state.viewMode = mode;

  // Toggle Tab Button States
  document.querySelectorAll('.view-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-mode') === mode);
  });

  const singleSec = document.getElementById('single-zone-section');
  const wallSec = document.getElementById('video-wall-section');
  const webcamSec = document.getElementById('webcam-section');

  if (singleSec) singleSec.style.display = mode === 'single' ? 'block' : 'none';
  if (wallSec) wallSec.classList.toggle('active', mode === 'wall');
  if (webcamSec) webcamSec.classList.toggle('active', mode === 'webcam');

  if (mode === 'wall') {
    renderVideoWall();
  } else if (mode === 'webcam') {
    startWebcam();
  } else {
    stopWebcam();
  }
}

// 3. Geolocation & Location Badge Detection
async function detectLocationAndLanguage() {
  updateLocationBadge('Detecting...', false);

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        const matched = findClosestIndianState(latitude, longitude);
        state.detectedState = matched.name;
        syncStateDropdown(matched.name);
        updateLocationBadge(matched.name, true);
        applyLanguage(matched.code);
      },
      async (err) => {
        await fallbackIpDetection();
      },
      { timeout: 4000, maximumAge: 60000 }
    );
  } else {
    await fallbackIpDetection();
  }
}

async function fallbackIpDetection() {
  try {
    const res = await fetch('https://ipapi.co/json/');
    const data = await res.json();
    if (data && (data.region || data.city)) {
      const regionStr = ((data.region || '') + ' ' + (data.city || '')).toLowerCase();
      let matched = INDIAN_STATES[0]; // Telangana default
      if (regionStr.includes('telangana') || regionStr.includes('hyderabad') || regionStr.includes('secunderabad')) {
        matched = INDIAN_STATES[0];
      } else if (regionStr.includes('andhra') || regionStr.includes('vijayawada') || regionStr.includes('visakhapatnam')) {
        matched = INDIAN_STATES[1];
      } else if (regionStr.includes('karnataka') || regionStr.includes('bangalore') || regionStr.includes('bengaluru')) {
        matched = INDIAN_STATES[2];
      } else if (regionStr.includes('tamil') || regionStr.includes('chennai')) {
        matched = INDIAN_STATES[3];
      } else if (regionStr.includes('maharashtra') || regionStr.includes('mumbai') || regionStr.includes('pune')) {
        matched = INDIAN_STATES[4];
      } else if (regionStr.includes('odisha') || regionStr.includes('bhubaneswar')) {
        matched = INDIAN_STATES[5];
      } else if (regionStr.includes('assam') || regionStr.includes('guwahati')) {
        matched = INDIAN_STATES[6];
      }

      state.detectedState = matched.name;
      syncStateDropdown(matched.name);
      updateLocationBadge(matched.name, true);
      applyLanguage(matched.code);
      return;
    }
  } catch (e) {
    // Offline mode
  }

  // Default to Telangana (Telugu)
  state.detectedState = "Telangana";
  syncStateDropdown("Telangana");
  updateLocationBadge("Telangana", true);
  applyLanguage("te");
}

function updateLocationBadge(stateName, isConfirmed) {
  const badge = document.getElementById('location-status');
  if (badge) {
    badge.innerHTML = `📍 <strong>${stateName}</strong> ${isConfirmed ? '✓' : '...'}`;
  }
}

function syncStateDropdown(stateName) {
  const stateSelect = document.getElementById('state-select');
  if (stateSelect) {
    stateSelect.value = stateName;
  }
}

// 4. Multilingual System (8 Indian Languages)
function applyLanguage(lang) {
  state.selectedLanguage = lang;
  const dict = (typeof I18N !== 'undefined' && I18N[lang]) ? I18N[lang] : (I18N.en || {});

  // Update all [data-i18n] tags
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      el.innerText = dict[key];
    }
  });

  // Sync Language select dropdown
  const langSelect = document.getElementById('lang-select');
  if (langSelect && langSelect.value !== lang) {
    langSelect.value = lang;
  }

  // Refresh dynamic camera cards and video wall
  renderCameraCards();
  if (state.viewMode === 'wall') {
    renderVideoWall();
  }

  if (state.currentInspection) {
    updateSirenTranscriptPreview(state.currentInspection);
  }
}

// 5. Load CCTV Cameras from Backend
async function loadCameras() {
  try {
    const res = await fetch('/api/cctv/cameras');
    if (res.ok) {
      state.allCameras = await res.json();
      renderCameraCards();
    }
  } catch (err) {
    console.error("Failed to load CCTV camera feeds:", err);
  }
}

function renderCameraCards() {
  const container = document.getElementById('camera-cards-container');
  if (!container || !state.allCameras.length) return;

  const lang = state.selectedLanguage || 'te';
  const dict = (typeof I18N !== 'undefined' && I18N[lang]) ? I18N[lang] : {};

  container.innerHTML = state.allCameras.map(cam => {
    const isActive = cam.id === state.currentCamId;
    const statusClass = cam.hazard_level === 'Compliant' ? 'compliant' : (cam.hazard_level === 'Warning' ? 'warning' : 'danger');
    
    let displayName = cam.name;
    let displayDesc = cam.description;
    if (dict[`cam${cam.id}Name`]) displayName = dict[`cam${cam.id}Name`];
    if (dict[`cam${cam.id}Desc`]) displayDesc = dict[`cam${cam.id}Desc`];

    return `
      <div class="cam-card ${isActive ? 'active' : ''}" onclick="selectCamera(${cam.id})">
        <div class="cam-card-top">
          <span class="cam-tag">${cam.cam_code}</span>
          <span class="status-pill ${statusClass}">
            <span class="live-dot" style="background:${statusClass === 'compliant' ? '#10b981' : (statusClass === 'warning' ? '#f59e0b' : '#ef4444')}"></span>
            ${cam.hazard_level}
          </span>
        </div>
        <div class="cam-name">${displayName}</div>
        <div class="cam-desc">${displayDesc}</div>
        <div class="cam-meta">
          <span>FPS: ${cam.fps}</span>
          <span>Res: ${cam.resolution}</span>
        </div>
      </div>
    `;
  }).join('');
}

function selectCamera(camId) {
  state.currentCamId = camId;
  state.customFile = null;
  state.customGeofencePoints = [];
  resetGeofenceCanvas();
  switchViewMode('single');
  renderCameraCards();
  runInspection(camId);
}

// 6. FEATURE 2: 4-Camera Video Wall (SCADA Control Room)
function renderVideoWall() {
  const container = document.getElementById('video-wall-grid');
  if (!container || !state.allCameras.length) return;

  const lang = state.selectedLanguage || 'te';
  const dict = (typeof I18N !== 'undefined' && I18N[lang]) ? I18N[lang] : {};

  container.innerHTML = state.allCameras.map(cam => {
    const statusClass = cam.hazard_level === 'Compliant' ? 'compliant' : (cam.hazard_level === 'Warning' ? 'warning' : 'danger');
    let displayName = cam.name;
    if (dict[`cam${cam.id}Name`]) displayName = dict[`cam${cam.id}Name`];

    return `
      <div class="video-wall-card" onclick="selectCamera(${cam.id})">
        <div class="wall-feed-header">
          <div style="display:flex; align-items:center; gap:0.5rem; font-family:var(--font-mono); font-size:0.75rem; color:#fff;">
            <span class="live-dot"></span>
            <strong>${cam.cam_code}</strong>: ${displayName}
          </div>
          <span class="status-pill ${statusClass}" style="font-size:0.65rem; padding:0.15rem 0.45rem;">
            ${cam.hazard_level}
          </span>
        </div>
        <img class="wall-feed-img" src="/data/cctv_feeds/${cam.feed_file}" alt="${cam.name}">
        <div class="wall-feed-footer">
          <span style="font-family:var(--font-mono); font-size:0.72rem; color:var(--accent-yellow);">● REC | ${cam.fps} FPS | ${cam.resolution}</span>
          <button class="btn btn-primary" style="padding:0.25rem 0.65rem; font-size:0.72rem;">
            🔍 Inspect Zone
          </button>
        </div>
      </div>
    `;
  }).join('');
}

// 7. FEATURE 3: Interactive Geofence Drawer
function initGeofenceCanvas() {
  const canvas = document.getElementById('geofence-canvas');
  if (!canvas) return;

  canvas.addEventListener('click', (e) => {
    if (!state.isDrawingGeofence) return;

    const rect = canvas.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);

    // Scale to original image dimensions (e.g. 1280x720)
    const scaleX = 1280 / rect.width;
    const scaleY = 720 / rect.height;

    state.customGeofencePoints.push([Math.round(x * scaleX), Math.round(y * scaleY)]);
    drawGeofencePointsOnCanvas(rect.width, rect.height);
  });
}

function toggleGeofenceDrawer() {
  state.isDrawingGeofence = !state.isDrawingGeofence;
  const feedArea = document.getElementById('feed-display-area');
  const banner = document.getElementById('geofence-banner');
  const btn = document.getElementById('btn-draw-geofence');

  if (feedArea) feedArea.classList.toggle('geofence-drawing', state.isDrawingGeofence);
  if (banner) banner.classList.toggle('active', state.isDrawingGeofence);

  if (state.isDrawingGeofence) {
    if (btn) btn.innerHTML = '✏️ <span>Drawing Geofence (Click Feed)...</span>';
    state.customGeofencePoints = [];
    resetGeofenceCanvas();
  } else {
    if (btn) btn.innerHTML = '✍️ <span>Calibrate Geofence</span>';
  }
}

function drawGeofencePointsOnCanvas(w, h) {
  const canvas = document.getElementById('geofence-canvas');
  if (!canvas) return;
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, w, h);

  if (state.customGeofencePoints.length === 0) return;

  const scaleX = w / 1280;
  const scaleY = h / 720;

  // Draw polygon path
  ctx.beginPath();
  const first = state.customGeofencePoints[0];
  ctx.moveTo(first[0] * scaleX, first[1] * scaleY);

  for (let i = 1; i < state.customGeofencePoints.length; i++) {
    const pt = state.customGeofencePoints[i];
    ctx.lineTo(pt[0] * scaleX, pt[1] * scaleY);
  }

  if (state.customGeofencePoints.length >= 3) {
    ctx.closePath();
    ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
    ctx.fill();
  }

  ctx.strokeStyle = '#ef4444';
  ctx.lineWidth = 2.5;
  ctx.stroke();

  // Draw vertices dots
  state.customGeofencePoints.forEach((pt, idx) => {
    ctx.beginPath();
    ctx.arc(pt[0] * scaleX, pt[1] * scaleY, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#f59e0b';
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.5;
    ctx.stroke();
  });

  const countElem = document.getElementById('geofence-points-count');
  if (countElem) {
    countElem.innerText = `${state.customGeofencePoints.length} points placed`;
  }
}

function armCustomGeofence() {
  if (state.customGeofencePoints.length < 3) {
    alert("Please click at least 3 points on the CCTV feed to define a hazard polygon.");
    return;
  }
  state.isDrawingGeofence = false;
  const feedArea = document.getElementById('feed-display-area');
  const banner = document.getElementById('geofence-banner');
  const btn = document.getElementById('btn-draw-geofence');
  if (feedArea) feedArea.classList.remove('geofence-drawing');
  if (banner) banner.classList.remove('active');
  if (btn) btn.innerHTML = '✍️ <span>Calibrate Geofence</span>';

  // Run inspection with custom geofence
  runInspection(state.currentCamId, null, state.customGeofencePoints);
}

function resetGeofence() {
  state.customGeofencePoints = [];
  state.isDrawingGeofence = false;
  resetGeofenceCanvas();
  const feedArea = document.getElementById('feed-display-area');
  const banner = document.getElementById('geofence-banner');
  const btn = document.getElementById('btn-draw-geofence');
  if (feedArea) feedArea.classList.remove('geofence-drawing');
  if (banner) banner.classList.remove('active');
  if (btn) btn.innerHTML = '✍️ <span>Calibrate Geofence</span>';

  runInspection(state.currentCamId);
}

function resetGeofenceCanvas() {
  const canvas = document.getElementById('geofence-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

// 8. Run Computer Vision Inspection
async function runInspection(camId = null, customFile = null, customGeofence = null) {
  const targetCamId = camId || state.currentCamId || 1;
  state.isInspecting = true;

  const btnScan = document.getElementById('btn-scan');
  if (btnScan) {
    btnScan.innerHTML = '⏳ <span>Scanning Feed...</span>';
    btnScan.disabled = true;
  }

  try {
    const formData = new FormData();
    formData.append('cam_id', targetCamId);
    if (customFile) {
      formData.append('file', customFile);
    }
    if (customGeofence && customGeofence.length >= 3) {
      formData.append('custom_geofence', JSON.stringify(customGeofence));
    }

    const res = await fetch('/api/cctv/inspect', {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      const data = await res.json();
      state.currentInspection = data;
      renderInspectionResults(data);

      // Check for automated emergency dispatch
      if (data.emergency_dispatch) {
        showEmergencyDispatchToast(data.emergency_dispatch);
      }
    } else {
      alert("Inspection failed. Please check CCTV camera feed.");
    }
  } catch (err) {
    console.error("Inspection error:", err);
  } finally {
    state.isInspecting = false;
    if (btnScan) {
      const dict = (typeof I18N !== 'undefined' && I18N[state.selectedLanguage]) ? I18N[state.selectedLanguage] : {};
      btnScan.innerHTML = `🔍 <span>${dict.btnScanNow || 'Run Safety Inspection'}</span>`;
      btnScan.disabled = false;
    }
  }
}

// 9. FEATURE 1: Live Webcam Stream & Inspection
async function startWebcam() {
  const videoElem = document.getElementById('webcam-video');
  const statusElem = document.getElementById('webcam-status-pill');

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Webcam access is not supported in this browser.");
    return;
  }

  try {
    state.webcamStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 } }
    });
    if (videoElem) {
      videoElem.srcObject = state.webcamStream;
      videoElem.play();
    }
    if (statusElem) {
      statusElem.className = 'status-pill compliant';
      statusElem.innerHTML = '<span class="live-dot" style="background:#10b981;"></span> WEBCAM LIVE';
    }
  } catch (err) {
    console.error("Webcam access error:", err);
    if (statusElem) {
      statusElem.className = 'status-pill danger';
      statusElem.innerText = 'WEBCAM BLOCKED';
    }
    alert("Could not access webcam. Please check browser permissions.");
  }
}

function stopWebcam() {
  if (state.webcamStream) {
    state.webcamStream.getTracks().forEach(track => track.stop());
    state.webcamStream = null;
  }
  const videoElem = document.getElementById('webcam-video');
  if (videoElem) videoElem.srcObject = null;

  const statusElem = document.getElementById('webcam-status-pill');
  if (statusElem) {
    statusElem.className = 'status-pill warning';
    statusElem.innerText = 'WEBCAM STANDBY';
  }
}

async function inspectWebcamFrame() {
  const videoElem = document.getElementById('webcam-video');
  if (!videoElem || !state.webcamStream) {
    alert("Please start the webcam first!");
    return;
  }

  const canvas = document.createElement('canvas');
  canvas.width = videoElem.videoWidth || 640;
  canvas.height = videoElem.videoHeight || 480;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoElem, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(async (blob) => {
    if (!blob) return;
    const formData = new FormData();
    formData.append('file', blob, 'webcam_frame.jpg');

    const btn = document.getElementById('btn-inspect-webcam');
    if (btn) btn.innerHTML = '⏳ <span>Analyzing Live Frame...</span>';

    try {
      const res = await fetch('/api/cctv/inspect-webcam', {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        // Render results into webcam result container
        const resultImg = document.getElementById('webcam-annotated-result');
        if (resultImg) {
          resultImg.src = data.annotated_image;
          resultImg.style.display = 'block';
        }

        const scoreElem = document.getElementById('webcam-score-val');
        if (scoreElem) scoreElem.innerText = `${data.compliance_score}%`;

        const alertElem = document.getElementById('webcam-alert-text');
        if (alertElem) {
          if (data.violations && data.violations.length > 0) {
            alertElem.innerHTML = `<span style="color:var(--accent-red); font-weight:700;">🚨 ${data.violations[0].type}</span> - ${data.violations[0].action}`;
            // Play audible siren
            playCurrentSiren(data.violations[0].type.includes('Fall') ? 'slip_fall_incident' : 'helmet_violation');
          } else {
            alertElem.innerHTML = '<span style="color:var(--accent-green); font-weight:700;">✅ 100% PPE COMPLIANT:</span> Hard hat detected on live subject.';
          }
        }
      }
    } catch (e) {
      console.error("Webcam inspection error:", e);
    } finally {
      if (btn) {
        const dict = (typeof I18N !== 'undefined' && I18N[state.selectedLanguage]) ? I18N[state.selectedLanguage] : {};
        btn.innerHTML = `📸 <span>${dict.btnInspectWebcam || 'Inspect Live Frame'}</span>`;
      }
    }
  }, 'image/jpeg', 0.9);
}

// 10. Render Inspection Results & Visuals
function renderInspectionResults(data) {
  // 1. CCTV Frame Display
  const imgElem = document.getElementById('cctv-live-frame');
  if (imgElem && data.annotated_image) {
    imgElem.src = data.annotated_image;
  }

  // 2. Camera Header info
  const camInfoText = document.getElementById('cctv-cam-title');
  if (camInfoText && data.camera_metadata) {
    camInfoText.innerText = `${data.camera_metadata.cam_code}: ${data.camera_metadata.name}`;
  }

  const fpsText = document.getElementById('cctv-fps');
  if (fpsText && data.camera_metadata) {
    fpsText.innerText = `${data.camera_metadata.fps} FPS`;
  }

  // 3. Safety Score Gauge
  const score = data.compliance_score || 0;
  const scoreElem = document.getElementById('score-circle');
  if (scoreElem) {
    scoreElem.className = 'score-circle ' + (score >= 90 ? 'compliant' : (score >= 70 ? 'warning' : 'danger'));
    scoreElem.innerHTML = `${score}%<span>SCORE</span>`;
  }

  // 4. Counts Breakdown
  const workersCountElem = document.getElementById('workers-count-val');
  if (workersCountElem) workersCountElem.innerText = data.workers_detected || 0;

  const helmetsCountElem = document.getElementById('helmets-count-val');
  if (helmetsCountElem) helmetsCountElem.innerText = `${data.helmets_detected || 0} / ${data.workers_detected || 0}`;

  const vestsCountElem = document.getElementById('vests-count-val');
  if (vestsCountElem) vestsCountElem.innerText = `${data.vests_detected || 0} / ${data.workers_detected || 0}`;

  const violationsCountElem = document.getElementById('violations-count-val');
  if (violationsCountElem) violationsCountElem.innerText = (data.violations || []).length;

  // 5. Violations List
  const violationsList = document.getElementById('violations-list-container');
  if (violationsList) {
    if (!data.violations || data.violations.length === 0) {
      violationsList.innerHTML = `
        <div class="violation-item ok">
          <span>✅</span>
          <div>
            <strong>100% Safety Compliance Verified</strong>
            <div>All floor personnel equipped with mandatory Hard Hats and Hi-Vis reflective vests.</div>
          </div>
        </div>
      `;
    } else {
      violationsList.innerHTML = data.violations.map(v => {
        const isCritical = v.severity === 'CRITICAL' || v.severity === 'EMERGENCY';
        return `
          <div class="violation-item ${isCritical ? 'critical' : 'warning'}">
            <span>${isCritical ? '🚨' : '⚠️'}</span>
            <div>
              <strong>${v.title || v.type} (${v.severity})</strong>
              <div>${v.action || v.description}</div>
              <div style="font-size:0.75rem; color:var(--text-dim); margin-top:0.2rem;">Location: ${v.zone || 'Floor Zone'} | Regulation: ${v.osha_standard || 'OSHA 1910'}</div>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  // 6. Siren Transcript Preview
  updateSirenTranscriptPreview(data);
}

function updateSirenTranscriptPreview(data) {
  const transcriptBox = document.getElementById('siren-transcript');
  if (!transcriptBox) return;

  const lang = state.selectedLanguage || 'te';
  let alertKey = "full_compliance";

  if (data.violations && data.violations.length > 0) {
    const firstType = (data.violations[0].type || '').toLowerCase();
    if (firstType.includes('fall') || firstType.includes('down')) alertKey = 'slip_fall_incident';
    else if (firstType.includes('intrusion') || firstType.includes('geofence')) alertKey = 'danger_zone_intrusion';
    else alertKey = 'helmet_violation';
  }

  fetch('/api/cctv/siren', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ alert_key: alertKey, lang: lang })
  })
  .then(res => res.json())
  .then(sirenData => {
    transcriptBox.innerHTML = `
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
        <span style="font-weight:700; color:var(--accent-yellow);">📢 [Voice Alarm: ${sirenData.language.toUpperCase()}]:</span>
      </div>
      <div>"${sirenData.alert_text}"</div>
    `;
    transcriptBox.setAttribute('data-audio-url', sirenData.audio_url);
    transcriptBox.setAttribute('data-alert-key', alertKey);
  })
  .catch(e => console.error("Siren preview error:", e));
}

// 11. Play Emergency Voice Siren Alert
async function playCurrentSiren(forcedKey = null) {
  const transcriptBox = document.getElementById('siren-transcript');
  const alertKey = forcedKey || (transcriptBox ? (transcriptBox.getAttribute('data-alert-key') || 'helmet_violation') : 'helmet_violation');
  const lang = state.selectedLanguage || 'te';

  const btnSiren = document.getElementById('btn-play-siren');
  if (btnSiren) {
    btnSiren.innerHTML = '🔊 <span>Sounding Siren...</span>';
  }

  try {
    const res = await fetch('/api/cctv/siren', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alert_key: alertKey, lang: lang })
    });

    if (res.ok) {
      const data = await res.json();
      if (state.currentAudio) {
        state.currentAudio.pause();
      }

      state.currentAudio = new Audio(data.audio_url);
      state.currentAudio.play();

      state.currentAudio.onended = () => {
        if (btnSiren) {
          const dict = (typeof I18N !== 'undefined' && I18N[state.selectedLanguage]) ? I18N[state.selectedLanguage] : {};
          btnSiren.innerHTML = `🚨 <span>${dict.btnSirenTest || 'Sound Spoken Siren Alert'}</span>`;
        }
      };
    }
  } catch (err) {
    console.error("Audio playback error:", err);
  }
}

// 12. FEATURE 4: Automated EHS Emergency Dispatch Toast
function showEmergencyDispatchToast(dispatch) {
  const toast = document.getElementById('dispatch-toast');
  if (!toast) return;

  const idElem = document.getElementById('dispatch-id');
  if (idElem) idElem.innerText = dispatch.dispatch_id;

  const incElem = document.getElementById('dispatch-incident');
  if (incElem) incElem.innerText = dispatch.incident_type;

  const zoneElem = document.getElementById('dispatch-zone');
  if (zoneElem) zoneElem.innerText = dispatch.zone_location;

  const targetElem = document.getElementById('dispatch-target');
  if (targetElem) targetElem.innerText = dispatch.recipient;

  const etaElem = document.getElementById('dispatch-eta');
  if (etaElem) etaElem.innerText = dispatch.eta_response_team;

  toast.classList.add('active');
}

function dismissDispatchToast() {
  const toast = document.getElementById('dispatch-toast');
  if (toast) toast.classList.remove('active');
}

function acknowledgeDispatch() {
  alert("Emergency incident acknowledged! First responder medical dispatch confirmed.");
  dismissDispatchToast();
}

// 13. Shift Safety Audit & ISO 45001 Certification
async function loadShiftAudit() {
  try {
    const res = await fetch('/api/safety/audit');
    if (res.ok) {
      const audit = await res.json();
      renderShiftAudit(audit);
    }
  } catch (e) {
    console.error("Failed to load shift safety audit:", e);
  }
}

function renderShiftAudit(audit) {
  const shiftElem = document.getElementById('audit-shift-id');
  if (shiftElem) shiftElem.innerText = audit.shift_id;

  const dateElem = document.getElementById('audit-date');
  if (dateElem) dateElem.innerText = audit.audit_timestamp;

  const auditorElem = document.getElementById('audit-officer');
  if (auditorElem) auditorElem.innerText = audit.ehs_officer;

  const complianceElem = document.getElementById('audit-overall-score');
  if (complianceElem) complianceElem.innerText = `${audit.shift_compliance_score}%`;

  const totalWorkersElem = document.getElementById('audit-total-workers');
  if (totalWorkersElem) totalWorkersElem.innerText = audit.total_workers_scanned;

  const totalIncidentsElem = document.getElementById('audit-total-incidents');
  if (totalIncidentsElem) totalIncidentsElem.innerText = audit.incidents_recorded;

  const tableBody = document.getElementById('audit-table-body');
  if (tableBody && audit.incidents) {
    tableBody.innerHTML = audit.incidents.map(inc => `
      <tr>
        <td style="font-family:var(--font-mono);">${inc.time}</td>
        <td><strong>${inc.zone}</strong></td>
        <td><span class="status-pill ${inc.severity === 'CRITICAL' ? 'danger' : 'warning'}">${inc.incident}</span></td>
        <td>${inc.action_taken}</td>
        <td style="color:${inc.status === 'RESOLVED' ? '#10b981' : '#f59e0b'}; font-weight:700;">${inc.status}</td>
      </tr>
    `).join('');
  }
}

function printAuditReport() {
  window.print();
}
