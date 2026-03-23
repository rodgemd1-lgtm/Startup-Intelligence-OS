/**
 * Jake Ops Dashboard — Panel Logic
 * Loads data from Supabase and renders each panel.
 * Auto-refreshes every 30 seconds.
 */

let refreshTimer = null;

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function relativeTime(isoStr) {
  if (!isoStr) return '—';
  const d = new Date(isoStr);
  const now = Date.now();
  const diff = now - d.getTime();
  const mins = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

function shortDate(isoStr) {
  if (!isoStr) return '—';
  return new Date(isoStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function truncate(str, len = 80) {
  if (!str) return '';
  return str.length > len ? str.slice(0, len) + '…' : str;
}

function setBody(panelId, html) {
  const panel = document.getElementById(panelId);
  if (panel) panel.querySelector('.panel-body').innerHTML = html;
}

function setBadge(badgeId, text, type = 'ok') {
  const badge = document.getElementById(badgeId);
  if (badge) {
    badge.textContent = text;
    badge.className = `badge badge-${type}`;
  }
}

// ---------------------------------------------------------------------------
// Panel 1: Task Board
// ---------------------------------------------------------------------------

async function loadTasks() {
  try {
    const tasks = await fetchTasks();
    const cols = {
      pending: [], in_progress: [], blocked: [], done: [],
    };
    tasks.forEach(t => {
      const status = t.status || 'pending';
      const key = status.replace('-', '_');
      if (cols[key]) cols[key].push(t);
      else cols.pending.push(t);
    });

    const total = tasks.length;
    const done = cols.done.length;
    setBadge('tasks-badge', `${done}/${total}`, done === total && total > 0 ? 'ok' : 'warn');

    if (total === 0) {
      setBody('panel-tasks', '<div class="kanban"><div class="empty">No tasks yet. Tasks appear here from jake_tasks table.</div></div>');
      return;
    }

    const colLabels = { pending: 'Pending', in_progress: 'In Progress', blocked: '🚫 Blocked', done: '✓ Done' };
    let html = '<div class="kanban">';
    for (const [key, label] of Object.entries(colLabels)) {
      html += `<div class="kanban-col"><h3>${label} <span style="color:var(--muted)">(${cols[key].length})</span></h3>`;
      if (cols[key].length === 0) {
        html += '<div class="empty" style="font-size:10px">empty</div>';
      } else {
        cols[key].slice(0, 8).forEach(t => {
          const pri = t.priority || 'medium';
          html += `
            <div class="task-card priority-${pri}">
              <div class="task-title">${truncate(t.title, 60)}</div>
              <div class="task-meta">${t.assignee || '—'} · ${relativeTime(t.created_at)}</div>
            </div>`;
        });
      }
      html += '</div>';
    }
    html += '</div>';
    setBody('panel-tasks', html);
  } catch (e) {
    setBadge('tasks-badge', 'err', 'err');
    setBody('panel-tasks', `<div class="error-msg">${e.message}</div>`);
  }
}

// ---------------------------------------------------------------------------
// Panel 2: Brain Stats
// ---------------------------------------------------------------------------

async function loadBrainStats() {
  try {
    const stats = await fetchBrainStats();
    const {
      episodic, semantic, procedural, working,
      entities, relationships, lastConsolidation,
    } = stats;

    const total = (episodic || 0) + (semantic || 0) + (procedural || 0);
    setBadge('brain-badge', `${total} memories`, 'ok');

    setBody('panel-brain', `
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">Episodic</div>
          <div class="stat-value">${episodic}</div>
          <div class="stat-sub">events</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Semantic</div>
          <div class="stat-value">${semantic}</div>
          <div class="stat-sub">facts</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Procedural</div>
          <div class="stat-value">${procedural}</div>
          <div class="stat-sub">patterns</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Working</div>
          <div class="stat-value">${working}</div>
          <div class="stat-sub">active</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Entities</div>
          <div class="stat-value">${entities}</div>
          <div class="stat-sub">people/places</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Relations</div>
          <div class="stat-value">${relationships}</div>
          <div class="stat-sub">graph edges</div>
        </div>
      </div>
      <div class="consolidation-time">
        Last semantic: ${lastConsolidation ? relativeTime(lastConsolidation) : 'never'}
      </div>
    `);
  } catch (e) {
    setBadge('brain-badge', 'err', 'err');
    setBody('panel-brain', `<div class="error-msg">${e.message}</div>`);
  }
}

// ---------------------------------------------------------------------------
// Panel 3: Activity Log
// ---------------------------------------------------------------------------

async function loadActivity() {
  try {
    const events = await fetchActivityLog();
    setBadge('activity-badge', `${events.length} events`, events.length > 0 ? 'ok' : 'warn');

    if (events.length === 0) {
      setBody('panel-activity', '<div class="empty">No activity in last 24h</div>');
      return;
    }

    const html = events.map(e => `
      <div class="activity-item">
        <span class="activity-time">${relativeTime(e.created_at)}</span>
        <span class="activity-type">${truncate(e.data_type || e.source || '?', 20)}</span>
        <span class="activity-content">${truncate(e.content, 90)}</span>
      </div>
    `).join('');
    setBody('panel-activity', html);
  } catch (e) {
    setBadge('activity-badge', 'err', 'err');
    setBody('panel-activity', `<div class="error-msg">${e.message}</div>`);
  }
}

// ---------------------------------------------------------------------------
// Panel 4: Cron Health
// ---------------------------------------------------------------------------

async function loadCronHealth() {
  try {
    const jobs = await fetchCronHealth();
    const errCount = jobs.filter(j => j.status === 'error').length;
    setBadge('cron-badge', errCount > 0 ? `${errCount} errors` : 'all ok', errCount > 0 ? 'err' : 'ok');

    if (jobs.length === 0) {
      setBody('panel-cron', '<div class="empty">No cron data yet. Runs appear after first V10 execution.</div>');
      return;
    }

    // Deduplicate by job_name (keep most recent)
    const seen = new Set();
    const deduped = jobs.filter(j => {
      if (seen.has(j.job_name)) return false;
      seen.add(j.job_name);
      return true;
    });

    const html = deduped.map(j => {
      const statusClass = j.status === 'ok' ? 'cron-ok' : j.status === 'error' ? 'cron-err' : 'cron-unknown';
      return `
        <div class="cron-row">
          <div class="cron-status ${statusClass}"></div>
          <div class="cron-name">${j.job_name}</div>
          <div class="cron-time">${relativeTime(j.last_run)}</div>
        </div>
        ${j.error_message ? `<div style="font-size:10px;color:var(--red);margin:-4px 0 8px 24px">${truncate(j.error_message, 80)}</div>` : ''}
      `;
    }).join('');
    setBody('panel-cron', html);
  } catch (e) {
    setBadge('cron-badge', 'err', 'err');
    setBody('panel-cron', `<div class="error-msg">${e.message}</div>`);
  }
}

// ---------------------------------------------------------------------------
// Panel 5: Goals Tracker
// ---------------------------------------------------------------------------

async function loadGoals() {
  try {
    const goals = await fetchGoals();
    const active = goals.filter(g => g.status !== 'completed' && g.status !== 'cancelled');
    setBadge('goals-badge', `${active.length} active`, active.length > 0 ? 'ok' : 'warn');

    if (goals.length === 0) {
      setBody('panel-goals', '<div class="empty">No goals yet. Add goals to jake_goals table.</div>');
      return;
    }

    const html = goals.slice(0, 8).map(g => {
      const pct = g.target_value > 0
        ? Math.min(100, Math.round((g.current_value || 0) / g.target_value * 100))
        : null;
      const barHtml = pct !== null
        ? `<div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>`
        : '';
      return `
        <div class="goal-item">
          <div class="goal-header">
            <span class="goal-title">${truncate(g.title, 50)}</span>
            ${pct !== null ? `<span class="goal-pct">${pct}%</span>` : ''}
          </div>
          ${barHtml}
          ${g.deadline ? `<div class="goal-deadline">Due: ${shortDate(g.deadline)}</div>` : ''}
        </div>
      `;
    }).join('');
    setBody('panel-goals', html);
  } catch (e) {
    setBadge('goals-badge', 'err', 'err');
    setBody('panel-goals', `<div class="error-msg">${e.message}</div>`);
  }
}

// ---------------------------------------------------------------------------
// Panel 6: Pipeline Runs
// ---------------------------------------------------------------------------

async function loadPipelineRuns() {
  try {
    const runs = await fetchPipelineRuns();
    const active = runs.filter(r => r.status === 'running').length;
    setBadge('pipeline-badge', active > 0 ? `${active} running` : `${runs.length} runs`,
      active > 0 ? 'warn' : runs.length > 0 ? 'ok' : 'warn');

    if (runs.length === 0) {
      setBody('panel-pipeline', '<div class="empty">No pipeline runs yet. Runs appear after Phase 4 build.</div>');
      return;
    }

    const html = runs.map(r => {
      const statusCls = `pipeline-status-${r.status || 'unknown'}`;
      return `
        <div class="pipeline-row">
          <div class="pipeline-name">${truncate(r.pipeline_name, 40)}</div>
          <div class="pipeline-meta">
            <span class="${statusCls}">${r.status || '?'}</span>
            <span class="pipeline-phase">phase ${r.current_phase || '?'}</span>
            <span>${relativeTime(r.started_at)}</span>
          </div>
          ${r.error_log ? `<div style="font-size:10px;color:var(--red);margin-top:3px">${truncate(r.error_log, 80)}</div>` : ''}
        </div>
      `;
    }).join('');
    setBody('panel-pipeline', html);
  } catch (e) {
    setBadge('pipeline-badge', '—', 'warn');
    setBody('panel-pipeline', '<div class="empty">Phase 4 not built yet.</div>');
  }
}

// ---------------------------------------------------------------------------
// Main: refresh all panels
// ---------------------------------------------------------------------------

async function refreshAll() {
  document.getElementById('last-refresh').textContent = 'Refreshing...';

  await Promise.allSettled([
    loadTasks(),
    loadBrainStats(),
    loadActivity(),
    loadCronHealth(),
    loadGoals(),
    loadPipelineRuns(),
  ]);

  const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  document.getElementById('last-refresh').textContent = `Last refresh: ${now}`;
}

// Auto-refresh every 30 seconds
function startAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refreshAll, 30000);
}

// Initial load
refreshAll().then(() => startAutoRefresh());
