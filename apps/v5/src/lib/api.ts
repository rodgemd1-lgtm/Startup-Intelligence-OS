const API_BASE = "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export interface DecisionOption {
  title: string;
  scores: Record<string, number>;
  total: number;
  summary?: string;
}

export interface DecisionRecord {
  id: string;
  title: string;
  status: string;
  context: string;
  company_id?: string;
  project_id?: string;
  options: DecisionOption[];
  recommendation?: string;
}

export interface CapabilitySummary {
  id: string;
  name: string;
  maturity_current: number;
  maturity_target: number;
  wave: number;
  gaps: string[];
  total_items: number;
  done_items: number;
  progress_percent: number;
  next_level: number | null;
  next_item: string | null;
  threshold: boolean;
  owner_agent: string;
}

export interface CapabilityWithLevels {
  id: string;
  name: string;
  maturity_current: number;
  maturity_target: number;
  wave: number;
  gaps: string[];
  levels: Record<number, { name: string; items: { text: string; done: boolean }[] }>;
  total_items: number;
  done_items: number;
  progress_percent: number;
}

export interface DepartmentStep {
  department_id: string;
  department_name: string;
  role: string;
  depends_on: string[];
  expected_outputs: string[];
}

export interface DepartmentPack {
  id: string;
  name: string;
  mission: string;
  owner_agent: string;
  supporting_agents: string[];
  primary_mode: string;
  decision_requirement: string;
  linked_capabilities: string[];
  current_maturity?: number | null;
  target_maturity?: number | null;
  simulated_maturity?: number | null;
  simulated_run_id?: string;
  simulated_artifact_id?: string;
  simulated_review_path?: string;
  simulated_generated_at?: string;
}

export interface ActionPacket {
  id: string;
  request_text: string;
  inferred_intent: string;
  company_context_id: string;
  company_context_name: string;
  execution_track_id: string;
  primary_department: string;
  supporting_departments: string[];
  dependency_order: string[];
  department_sequence: DepartmentStep[];
  recommended_susan_mode: string;
  required_evidence: string[];
  required_artifacts: string[];
  context_sources: string[];
  routing_notes: string[];
  decision_requirement: string;
  linked_decision_id: string;
  artifact_paths: string[];
  status: string;
  created_at: string;
}

export interface SignalEvent {
  id: string;
  signal_type: string;
  severity: "info" | "warning" | "critical";
  title: string;
  description: string;
  source: string;
  auto_generated: boolean;
  status: string;
  related_ids: Record<string, string>;
  recommended_departments: string[];
  next_action: string;
  created_at: string;
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  status: string;
  path: string;
  metadata: Record<string, unknown>;
}

export interface GraphLink {
  id: string;
  source_id: string;
  target_id: string;
  relation: string;
  metadata: Record<string, unknown>;
}

export interface GraphSnapshot {
  nodes: GraphNode[];
  links: GraphLink[];
  summary: {
    node_count: number;
    link_count: number;
    active: Record<string, string>;
  };
}

export interface RouteResponse {
  inferred_intent: string;
  recommended_departments: DepartmentPack[];
  recommended_susan_mode: string;
  required_evidence: string[];
  required_artifacts: string[];
  decision_requirement: string;
  action_packet: ActionPacket;
  linked_decision_id: string;
}

export const api = {
  context: () => fetchJson<Record<string, string>>("/context"),
  status: () => fetchJson<Record<string, number>>("/status"),
  debrief: (operator = "mike") =>
    fetchJson<{ greeting: string; actions: Record<string, string[]>; debrief: string[]; status: string[] }>(
      `/debrief?operator=${operator}`
    ),
  decisions: () => fetchJson<DecisionRecord[]>("/decisions"),
  capabilities: () => fetchJson<Record<string, unknown>[]>("/capabilities"),
  capabilitySummary: () => fetchJson<CapabilitySummary[]>("/capabilities/summary"),
  capabilityLevels: (id: string) => fetchJson<CapabilityWithLevels>(`/capabilities/${id}/levels`),
  departments: () => fetchJson<DepartmentPack[]>("/departments"),
  signals: () => fetchJson<SignalEvent[]>("/signals"),
  actionPackets: () => fetchJson<ActionPacket[]>("/action-packets"),
  graph: () => fetchJson<GraphSnapshot>("/graph"),
  routeRequest: (requestText: string) => postJson<RouteResponse>("/route/request", { request_text: requestText }),
  toggleItem: (id: string, level: number, index: number) =>
    fetch(`${API_BASE}/capabilities/${id}/levels/${level}/items/${index}`, { method: "PUT" })
      .then((r) => { if (!r.ok) throw new Error(`API error: ${r.status}`); return r.json(); }),
  debate: (decisionId: string, mode: string) =>
    fetch(`${API_BASE}/decision/${decisionId}/debate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    }).then((r) => {
      if (!r.ok) throw new Error(`API error: ${r.status}`);
      return r.json();
    }),
};
