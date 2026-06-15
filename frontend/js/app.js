// Frieren Cognitive AI Control Center Core Logic

// State management variables
let config = {
  backendUrl: 'http://localhost:8000',
  apiKey: 'frieren-dev-key-123',
  userId: 'vikash',
  deviceId: 'browser-client',
  sessionId: ''
};

let voiceSettings = {
  enabled: true,
  autoSpeak: true,
  rate: 0.9,
  volume: 1.0,
  pitch: 1.0
};

let systemState = 'AWAKE';
let recognition = null;
let isListening = false;
let pollingInterval = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
  initSettings();
  setupNavigation();
  setupEventListeners();
  initVoiceSettings();
  registerServiceWorker();
  
  // Initial checks
  checkBackendHealth();
  refreshMemoryStats();
  
  // Start polling connection & health every 10 seconds
  pollingInterval = setInterval(() => {
    checkBackendHealth();
  }, 10000);
});

// ─── 1. SETTINGS & LOCALSTORAGE ──────────────────────────────────────────────

function initSettings() {
  // Load settings from localStorage or write defaults
  if (localStorage.getItem('frieren_backend_url')) {
    config.backendUrl = localStorage.getItem('frieren_backend_url');
    config.apiKey = localStorage.getItem('frieren_api_key');
    config.userId = localStorage.getItem('frieren_user_id');
    config.deviceId = localStorage.getItem('frieren_device_id');
    config.sessionId = localStorage.getItem('frieren_session_id');
  } else {
    config.sessionId = generateUUID();
    saveSettingsToStorage();
  }

  // Generate session ID if missing
  if (!config.sessionId) {
    config.sessionId = generateUUID();
    localStorage.setItem('frieren_session_id', config.sessionId);
  }

  // Populate settings modal inputs
  document.getElementById('set-backend-url').value = config.backendUrl;
  document.getElementById('set-api-key').value = config.apiKey;
  document.getElementById('set-user-id').value = config.userId;
  document.getElementById('set-device-id').value = config.deviceId;
  document.getElementById('set-session-id').value = config.sessionId;
}

function saveSettingsToStorage() {
  localStorage.setItem('frieren_backend_url', config.backendUrl);
  localStorage.setItem('frieren_api_key', config.apiKey);
  localStorage.setItem('frieren_user_id', config.userId);
  localStorage.setItem('frieren_device_id', config.deviceId);
  localStorage.setItem('frieren_session_id', config.sessionId);
}

function generateUUID() {
  return 'sess-' + Math.random().toString(36).substr(2, 9) + '-' + Date.now().toString(36).substr(-4);
}

// ─── 2. TABBED NAVIGATION ────────────────────────────────────────────────────

function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item, .mobile-nav-item');
  const panels = document.querySelectorAll('.content-panel');
  const panelTitle = document.getElementById('current-panel-title');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetId = item.getAttribute('data-target');
      
      // Update Active Navigation State in UI
      navItems.forEach(nav => nav.classList.remove('active'));
      
      // Highlight matching desktop and mobile navigation buttons
      document.querySelectorAll(`[data-target="${targetId}"]`).forEach(el => el.classList.add('active'));

      // Show Selected Panel
      panels.forEach(panel => {
        if (panel.id === targetId) {
          panel.classList.add('active');
        } else {
          panel.classList.remove('active');
        }
      });

      // Update Panel Header Title
      let title = 'Chat Room';
      if (targetId === 'panel-memory') title = 'Memory Explorer';
      else if (targetId === 'panel-controls') title = 'Control Panel';
      else if (targetId === 'panel-metrics') title = 'System Metrics & Diagnostics';
      else if (targetId === 'panel-actions') title = 'Representative Actions';
      else if (targetId === 'panel-history') title = 'Conversation History Log';
      panelTitle.textContent = title;

      // Trigger panels data updates on tab load
      if (targetId === 'panel-metrics') {
        checkBackendHealth();
        refreshMemoryStats();
      } else if (targetId === 'panel-memory') {
        fetchMemorySearch('');
      } else if (targetId === 'panel-actions') {
        fetchRepresentativeTasks();
      } else if (targetId === 'panel-history') {
        fetchHistoryLogs();
      }
    });
  });
}

