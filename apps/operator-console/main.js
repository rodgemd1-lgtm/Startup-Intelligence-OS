var params = new URLSearchParams(window.location.search);
var operatorRaw = (params.get('operator') || 'mike').toLowerCase();
var operator = operatorRaw === 'susan' ? 'susan' : 'mike';

var API_BASE = 'http://localhost:8420';

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
