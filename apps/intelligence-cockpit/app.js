const state = {
  tenantId: "transformfit",
};

async function api(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function severityBadge(severity) {
  return `<span class="severity ${severity}">${severity}</span>`;
}

function chipRow(items = []) {
  if (!items.length) {
    return `<p class="muted">None</p>`;
  }
  return `<div class="chip-row">${items.map((item) => `<span class="chip">${item}</span>`).join("")}</div>`;
}

function renderTenants(tenants) {
  const target = document.querySelector("#tenant-list");
  target.innerHTML = tenants
    .map(
      (tenant) => `
        <button class="tenant-card ${tenant.id === state.tenantId ? "active" : ""}" data-tenant-id="${tenant.id}">
          <p class="eyebrow">${tenant.domain}</p>
          <strong>${tenant.name}</strong>
          <p>${tenant.stage}</p>
          <div class="chip-row">
            <span class="chip">Health ${tenant.health_score}</span>
            <span class="chip">$${tenant.budget_per_month_usd ?? "n/a"}/mo</span>
          </div>
        </button>
      `
    )
    .join("");

  for (const button of target.querySelectorAll("[data-tenant-id]")) {
    button.addEventListener("click", async () => {
      state.tenantId = button.dataset.tenantId;
      await loadWorkspace();
    });
  }
}

function renderScorecard(scorecard) {
  document.querySelector("#workspace-title").textContent = scorecard.tenant.name;
  document.querySelector("#workspace-health").textContent = scorecard.tenant.health_score;
  document.querySelector("#diagnosis-copy").textContent = scorecard.diagnosis;

  document.querySelector("#recommended-actions").innerHTML = scorecard.recommended_actions
    .map((action) => `<div class="action-card"><strong>Next move</strong><p>${action}</p></div>`)
    .join("");

  document.querySelector("#metric-grid").innerHTML = scorecard.metrics
    .map(
      (metric) => `
        <div class="metric-card">
          <p class="eyebrow">${metric.label}</p>
          <strong>${metric.value}</strong>
          ${metric.trend ? `<p class="muted">${metric.trend}</p>` : ""}
        </div>
      `
    )
    .join("");

  document.querySelector("#layer-coverage").innerHTML = scorecard.layer_coverage
    .map(
      (layer) => `
        <div class="layer-card">
          <p class="eyebrow">${layer.name}</p>
          <strong>${layer.coverage_score}</strong>
          <p>${layer.description}</p>
          <p class="muted">${layer.asset_count} assets</p>
          ${chipRow(layer.notes)}
        </div>
      `
    )
    .join("");

  document.querySelector("#protocol-list").innerHTML = scorecard.protocols
    .map(
      (protocol) => `
        <div class="protocol-card">
          <strong>${protocol.name}</strong>
          <p>${protocol.summary}</p>
          ${chipRow([protocol.family, protocol.freshness_status])}
        </div>
      `
    )
    .join("");

  document.querySelector("#company-gaps").innerHTML = scorecard.coverage_gaps
    .slice(0, 6)
    .map(
      (gap) => `
        <div class="issue-card">
          <div class="panel-heading">
            <strong>${gap.title}</strong>
            ${severityBadge(gap.severity)}
          </div>
          <p>${gap.detail}</p>
          ${chipRow([gap.gap_type, gap.layer ?? "unassigned", gap.owner ?? "unowned"])}
        </div>
      `
    )
    .join("");

  document.querySelector("#backlog-preview").innerHTML = scorecard.backlog
    .slice(0, 5)
    .map(
      (item) => `
        <div class="issue-card">
          <div class="panel-heading">
            <strong>${item.title}</strong>
            <span class="chip">Score ${item.score}</span>
          </div>
          <p>${item.reason}</p>
        </div>
      `
    )
    .join("");
}

function renderSearch(searchResponse) {
  document.querySelector("#search-lanes").innerHTML = searchResponse.lanes
    .map(
      (lane) => `
        <div class="lane-card">
          <strong>${lane.lane}</strong>
          <p>${lane.detail}</p>
          <p class="muted">${lane.result_count} results</p>
        </div>
      `
    )
    .join("");

  document.querySelector("#search-results").innerHTML = searchResponse.results
    .map(
      (asset) => `
        <div class="result-card">
          <div class="panel-heading">
            <strong>${asset.title}</strong>
            <span class="chip">${asset.lane}</span>
          </div>
          <p>${asset.excerpt}</p>
          ${chipRow([
            asset.asset_type,
            asset.freshness_status,
            asset.source_path ?? asset.source ?? "repo",
            `confidence ${asset.confidence}`,
          ])}
        </div>
      `
    )
    .join("");
}

function renderPromptBundles(bundles) {
  document.querySelector("#prompt-table").innerHTML = bundles
    .slice(0, 12)
    .map(
      (bundle) => `
        <div class="table-row">
          <div>
            <strong>${bundle.name}</strong>
            <p class="muted">${bundle.id}</p>
          </div>
          <div>
            ${severityBadge(bundle.status === "ready" ? "info" : "high")}
            <p class="muted">v${bundle.version}</p>
          </div>
          <div>
            <p>${bundle.eval.failures.join(" ") || "Promotion-ready."}</p>
          </div>
        </div>
      `
    )
    .join("");
}

function renderAgentProfiles(profiles) {
  document.querySelector("#agent-profiles").innerHTML = profiles
    .slice(0, 8)
    .map(
      (profile) => `
        <div class="issue-card">
          <div class="panel-heading">
            <strong>${profile.name}</strong>
            <span class="chip">Humanization ${profile.humanization_score}</span>
          </div>
          <p>${profile.role}</p>
          ${chipRow([
            profile.group,
            profile.registered ? "registered" : "unregistered",
            ...profile.traits,
          ])}
          <p class="muted">${profile.conversation_style ?? "No conversation style captured yet."}</p>
          <p class="muted">${profile.debate_protocol ?? "Debate protocol missing."}</p>
          ${profile.meeting_habits.length ? `<p class="muted">Habits: ${profile.meeting_habits.join(" • ")}</p>` : ""}
          ${profile.missing_data_types.length ? chipRow(profile.missing_data_types.map((item) => `missing ${item}`)) : ""}
        </div>
      `
    )
    .join("");
}

function renderResearch(snapshot) {
  document.querySelector("#research-summary").innerHTML = `
    <div class="metric-grid">
      <div class="metric-card">
        <p class="eyebrow">Search Hits</p>
        <strong>${snapshot.total_hits}</strong>
      </div>
      <div class="metric-card">
        <p class="eyebrow">Unique URLs</p>
        <strong>${snapshot.unique_urls}</strong>
      </div>
      <div class="metric-card">
        <p class="eyebrow">Scraped Pages</p>
        <strong>${snapshot.total_scrapes}</strong>
      </div>
      <div class="metric-card">
        <p class="eyebrow">Last Harvest</p>
        <strong>${snapshot.generated_at ? new Date(snapshot.generated_at).toLocaleDateString() : "Not run"}</strong>
      </div>
    </div>
    <div class="chip-row">
      ${snapshot.providers.map((provider) => `<span class="chip">${provider.provider}: ${provider.status}</span>`).join("")}
    </div>
  `;

  document.querySelector("#research-topics").innerHTML = snapshot.topics
    .map(
      (topic) => `
        <div class="issue-card">
          <div class="panel-heading">
            <strong>${topic.topic}</strong>
            <span class="chip">${topic.status}</span>
          </div>
          <p>${topic.why}</p>
          ${chipRow([`${topic.hits} hits`, `${topic.scraped_pages} scrapes`, ...topic.example_urls.slice(0, 2)])}
        </div>
      `
    )
    .join("");
}

function renderMcp(servers, tools) {
  document.querySelector("#mcp-servers").innerHTML = servers
    .map(
      (server) => `
        <div class="table-row">
          <div>
            <strong>${server.name}</strong>
            <p class="muted">${server.transport}</p>
          </div>
          <div>
            <span class="chip">${server.status}</span>
            <p class="muted">${server.health}</p>
          </div>
          <div>
            <p>${server.tools_count} tools</p>
            <p class="muted">${server.dependent_workflows.join(", ") || "none"}</p>
          </div>
        </div>
      `
    )
    .join("");

  document.querySelector("#mcp-tools").innerHTML = tools.length
    ? tools
        .map(
          (tool) => `
            <div class="table-row">
              <div>
                <strong>${tool.name}</strong>
                <p class="muted">${tool.server_id}</p>
              </div>
              <div>
                <span class="chip">${tool.status}</span>
              </div>
              <div>
                <p>${tool.description}</p>
              </div>
            </div>
          `
        )
        .join("")
    : `<div class="table-row"><div><strong>No MCP tools detected</strong><p class="muted">The server parser did not find tool definitions.</p></div><div></div><div></div></div>`;
}

function renderRoutingPolicies(policies) {
  document.querySelector("#routing-policies").innerHTML = policies
    .map(
      (policy) => `
        <div class="routing-card">
          <div class="panel-heading">
            <strong>${policy.name}</strong>
            <span class="chip">${policy.mode}</span>
          </div>
          <p>${policy.description}</p>
          ${chipRow([
            `default ${policy.default_route}`,
            policy.provenance_required ? "provenance required" : "provenance optional",
            ...policy.allowed_workloads,
          ])}
        </div>
      `
    )
    .join("");
}

function renderRunTraces(traces) {
  document.querySelector("#run-traces").innerHTML = traces.length
    ? traces
        .map(
          (trace) => `
            <div class="trace-card">
              <div class="panel-heading">
                <strong>${trace.kind}</strong>
                <span class="chip">${trace.status}</span>
              </div>
              <p>${trace.model_route ?? "No model route recorded"}</p>
              ${chipRow(trace.retrieval_lanes)}
            </div>
          `
        )
        .join("")
    : `<div class="trace-card"><strong>No run traces yet</strong><p class="muted">Run Susan or capture agent traces to compare prompt, retrieval, and tool changes here.</p></div>`;
}

function renderReconciliation(report) {
  document.querySelector("#reconciliation-issues").innerHTML = report.issues
    .map(
      (issue) => `
        <div class="issue-card">
          <div class="panel-heading">
            <strong>${issue.title}</strong>
            ${severityBadge(issue.severity)}
          </div>
          <p>${issue.detail}</p>
          <p class="muted">${issue.recommendation}</p>
        </div>
      `
    )
    .join("");
}

async function loadWorkspace() {
  const [tenants, scorecard, profiles, promptBundles, research, servers, tools, policies, traces, reconciliation] = await Promise.all([
    api("/api/tenants"),
    api(`/api/tenants/${state.tenantId}/scorecard`),
    api("/api/agents/profiles"),
    api("/api/prompts/bundles"),
    api("/api/research/prompt-intelligence"),
    api("/api/mcp/servers"),
    api("/api/mcp/tools"),
    api("/api/routing/policies"),
    api(`/api/runs/traces?tenant_id=${encodeURIComponent(state.tenantId)}`),
    api("/api/audits/reconcile"),
  ]);

  renderTenants(tenants);
  renderScorecard(scorecard);
  renderAgentProfiles(profiles);
  renderPromptBundles(promptBundles);
  renderResearch(research);
  renderMcp(servers, tools);
  renderRoutingPolicies(policies);
  renderRunTraces(traces);
  renderReconciliation(reconciliation);
}

async function runSearch(query) {
  const includeVector = document.querySelector("#search-vector").checked;
  const params = new URLSearchParams({
    q: query,
    tenant_id: state.tenantId,
    top_k: "8",
    include_vector: includeVector ? "true" : "false",
  });
  const response = await api(`/api/knowledge/search?${params.toString()}`);
  renderSearch(response);
}

document.querySelector("#search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = new FormData(event.currentTarget).get("search");
  await runSearch(String(query));
});

document.querySelector("#refresh-all").addEventListener("click", async () => {
  await loadWorkspace();
  await runSearch(document.querySelector("#search-input").value);
});

await loadWorkspace();
await runSearch(document.querySelector("#search-input").value);