// ─── 3. BACKEND API TELEMETRY (HEALTH & STATE) ───────────────────────────────

async function checkBackendHealth() {
  const dot = document.getElementById('connection-dot');
  const lbl = document.getElementById('connection-lbl');
  
  try {
    const res = await fetch(`${config.backendUrl}/api/v1/health`, {
      headers: { 'X-API-Key': config.apiKey }
    });
    
    if (res.ok) {
      const healthData = await res.json();
      dot.className = 'status-dot online';
      lbl.textContent = 'Online';
      
      // Update Advanced Diagnostics metrics panel if present
      updateDiagnosticsPanel(healthData);
    } else {
      setOfflineState(dot, lbl);
    }
  } catch (err) {
    setOfflineState(dot, lbl);
  }

  // Check system operational sleep state
  try {
    const resState = await fetch(`${config.backendUrl}/api/v1/system/status`, {
      headers: { 'X-API-Key': config.apiKey }
    });
    if (resState.ok) {
      const stateData = await resState.json();
      updateSystemStateUI(stateData.status);
    }
  } catch (err) {
    console.warn('System status check failed:', err);
  }
}

function setOfflineState(dot, lbl) {
  dot.className = 'status-dot offline';
  lbl.textContent = 'Offline';
  
  // Set all telemetry status badges to degraded/offline
  const badges = document.querySelectorAll('.diagnostic-badge');
  badges.forEach(b => {
    b.className = 'diagnostic-badge red';
    b.textContent = 'Offline';
  });
}

function updateDiagnosticsPanel(data) {
  updateBadgeState('diag-sqlite', data.sqlite === 'connected' ? 'green' : 'red', data.sqlite);
  updateBadgeState('diag-redis', data.redis === 'connected' ? 'green' : 'red', data.redis);
  updateBadgeState('diag-chromadb', data.chromadb === 'connected' ? 'green' : 'red', data.chromadb);
  
  updateBadgeState('diag-memory', data.memory_system === 'active' ? 'green' : 'red', data.memory_system);
  updateBadgeState('diag-reasoning', data.reasoning_engine === 'active' ? 'green' : 'red', data.reasoning_engine);
  updateBadgeState('diag-reflection', data.reflection_engine === 'active' ? 'green' : 'red', data.reflection_engine);
  updateBadgeState('diag-representative', data.representative_engine === 'active' ? 'green' : 'red', data.representative_engine);
  updateBadgeState('diag-proactive', data.proactive_assistant === 'active' ? 'green' : (data.proactive_assistant === 'paused' ? 'yellow' : 'red'), data.proactive_assistant);
}

function updateBadgeState(id, colorClass, text) {
  const el = document.getElementById(id);
  if (el) {
    el.className = `diagnostic-badge ${colorClass}`;
    el.textContent = text.toUpperCase();
  }
}

async function refreshMemoryStats() {
  try {
    const res = await fetch(`${config.backendUrl}/api/v1/memory/stats`, {
      headers: { 'X-API-Key': config.apiKey }
    });
    if (res.ok) {
      const stats = await res.json();
      document.getElementById('metric-semantic').textContent = stats.semantic_count;
      document.getElementById('metric-episodic').textContent = stats.episodic_count;
      document.getElementById('metric-goals').textContent = stats.goals_count;
      document.getElementById('metric-projects').textContent = stats.projects_count;
      document.getElementById('metric-skills').textContent = stats.skills_count;
      document.getElementById('metric-reflections').textContent = stats.reflections_count;
    }
  } catch (err) {
    console.warn('Memory stats polling failed:', err);
  }
}

