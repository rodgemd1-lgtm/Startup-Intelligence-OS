const API_BASE = "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
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
