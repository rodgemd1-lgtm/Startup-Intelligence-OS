/**
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