function updateSystemStateUI(state) {
  systemState = state;
  const badge = document.getElementById('state-badge');
  const icon = document.getElementById('state-icon');
  const lbl = document.getElementById('state-lbl');
  const micBtn = document.getElementById('btn-toggle-mic');

  if (state === 'AWAKE') {
    badge.className = 'state-display-badge awake';
    icon.className = 'fa-solid fa-sun';
    lbl.textContent = 'AWAKE';
    if (micBtn) {
      micBtn.disabled = false;
      micBtn.style.opacity = '1';
      micBtn.title = 'Voice Input';
    }
  } else {
    badge.className = 'state-display-badge sleeping';
    icon.className = 'fa-solid fa-moon';
    lbl.textContent = 'SLEEPING';
    if (micBtn) {
      micBtn.disabled = true;
      micBtn.style.opacity = '0.4';
      micBtn.title = 'Voice disabled while sleeping';
      if (isListening) stopSpeechRecognition();
    }
  }
}

// ─── 4. CHAT ROOM ENGINE ─────────────────────────────────────────────────────

async function sendChatMessage() {
  const inputEl = document.getElementById('chat-input');
  const msgText = inputEl.value.trim();
  if (!msgText) return;

  // Clear input
  inputEl.value = '';

  // Append user bubble
  appendMessageBubble('user', msgText);

  // Append thinking bubble
  const thinkingId = appendThinkingBubble();

  try {
    const res = await fetch(`${config.backendUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'X-API-Key': config.apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: config.userId,
        device_id: config.deviceId,
        message: msgText
      })
    });

    // Remove thinking indicator
    removeThinkingBubble(thinkingId);

    if (res.ok) {
      const data = await res.json();
      
      // Simulate streaming token response with typewriter effect
      appendMessageBubbleTypewriter('frieren', data.response);
      
      // Update session ID if it changes
      if (data.session_id && data.session_id !== config.sessionId) {
        config.sessionId = data.session_id;
        document.getElementById('set-session-id').value = config.sessionId;
        localStorage.setItem('frieren_session_id', config.sessionId);
      }
    } else {
      appendMessageBubble('frieren', 'Error: Frieren failed to retrieve a response.');
    }
  } catch (err) {
    removeThinkingBubble(thinkingId);
    appendMessageBubble('frieren', 'Could not contact the cognitive backend. Please check connection.');
  }
}

function appendMessageBubble(sender, text) {
  const container = document.getElementById('chat-messages');
  const wrapper = document.createElement('div');
  wrapper.className = `message-wrapper ${sender}`;
  
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  wrapper.innerHTML = `
    <div class="message-bubble">${text}</div>
    <div class="message-timestamp">${time}</div>
  `;
  
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

function appendMessageBubbleTypewriter(sender, text) {
  const container = document.getElementById('chat-messages');
  const wrapper = document.createElement('div');
  wrapper.className = `message-wrapper ${sender}`;
  
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  
  const timeEl = document.createElement('div');
  timeEl.className = 'message-timestamp';
  timeEl.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  wrapper.appendChild(bubble);
  wrapper.appendChild(timeEl);
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;

  // Voice playback trigger (triggering immediately or after typing, starting immediately feels more natural)
  if (voiceSettings.enabled && voiceSettings.autoSpeak) {
    speakText(text);
  }

  // Typewriter loop simulation
  let i = 0;
  function type() {
    if (i < text.length) {
      bubble.textContent += text.charAt(i);
      i++;
      container.scrollTop = container.scrollHeight;
      setTimeout(type, 15); // Speed multiplier
    }
  }
  type();
}

function appendThinkingBubble() {
  const container = document.getElementById('chat-messages');
  const id = 'thinking-' + Date.now();
  const wrapper = document.createElement('div');
  wrapper.className = 'message-wrapper frieren';
  wrapper.id = id;
  wrapper.innerHTML = `
    <div class="message-bubble typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeThinkingBubble(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ─── 5. VOICE: SPEECH RECOGNITION & SYNTHESIS ────────────────────────────────

function initVoiceSettings() {
  // Load settings from localStorage
  if (localStorage.getItem('frieren_voice_enabled')) {
    voiceSettings.enabled = localStorage.getItem('frieren_voice_enabled') === 'true';
    voiceSettings.autoSpeak = localStorage.getItem('frieren_voice_autospeak') === 'true';
    voiceSettings.rate = parseFloat(localStorage.getItem('frieren_voice_rate'));
    voiceSettings.volume = parseFloat(localStorage.getItem('frieren_voice_volume'));
    voiceSettings.pitch = parseFloat(localStorage.getItem('frieren_voice_pitch'));
  }

  // Populate voice UI fields
  document.getElementById('voice-toggle-enabled').checked = voiceSettings.enabled;
  document.getElementById('voice-toggle-autospeak').checked = voiceSettings.autoSpeak;
  document.getElementById('voice-rate').value = voiceSettings.rate;
  document.getElementById('voice-volume').value = voiceSettings.volume;
  document.getElementById('voice-pitch').value = voiceSettings.pitch;
  
  updateVoiceLabels();

  // Toggle speaker button state in Chat Input
  updateSpeakerButtonUI();

  // Setup Web Speech Recognition API
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => {
      isListening = true;
      document.getElementById('btn-toggle-mic').classList.add('active-mic');
      document.getElementById('btn-toggle-mic').innerHTML = '<i class="fa-solid fa-face-gasp"></i>';
    };

    recognition.onresult = (event) => {
      const resultText = event.results[0][0].transcript;
      document.getElementById('chat-input').value = resultText;
    };

    recognition.onerror = (err) => {
      console.error('Speech recognition error:', err.error);
      stopSpeechRecognition();
    };

    recognition.onend = () => {
      stopSpeechRecognition();
    };
  } else {
    document.getElementById('btn-toggle-mic').style.display = 'none'; // Hide if unsupported
  }
}

function updateVoiceLabels() {
  document.getElementById('lbl-voice-rate').textContent = voiceSettings.rate + 'x';
  document.getElementById('lbl-voice-volume').textContent = Math.round(voiceSettings.volume * 100) + '%';
  document.getElementById('lbl-voice-pitch').textContent = voiceSettings.pitch.toFixed(1);
}

function updateSpeakerButtonUI() {
  const speakBtn = document.getElementById('btn-toggle-speak');
  if (voiceSettings.enabled) {
    speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
    speakBtn.style.color = 'var(--color-gold)';
  } else {
    speakBtn.innerHTML = '<i class="fa-solid fa-volume-xmark"></i>';
    speakBtn.style.color = 'var(--text-muted)';
  }
}

function toggleVoiceOutputGlobal() {
  voiceSettings.enabled = !voiceSettings.enabled;
  localStorage.setItem('frieren_voice_enabled', voiceSettings.enabled);
  document.getElementById('voice-toggle-enabled').checked = voiceSettings.enabled;
  updateSpeakerButtonUI();
}

function startSpeechRecognition() {
  if (systemState === 'SLEEPING') return;
  if (recognition) {
    try {
      recognition.start();
    } catch (e) {
      console.warn('Recognition already started');
    }
  }
}

function stopSpeechRecognition() {
  isListening = false;
  const micBtn = document.getElementById('btn-toggle-mic');
  if (micBtn) {
    micBtn.classList.remove('active-mic');
    micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
  }
  if (recognition) {
    try {
      recognition.stop();
    } catch (e) {}
  }
}

function speakText(text) {
  if (!voiceSettings.enabled || !window.speechSynthesis) return;

  // Stop active speech synthesis
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = voiceSettings.rate;
  utterance.volume = voiceSettings.volume;
  utterance.pitch = voiceSettings.pitch;

  // Attempt to select a calm elven-like female voice
  const voices = window.speechSynthesis.getVoices();
  const femaleVoice = voices.find(v => 
    v.lang.startsWith('en') && 
    (v.name.toLowerCase().includes('female') || 
     v.name.toLowerCase().includes('zira') || 
     v.name.toLowerCase().includes('google us english') ||
     v.name.toLowerCase().includes('samantha'))
  );
  if (femaleVoice) {
    utterance.voice = femaleVoice;
  }

  window.speechSynthesis.speak(utterance);
}

// ─── 6. MEMORY EXPLORER PANEL ────────────────────────────────────────────────

async function fetchMemorySearch(query = '') {
  const resultsContainer = document.getElementById('memory-results');
  resultsContainer.innerHTML = '<div style="color: var(--text-muted);">Fetching memories from ChromaDB...</div>';

  try {
    const res = await fetch(`${config.backendUrl}/api/v1/memory/search?q=${encodeURIComponent(query)}`, {
      headers: { 'X-API-Key': config.apiKey }
    });

    if (res.ok) {
      const memories = await res.json();
      renderMemoryCards(memories);
    } else {
      resultsContainer.innerHTML = '<div style="color: var(--color-red);">Failed to pull memories. Check API Key.</div>';
    }
  } catch (err) {
    resultsContainer.innerHTML = '<div style="color: var(--color-red);">Error connecting to memory endpoint.</div>';
  }
}

function renderMemoryCards(memories) {
  const resultsContainer = document.getElementById('memory-results');
  resultsContainer.innerHTML = '';
  
  if (memories.length === 0) {
    resultsContainer.innerHTML = '<div style="color: var(--text-muted); grid-column: 1/-1;">No memories found matching query.</div>';
    return;
  }

  // Get active filter
  const activeFilter = document.querySelector('.filter-btn.active').getAttribute('data-filter');

  memories.forEach(m => {
    // Apply client-side filter toggle
    if (activeFilter !== 'all' && m.type !== activeFilter) {
      return;
    }

    const card = document.createElement('div');
    card.className = 'memory-card';
    
    // Format timestamp nicely
    let dateStr = 'Unknown';
    if (m.created_date) {
      try {
        dateStr = new Date(m.created_date).toLocaleString();
      } catch (e) {}
    }

    card.innerHTML = `
      <div>
        <div class="memory-header">
          <span class="memory-badge ${m.type}">${m.type}</span>
          <span style="font-size: 11px; background: rgba(255,255,255,0.03); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.05);">
            Importance: ${m.importance_score}/10
          </span>
        </div>
        <p class="memory-text">${m.text}</p>
      </div>
      <div class="memory-meta">
        <div class="meta-item"><i class="fa-solid fa-tag"></i> <span>${m.category}</span></div>
        <div class="meta-item"><i class="fa-solid fa-bullseye"></i> <span>Confidence: ${m.confidence_score}%</span></div>
        <div class="meta-item"><i class="fa-solid fa-clock"></i> <span>${dateStr}</span></div>
        <div class="meta-item"><i class="fa-solid fa-user"></i> <span>User: ${m.user_id}</span></div>
      </div>
    `;
    resultsContainer.appendChild(card);
  });
}

// ─── 7. OPERATIONAL CONTROLS (SLEEP / WAKE) ──────────────────────────────────

async function setSystemPowerState(state) {
  const endpoint = state === 'AWAKE' ? 'wake' : 'sleep';
  try {
    const res = await fetch(`${config.backendUrl}/api/v1/system/${endpoint}`, {
      method: 'POST',
      headers: { 'X-API-Key': config.apiKey }
    });
    if (res.ok) {
      const data = await res.json();
      updateSystemStateUI(data.status);
    }
  } catch (err) {
    console.error('Failed to change system operational state:', err);
  }
}

// ─── 8. REPRESENTATIVE ACTIONS PANEL ─────────────────────────────────────────

async function fetchRepresentativeTasks() {
  const container = document.getElementById('actions-list');
  container.innerHTML = '<div style="color: var(--text-muted);">Fetching agent action logs...</div>';

  try {
    const res = await fetch(`${config.backendUrl}/api/v1/representative/tasks`, {
      headers: { 'X-API-Key': config.apiKey }
    });
    if (res.ok) {
      const tasks = await res.json();
      renderActionTasks(tasks);
    }
  } catch (err) {
    container.innerHTML = '<div style="color: var(--color-red);">Error loading agent logs.</div>';
  }
}

function renderActionTasks(tasks) {
  const container = document.getElementById('actions-list');
  container.innerHTML = '';
  
  if (tasks.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted);">No representative tasks tracked.</div>';
    return;
  }

  tasks.forEach(t => {
    const card = document.createElement('div');
    card.className = 'action-item-card';
    
    let timeStr = new Date(t.created_at).toLocaleString();
    let resultSection = t.result ? `<div class="action-result">${t.result}</div>` : '';
    
    card.innerHTML = `
      <div class="action-card-header">
        <span class="action-desc">${t.task_description}</span>
        <span class="action-status-badge ${t.status}">${t.status}</span>
      </div>
      ${resultSection}
      <div class="action-card-footer">
        <span><i class="fa-solid fa-clock"></i> ${timeStr}</span>
        <span>ID: #${t.id}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

async function triggerRepresentativeTask() {
  const input = document.getElementById('action-input');
  const taskDesc = input.value.trim();
  if (!taskDesc) return;
  
  input.value = '';

  try {
    const res = await fetch(`${config.backendUrl}/api/v1/representative/tasks`, {
      method: 'POST',
      headers: {
        'X-API-Key': config.apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ task_description: taskDesc })
    });
    
    if (res.ok) {
      // Refresh list immediately and start a poll since task is pending
      fetchRepresentativeTasks();
      setTimeout(fetchRepresentativeTasks, 2500); // Poll after 2.5s to get completed status
    }
  } catch (err) {
    console.error('Failed to execute representative task:', err);
  }
}

// ─── 9. CONVERSATION HISTORY LOGS ───────────────────────────────────────────

async function fetchHistoryLogs() {
  const container = document.getElementById('history-list');
  container.innerHTML = '<div style="color: var(--text-muted);">Fetching logs from SQLite...</div>';

  const dateVal = document.getElementById('history-filter-date').value;
  const sessVal = document.getElementById('history-filter-session').value.trim();
  const devVal = document.getElementById('history-filter-device').value.trim();

  let queryUrl = `${config.backendUrl}/api/v1/conversations?`;
  if (dateVal) queryUrl += `date=${encodeURIComponent(dateVal)}&`;
  if (sessVal) queryUrl += `session_id=${encodeURIComponent(sessVal)}&`;
  if (devVal) queryUrl += `device_id=${encodeURIComponent(devVal)}&`;

  try {
    const res = await fetch(queryUrl, {
      headers: { 'X-API-Key': config.apiKey }
    });
    if (res.ok) {
      const logs = await res.json();
      renderHistoryLogs(logs);
    }
  } catch (err) {
    container.innerHTML = '<div style="color: var(--color-red);">Error loading conversation logs.</div>';
  }
}

function renderHistoryLogs(logs) {
  const container = document.getElementById('history-list');
  container.innerHTML = '';
  
  if (logs.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted);">No matching history logs found.</div>';
    return;
  }

  logs.forEach(l => {
    const card = document.createElement('div');
    card.className = 'history-item-card';
    
    let timeStr = new Date(l.timestamp).toLocaleString();
    
    card.innerHTML = `
      <div class="history-meta-row">
        <span><i class="fa-solid fa-circle-info"></i> Session: ${l.session_id} | Device: ${l.device_id}</span>
        <span>${timeStr}</span>
      </div>
      <div class="history-exchange">
        <div class="exchange-row user">
          <strong>User:</strong> ${l.user_message}
        </div>
        <div class="exchange-row frieren">
          <strong>Frieren:</strong> ${l.ai_response}
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

// ─── 10. SETUP EVENTS AND UTILS ──────────────────────────────────────────────

function setupEventListeners() {
  // Settings Modal toggles
  document.getElementById('btn-open-settings').addEventListener('click', () => {
    document.getElementById('settings-modal').classList.add('active');
  });

  document.getElementById('btn-close-settings').addEventListener('click', () => {
    document.getElementById('settings-modal').classList.remove('active');
  });

  // Save Settings Modal form
  document.getElementById('btn-save-settings').addEventListener('click', () => {
    config.backendUrl = document.getElementById('set-backend-url').value.trim();
    config.apiKey = document.getElementById('set-api-key').value.trim();
    config.userId = document.getElementById('set-user-id').value.trim();
    config.deviceId = document.getElementById('set-device-id').value.trim();
    config.sessionId = document.getElementById('set-session-id').value.trim();
    
    saveSettingsToStorage();
    document.getElementById('settings-modal').classList.remove('active');
    
    // Trigger immediate diagnostics update with new endpoint settings
    checkBackendHealth();
    refreshMemoryStats();
  });

  // Rotate Session ID when settings ID is clicked
  document.getElementById('set-session-id').addEventListener('click', () => {
    const newSess = generateUUID();
    document.getElementById('set-session-id').value = newSess;
  });

  // Chat send actions
  document.getElementById('btn-send').addEventListener('click', sendChatMessage);
  document.getElementById('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendChatMessage();
  });

  // Microphone toggle button
  document.getElementById('btn-toggle-mic').addEventListener('click', () => {
    if (isListening) {
      stopSpeechRecognition();
    } else {
      startSpeechRecognition();
    }
  });

  // Speak toggle button in input bar
  document.getElementById('btn-toggle-speak').addEventListener('click', toggleVoiceOutputGlobal);

  // Sleep wake control panel buttons
  document.getElementById('btn-wake-system').addEventListener('click', () => setSystemPowerState('AWAKE'));
  document.getElementById('btn-sleep-system').addEventListener('click', () => setSystemPowerState('SLEEPING'));

  // Voice range settings listeners
  document.getElementById('voice-toggle-enabled').addEventListener('change', (e) => {
    voiceSettings.enabled = e.target.checked;
    localStorage.setItem('frieren_voice_enabled', voiceSettings.enabled);
    updateSpeakerButtonUI();
  });

  document.getElementById('voice-toggle-autospeak').addEventListener('change', (e) => {
    voiceSettings.autoSpeak = e.target.checked;
    localStorage.setItem('frieren_voice_autospeak', voiceSettings.autoSpeak);
  });

  document.getElementById('voice-rate').addEventListener('input', (e) => {
    voiceSettings.rate = parseFloat(e.target.value);
    localStorage.setItem('frieren_voice_rate', voiceSettings.rate);
    updateVoiceLabels();
  });

  document.getElementById('voice-volume').addEventListener('input', (e) => {
    voiceSettings.volume = parseFloat(e.target.value);
    localStorage.setItem('frieren_voice_volume', voiceSettings.volume);
    updateVoiceLabels();
  });

  document.getElementById('voice-pitch').addEventListener('input', (e) => {
    voiceSettings.pitch = parseFloat(e.target.value);
    localStorage.setItem('frieren_voice_pitch', voiceSettings.pitch);
    updateVoiceLabels();
  });

  // Notification Permission Request button
  document.getElementById('btn-notifications').addEventListener('click', () => {
    if ('Notification' in window) {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          alert('Notification service initialized! Frieren will trigger reminders proactively.');
        } else {
          alert('Notifications denied.');
        }
      });
    } else {
      alert('This browser does not support desktop notifications.');
    }
  });

  // Memory search input listeners (with simple 300ms debouncing)
  let searchTimeout = null;
  document.getElementById('memory-search-input').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      fetchMemorySearch(e.target.value.trim());
    }, 300);
  });

  // Memory Filter button group actions
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      // Trigger search refresh with filters applied
      const q = document.getElementById('memory-search-input').value.trim();
      fetchMemorySearch(q);
    });
  });

  // Execute Action button click handler (Representative panel)
  document.getElementById('btn-submit-action').addEventListener('click', triggerRepresentativeTask);
  document.getElementById('action-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') triggerRepresentativeTask();
  });

  // Conversation history filter listeners
  document.getElementById('history-filter-date').addEventListener('change', fetchHistoryLogs);
  document.getElementById('history-filter-session').addEventListener('input', fetchHistoryLogs);
  document.getElementById('history-filter-device').addEventListener('input', fetchHistoryLogs);
  document.getElementById('btn-reset-history-filters').addEventListener('click', () => {
    document.getElementById('history-filter-date').value = '';
    document.getElementById('history-filter-session').value = '';
    document.getElementById('history-filter-device').value = '';
    fetchHistoryLogs();
  });
}

// Register service worker for installable PWA behavior
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./service-worker.js')
        .then(reg => console.log('Service Worker registered successfully!', reg.scope))
        .catch(err => console.error('Service Worker registration failed:', err));
    });
  }
}
