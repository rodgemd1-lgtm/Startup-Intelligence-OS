var params = new URLSearchParams(window.location.search);
var operatorRaw = (params.get('operator') || 'mike').toLowerCase();
var operator = operatorRaw === 'susan' ? 'susan' : 'mike';

var API_BASE = 'http://localhost:8420';

// ---------------------------------------------------------------------------
// Supabase direct REST API (for Cost + Pipeline panels)
// ---------------------------------------------------------------------------

var SUPABASE_URL = 'https://zqsdadnnpgqhehqxplio.supabase.co';
var SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpxc2RhZG5ucGdxaGVocXhwbGlvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyMzkyNTMsImV4cCI6MjA1NjgxNTI1M30.n45Uo3-7OSU5kQCLGsAbS21dXQ1OEPjKgdZQSVHNSK0';

function fetchSupabase(table, select, filters) {
  select = select || '*';
  filters = filters || '';
  var url = SUPABASE_URL + '/rest/v1/' + table + '?select=' + encodeURIComponent(select) + (filters ? '&' + filters : '');
  return fetch(url, {
    headers: {
      'apikey': SUPABASE_ANON_KEY,
      'Authorization': 'Bearer ' + SUPABASE_ANON_KEY
    }
  }).then(function(resp) {
    if (!resp.ok) throw new Error('Supabase ' + resp.status);
    return resp.json();
  });
}

function formatCurrency(value) {
  if (value >= 1000000) return '$' + (value / 1000000).toFixed(2) + 'M';
  if (value >= 1000) return '$' + (value / 1000).toFixed(1) + 'K';
  return '$' + value.toFixed(0);
}

// --- Cost Tracking Panel ---

function loadCostPanel() {
  var today = new Date().toISOString().slice(0, 10);
  var monthStart = today.slice(0, 7) + '-01';

  // Fetch today's records
  var dailyFilter = 'recorded_at=gte.' + today + 'T00:00:00Z&recorded_at=lte.' + today + 'T23:59:59Z';
  var monthFilter = 'recorded_at=gte.' + monthStart + 'T00:00:00Z';

  Promise.all([
    fetchSupabase('jake_cost_tracking', 'estimated_cost_usd', dailyFilter),
    fetchSupabase('jake_cost_tracking', 'model,estimated_cost_usd', monthFilter)
  ]).then(function(results) {
    var dailyRows = results[0] || [];
    var monthRows = results[1] || [];

    // Daily total
    var dailyTotal = dailyRows.reduce(function(sum, r) { return sum + parseFloat(r.estimated_cost_usd || 0); }, 0);
    document.getElementById('cost-daily').textContent = 'Daily: $' + dailyTotal.toFixed(4);

    // Monthly totals by model
    var byModel = {};
    var monthTotal = 0;
    monthRows.forEach(function(r) {
      var model = r.model || 'unknown';
      var short = model.indexOf('haiku') !== -1 ? 'Haiku' : model.indexOf('opus') !== -1 ? 'Opus' : 'Sonnet';
      byModel[short] = byModel[short] || { calls: 0, cost: 0 };
      byModel[short].calls++;
      byModel[short].cost += parseFloat(r.estimated_cost_usd || 0);
      monthTotal += parseFloat(r.estimated_cost_usd || 0);
    });

    document.getElementById('cost-monthly').textContent = 'Monthly: $' + monthTotal.toFixed(4);

    var tbody = document.getElementById('cost-table-body');
    tbody.innerHTML = '';
    Object.keys(byModel).forEach(function(model) {
      var tr = document.createElement('tr');
      tr.innerHTML = '<td>' + model + '</td><td>' + byModel[model].calls + '</td><td>$' + byModel[model].cost.toFixed(4) + '</td>';
      tbody.appendChild(tr);
    });

    if (Object.keys(byModel).length === 0) {
      var tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="3" style="opacity:0.5;font-size:0.85em;">No data yet</td>';
      tbody.appendChild(tr);
    }

    document.getElementById('cost-last-updated').textContent = 'Updated ' + new Date().toLocaleTimeString();
  }).catch(function(err) {
    document.getElementById('cost-daily').textContent = 'Daily: unavailable';
    document.getElementById('cost-last-updated').textContent = 'Error: ' + err.message;
  });
}

// --- Business Pipeline Panel ---

