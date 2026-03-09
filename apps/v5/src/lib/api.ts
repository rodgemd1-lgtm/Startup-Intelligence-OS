const API_BASE = "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
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

export const api = {
  context: () => fetchJson<Record<string, string>>("/context"),
  status: () => fetchJson<Record<string, number>>("/status"),
  debrief: (operator = "mike") =>
    fetchJson<{ greeting: string; actions: Record<string, string[]>; debrief: string[]; status: string[] }>(
      `/debrief?operator=${operator}`
    ),
  decisions: () => fetchJson<Record<string, unknown>[]>("/decisions"),
  capabilities: () => fetchJson<Record<string, unknown>[]>("/capabilities"),
  capabilitySummary: () => fetchJson<CapabilitySummary[]>("/capabilities/summary"),
  capabilityLevels: (id: string) => fetchJson<CapabilityWithLevels>(`/capabilities/${id}/levels`),
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
