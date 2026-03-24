/**
<<<<<<< HEAD
 * Supabase client for Jake Ops Dashboard.
 * LOCAL TOOL ONLY — service key is acceptable for localhost use.
 * Never expose this file publicly.
 */

const SUPABASE_URL = 'https://zqsdadnnpgqhehqxplio.supabase.co';
// Service key — read-only queries only in this dashboard
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpxc2RhZG5ucGdxaGVocXhwbGlvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjgyNTUyNSwiZXhwIjoyMDg4NDAxNTI1fQ.9l4vu1zz-pW6GlhPhk8sRTcWGUvQcN3LGXy1jnKDAzk';

/** Generic Supabase REST query helper */
async function sbQuery(table, params = '') {
  const url = `${SUPABASE_URL}/rest/v1/${table}${params ? '?' + params : ''}`;
  const res = await fetch(url, {
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
    },
  });
  if (!res.ok) throw new Error(`${table}: ${res.status} ${res.statusText}`);
  return res.json();
}

/** Generic Supabase REST insert helper */
async function sbInsert(table, row) {
  const url = `${SUPABASE_URL}/rest/v1/${table}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
    },
    body: JSON.stringify(row),
  });
  if (!res.ok) throw new Error(`${table} insert: ${res.status} ${res.statusText}`);
  return res.json();
}

/** Generic Supabase REST update helper */
async function sbUpdate(table, id, updates) {
  const url = `${SUPABASE_URL}/rest/v1/${table}?id=eq.${id}`;
  const res = await fetch(url, {
    method: 'PATCH',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
    },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error(`${table} update: ${res.status} ${res.statusText}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Panel data fetchers
// ---------------------------------------------------------------------------

/** Panel 1: Task Board */
async function fetchTasks() {
  return sbQuery('jake_tasks', 'select=id,title,status,priority,assignee,created_at&order=created_at.desc&limit=50');
}

/** Panel 2: Brain Stats */
async function fetchBrainStats() {
  const [episodic, semantic, procedural, working, entities, relationships] = await Promise.allSettled([
    sbQuery('jake_episodic', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_episodic', 'select=count')),
    sbQuery('jake_semantic', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_semantic', 'select=count')),
    sbQuery('jake_procedural', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_procedural', 'select=count')),
    sbQuery('jake_working', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_working', 'select=count')),
    sbQuery('jake_entities', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_entities', 'select=count')),
    sbQuery('jake_relationships', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_relationships', 'select=count')),
  ]);
  // Get actual counts via select=*&limit with count headers
  const [epiCount, semCount, proCount, wrkCount, entCount, relCount] = await Promise.all([
    getCount('jake_episodic'),
    getCount('jake_semantic'),
    getCount('jake_procedural'),
    getCount('jake_working'),
    getCount('jake_entities'),
    getCount('jake_relationships'),
  ]);
  // Get last consolidation — most recent semantic created_at
  const lastSemantic = await sbQuery('jake_semantic', 'select=created_at&order=created_at.desc&limit=1').catch(() => []);
  return {
    episodic: epiCount,
    semantic: semCount,
    procedural: proCount,
    working: wrkCount,
    entities: entCount,
    relationships: relCount,
    lastConsolidation: lastSemantic[0]?.created_at || null,
  };
}

async function getCount(table) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?select=id`, {
    method: 'HEAD',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Prefer': 'count=exact',
    },
  });
  const countHeader = res.headers.get('content-range');
  if (countHeader) {
    const match = countHeader.match(/\/(\d+)/);
    if (match) return parseInt(match[1], 10);
  }
  return '?';
}

/** Panel 3: Agent Activity Log */
async function fetchActivityLog() {
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  return sbQuery('jake_episodic',
    `select=id,content,source,data_type,created_at&order=created_at.desc&limit=30&created_at=gte.${since}`
  ).catch(() =>
    sbQuery('jake_episodic', 'select=id,content,source,data_type,created_at&order=created_at.desc&limit=30')
  );
}

/** Panel 4: Cron Health */
async function fetchCronHealth() {
  // Try jake_cron_status table first (may not exist yet)
  try {
    return await sbQuery('jake_cron_status',
      'select=job_name,last_run,status,next_run,error_message&order=last_run.desc&limit=20'
    );
  } catch (e) {
    // Fall back to episodic entries with data_type matching cron runs
    const rows = await sbQuery('jake_episodic',
      `select=source,data_type,created_at,metadata&data_type=in.(self_improvement_run,research_daemon_run,collective_run,cron_run)&order=created_at.desc&limit=10`
    ).catch(() => []);
    return rows.map(r => ({
      job_name: r.source || r.data_type,
      last_run: r.created_at,
      status: r.metadata?.success ? 'ok' : 'error',
      next_run: null,
      error_message: r.metadata?.error || null,
    }));
  }
}

/** Panel 5: Goals Tracker */
async function fetchGoals() {
  return sbQuery('jake_goals',
    'select=id,title,status,target_value,current_value,deadline,priority&order=priority.asc,created_at.desc&limit=20'
  ).catch(() => []);
}

/** Panel 6 (Phase 4): Pipeline Runs */
async function fetchPipelineRuns() {
  try {
    return await sbQuery('jake_pipeline_runs',
      'select=id,pipeline_name,started_at,current_phase,status,completed_at,error_log&order=started_at.desc&limit=10'
    );
  } catch (e) {
    return [];
  }
}
=======
 * Supabase client for the Operator Console.
 * Handles pipeline runs, cron health, and brain stats panels.
 *
 * Uses anon key (read-only queries). Set SUPABASE_URL and SUPABASE_ANON_KEY
 * as globals before this script, or they fall back to the known constants.
 */

var SUPABASE_URL = window.SUPABASE_URL || 'https://zqsdadnnpgqhehqxplio.supabase.co';
var SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY || '';  // set in env or config

// Status → color
var STATUS_COLORS = {
  completed: '#22c55e',
  success:   '#22c55e',
  running:   '#3b82f6',
  pending:   '#6b7280',
  failed:    '#ef4444',
  blocked:   '#f97316',
  skipped:   '#6b7280',
};

function statusDot(status) {
  var color = STATUS_COLORS[status] || '#6b7280';
  return '<span style="color:' + color + ';font-size:10px;">● </span>';
}

function timeAgo(isoStr) {
  if (!isoStr) return '—';
  var diff = Math.floor((Date.now() - new Date(isoStr)) / 1000);
  if (diff < 60) return diff + 's ago';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  return Math.floor(diff / 86400) + 'd ago';
}

/**
 * Minimal Supabase REST fetch (no SDK dependency).
 */
function sbFetch(table, params) {
  if (!SUPABASE_ANON_KEY) {
    return Promise.reject(new Error('SUPABASE_ANON_KEY not set'));
  }
  var url = SUPABASE_URL + '/rest/v1/' + table + '?' + (params || '');
  return fetch(url, {
    headers: {
      'apikey': SUPABASE_ANON_KEY,
      'Authorization': 'Bearer ' + SUPABASE_ANON_KEY,
      'Accept': 'application/json',
    },
  }).then(function(r) {
    if (!r.ok) throw new Error('Supabase error ' + r.status);
    return r.json();
  });
}

// ------------------------------------------------------------------
// Pipeline Runs Panel
// ------------------------------------------------------------------

function loadPipelineRuns() {
  var panel = document.getElementById('pipeline-runs-panel');
  if (!panel) return;

  sbFetch('jake_pipeline_runs', 'select=id,pipeline_name,task_type,status,current_phase,started_at,completed_at&order=started_at.desc&limit=8')
    .then(function(runs) {
      if (!runs || !runs.length) {
        panel.innerHTML = '<p class="pipeline-empty">No pipeline runs yet.</p>';
        return;
      }
      var html = '<table class="pipeline-table"><thead><tr><th>Pipeline</th><th>Type</th><th>Phase</th><th>Status</th><th>Started</th></tr></thead><tbody>';
      runs.forEach(function(r) {
        html += '<tr>';
        html += '<td class="mono" title="' + (r.id || '') + '">' + (r.pipeline_name || '—').slice(0, 20) + '</td>';
        html += '<td>' + (r.task_type || '—') + '</td>';
        html += '<td class="mono">' + (r.current_phase || '—') + '</td>';
        html += '<td>' + statusDot(r.status) + (r.status || '—') + '</td>';
        html += '<td class="dim">' + timeAgo(r.started_at) + '</td>';
        html += '</tr>';
      });
      html += '</tbody></table>';
      panel.innerHTML = html;
    })
    .catch(function(e) {
      panel.innerHTML = '<p class="pipeline-error">Pipeline data unavailable: ' + e.message + '</p>';
    });
}

// ------------------------------------------------------------------
// Cron Health Panel
// ------------------------------------------------------------------

function loadCronHealth() {
  var panel = document.getElementById('cron-health-panel');
  if (!panel) return;

  sbFetch('jake_cron_status', 'select=job_name,status,last_run_at,next_run_at,actions_taken,error_message&order=job_name.asc')
    .then(function(jobs) {
      if (!jobs || !jobs.length) {
        panel.innerHTML = '<p class="pipeline-empty">No cron jobs found.</p>';
        return;
      }
      var html = '<ul class="cron-list">';
      jobs.forEach(function(j) {
        html += '<li>';
        html += statusDot(j.status);
        html += '<span class="mono">' + j.job_name + '</span>';
        html += '<span class="dim"> · ' + timeAgo(j.last_run_at) + '</span>';
        if (j.error_message) {
          html += '<br><span class="cron-error">' + j.error_message.slice(0, 60) + '</span>';
        }
        html += '</li>';
      });
      html += '</ul>';
      panel.innerHTML = html;
    })
    .catch(function(e) {
      panel.innerHTML = '<p class="pipeline-error">Cron data unavailable: ' + e.message + '</p>';
    });
}

// ------------------------------------------------------------------
// Init + auto-refresh
// ------------------------------------------------------------------

function refreshPipelinePanels() {
  loadPipelineRuns();
  loadCronHealth();
}

// Wire refresh button
document.addEventListener('DOMContentLoaded', function() {
  var btn = document.getElementById('pipeline-refresh');
  if (btn) btn.addEventListener('click', refreshPipelinePanels);

  // Initial load
  refreshPipelinePanels();

  // Auto-refresh every 30 seconds
  setInterval(refreshPipelinePanels, 30000);
});

// Inject styles for pipeline panels
(function() {
  var style = document.createElement('style');
  style.textContent = [
    '.btn-tiny{background:none;border:none;color:#6b7280;cursor:pointer;font-size:12px;padding:0 4px;}',
    '.btn-tiny:hover{color:#e5e7eb;}',
    '.pipeline-loading{color:#6b7280;font-size:11px;padding:4px 0;}',
    '.pipeline-empty{color:#6b7280;font-size:11px;padding:4px 0;}',
    '.pipeline-error{color:#ef4444;font-size:11px;padding:4px 0;}',
    '.pipeline-table{width:100%;border-collapse:collapse;font-size:11px;}',
    '.pipeline-table th{color:#6b7280;text-align:left;padding:2px 4px;border-bottom:1px solid #374151;}',
    '.pipeline-table td{padding:3px 4px;border-bottom:1px solid #1f2937;vertical-align:top;}',
    '.cron-list{list-style:none;padding:0;margin:0;font-size:11px;}',
    '.cron-list li{padding:3px 0;border-bottom:1px solid #1f2937;}',
    '.cron-error{color:#ef4444;font-size:10px;}',
    '.mono{font-family:monospace;}',
    '.dim{color:#6b7280;}',
  ].join('\n');
  document.head.appendChild(style);
})();
>>>>>>> claude/nifty-ptolemy