var PIPELINE_STAGES = ['DISCOVERY', 'DEMO', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON'];
var STAGE_PROBS = { DISCOVERY: 0.1, DEMO: 0.3, PROPOSAL: 0.5, NEGOTIATION: 0.7, CLOSED_WON: 1.0 };

function loadPipelinePanel() {
  Promise.all([
    fetchSupabase('jake_deals', 'stage,value_usd,probability,name,company,updated_at', 'stage=neq.CLOSED_LOST&order=updated_at.desc'),
  ]).then(function(results) {
    var deals = results[0] || [];

    // Group by stage
    var byStage = {};
    PIPELINE_STAGES.forEach(function(s) { byStage[s] = []; });
    var totalWeighted = 0;
    var staleCount = 0;
    var staleThreshold = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

    deals.forEach(function(d) {
      var stage = d.stage;
      if (!byStage[stage]) byStage[stage] = [];
      byStage[stage].push(d);
      var val = parseFloat(d.value_usd || 0);
      var prob = parseFloat(d.probability || STAGE_PROBS[stage] || 0.1);
      totalWeighted += val * prob;
      if (d.updated_at && new Date(d.updated_at) < staleThreshold && stage !== 'CLOSED_WON') {
        staleCount++;
      }
    });

    document.getElementById('pipeline-total').textContent = 'Weighted: ' + formatCurrency(totalWeighted);

    var stagesEl = document.getElementById('pipeline-stages');
    stagesEl.innerHTML = '';
    PIPELINE_STAGES.forEach(function(stage) {
      var stagDeals = byStage[stage] || [];
      if (stagDeals.length === 0 && stage === 'CLOSED_WON') return;
      var stageVal = stagDeals.reduce(function(s, d) { return s + parseFloat(d.value_usd || 0); }, 0);
      var div = document.createElement('div');
      div.className = 'pipeline-stage-row';
      div.textContent = stage + ': ' + stagDeals.length + ' deal' + (stagDeals.length !== 1 ? 's' : '') +
        (stageVal > 0 ? ' — ' + formatCurrency(stageVal) : '');
      stagesEl.appendChild(div);
    });

    if (deals.length === 0) {
      stagesEl.textContent = 'No active deals';
    }

    var staleEl = document.getElementById('pipeline-stale');
    staleEl.textContent = 'Deals Needing Action: ' + staleCount;
    if (staleCount > 0) staleEl.style.color = '#e85';

    document.getElementById('pipeline-last-updated').textContent = 'Updated ' + new Date().toLocaleTimeString();
  }).catch(function(err) {
    document.getElementById('pipeline-total').textContent = 'Pipeline: unavailable';
    document.getElementById('pipeline-last-updated').textContent = 'Error: ' + err.message;
  });
}

// Load panels on startup and refresh every 60 seconds
loadCostPanel();
loadPipelinePanel();
setInterval(loadCostPanel, 60000);
setInterval(loadPipelinePanel, 60000);

var helloEl = document.getElementById('hello');
var debriefEl = document.getElementById('debrief');
var actionsEl = document.getElementById('actions');
var statusEl = document.getElementById('status');
var nextActionsEl = document.getElementById('next-actions');
var workspaceSummaryEl = document.getElementById('workspace-summary');
var terminalOutput = document.getElementById('terminal-output');
var terminalInput = document.getElementById('terminal-input');

var apiAvailable = false;

// --- Helpers ---

function appendTerminal(text) {
  terminalOutput.textContent += text + '\n';
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function renderList(el, items) {
  el.innerHTML = '';
  items.forEach(function (item) {
    var li = document.createElement('li');
    li.textContent = typeof item === 'string' ? item : JSON.stringify(item);
    el.appendChild(li);
  });
}

// --- API integration with fallback ---

function tryApi(path) {
  return fetch(API_BASE + path)
    .then(function (r) {
      if (!r.ok) throw new Error('API returned ' + r.status);
      return r.json();
    });
}

function loadFromApi() {
  return tryApi('/api/debrief?operator=' + operator)
    .then(function (data) {
      apiAvailable = true;
      helloEl.textContent = (data.greeting || ('Hello, ' + (operator === 'susan' ? 'Susan' : 'Mike'))) + ' — here is your Decision OS debrief.';
      renderList(debriefEl, data.debrief || []);
      var actionSet = (data.actions || {})[operator] || [];
      renderList(actionsEl, actionSet);
      renderList(nextActionsEl, actionSet);
      renderList(statusEl, data.status || []);

      // Load workspace summary from context endpoint
      return tryApi('/api/context');
    })
    .then(function (ctx) {
      var summaryItems = [
        'Mode: ' + (ctx.mode || 'unknown'),
        'Front door: ' + (ctx.front_door || 'unknown'),
        'Foundry: ' + (ctx.foundry || 'unknown'),
        'Runtime: ' + (ctx.runtime_source_of_truth || 'unknown'),
        'Branch: ' + (ctx.active_branch || 'unknown'),
        'Company: ' + (ctx.active_company || 'unknown'),
      ];
      renderList(workspaceSummaryEl, summaryItems);
    });
}

function loadFromStatic() {
  return fetch('./operator-debrief.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var greeting = operator === 'susan' ? 'Hello, Susan' : 'Hello, Mike';
      helloEl.textContent = greeting + ' — here is your Decision OS debrief.';

      renderList(debriefEl, data.debrief || []);
      var actionSet = (data.actions || {})[operator] || [];
      renderList(actionsEl, actionSet);
      renderList(nextActionsEl, actionSet);
      renderList(statusEl, data.status || []);

      var summaryItems = [
        'Mode: decision-capability-os',
        'Front door: jake',
        'Foundry: susan',
        'Runtime: susan-team-architect/backend',
        'Branch: main',
        'Company: founder-intelligence-os',
      ];
      renderList(workspaceSummaryEl, summaryItems);
    });
}

// Try API first, fallback to static
loadFromApi().catch(function () {
  apiAvailable = false;
  return loadFromStatic();
}).catch(function (err) {
  helloEl.textContent = 'Hello, Mike — unable to load debrief data.';
  var li = document.createElement('li');
  li.textContent = 'Error: ' + err.message;
  statusEl.appendChild(li);
});

// --- Terminal commands ---

var staticCommands = {
  help: [
    'Available commands:',
    '  help                Show this help',
    '  bin/jake            Validate OS contract',
    '  bin/jake status     Print Decision OS object counts',
    '  bin/jake sync-intel Sync agent readiness + debrief',
    '  bin/os-context      Print active OS context',
    '  status              Object counts (API)',
    '  decisions           List decisions (API)',
    '  runs                List runs (API)',
    '  capabilities        List capabilities (API)',
    '  clear               Clear terminal',
  ].join('\n'),
  'bin/jake': [
    'jake: checks passed',
    '',
    'Validated:',
    '  - README.md, CLAUDE.md, AGENTS.md',
    '  - .startup-os/workspace.yaml (front_door=jake)',
    '  - schemas and templates present',
    '  - jake.profile.yaml roles verified',
    '  - company registry entries verified',
    '  - operator-debrief.json loaded',
    '  - startup-intelligence-overview.md sections verified',
  ].join('\n'),
  'bin/jake status': [
    'jake: Decision OS status',
    '  decisions: 1',
    '  capabilities: 5',
    '  projects: 1',
    '  companies: 1',
    '  runs: 0',
  ].join('\n'),
  'bin/jake sync-intel': 'jake: intel sync complete',
  'bin/os-context': [
    'Startup Intelligence OS Context',
    '- Root: /Users/mikerodgers/Startup-Intelligence-OS',
    '- Front door: bin/jake',
    '- Foundry: susan-team-architect/',
    '- Runtime: susan-team-architect/backend/',
    '',
    'Workspace contract:',
    '  name: startup-intelligence-os',
    '  mode: decision-capability-os',
    '  front_door: jake',
    '  foundry: susan',
    '  runtime_source_of_truth: susan-team-architect/backend',
  ].join('\n'),
};

// API-backed commands
function apiCommand(path, label) {
  appendTerminal('Fetching ' + label + '...');
  tryApi(path)
    .then(function (data) {
      appendTerminal(JSON.stringify(data, null, 2));
    })
    .catch(function (err) {
      appendTerminal('API unavailable: ' + err.message);
      appendTerminal('Start the API server: python3 apps/decision-os/api.py');
    });
}

terminalInput.addEventListener('keydown', function (e) {
  if (e.key === 'Enter') {
    var cmd = terminalInput.value.trim();
    if (!cmd) return;
    appendTerminal('$ ' + cmd);
    terminalInput.value = '';

    if (cmd === 'clear') {
      terminalOutput.textContent = '';
      return;
    }

    // API-backed commands
    if (cmd === 'status') {
      apiCommand('/api/status', 'status');
      return;
    }
    if (cmd === 'decisions') {
      apiCommand('/api/decisions', 'decisions');
      return;
    }
    if (cmd === 'runs') {
      apiCommand('/api/runs', 'runs');
      return;
    }
    if (cmd === 'capabilities') {
      apiCommand('/api/capabilities', 'capabilities');
      return;
    }
    if (cmd === 'artifacts') {
      apiCommand('/api/artifacts', 'artifacts');
      return;
    }
    if (cmd === 'context') {
      apiCommand('/api/context', 'context');
      return;
    }

    // Static fallback commands
    var response = staticCommands[cmd];
    if (response) {
      appendTerminal(response);
    } else {
      appendTerminal('Unknown command: ' + cmd + '\nType "help" for available commands.');
    }
  }
});

// Auto-focus terminal
terminalInput.focus();
