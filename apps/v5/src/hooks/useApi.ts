"use client";
import useSWR from "swr";
import { api } from "@/lib/api";
import type { CapabilitySummary } from "@/lib/api";
import { defaultState } from "@/lib/state";

export function useApi() {
  const ctx = useSWR("context", () => api.context(), {
    fallbackData: defaultState.context as unknown as Record<string, string>,
    onError: () => {},
    refreshInterval: 30000,
  });
  const status = useSWR("status", () => api.status(), {
    fallbackData: defaultState.status as unknown as Record<string, number>,
    onError: () => {},
    refreshInterval: 30000,
  });
  const debrief = useSWR("debrief", () => api.debrief(), {
    fallbackData: defaultState.debrief as unknown as { greeting: string; actions: Record<string, string[]>; debrief: string[]; status: string[] },
    onError: () => {},
  });
  const capSummary = useSWR("capabilitySummary", () => api.capabilitySummary(), {
    onError: () => {},
    refreshInterval: 30000,
  });

  const apiLive = !ctx.error && !status.error;

  // When summary data is available, build enriched capabilities for downstream consumers
  const capabilitySummary: CapabilitySummary[] | null = capSummary.data ?? null;

  return {
    context: (ctx.data as unknown as typeof defaultState.context) ?? defaultState.context,
    status: (status.data as unknown as typeof defaultState.status) ?? defaultState.status,
    debrief: (debrief.data as unknown as typeof defaultState.debrief) ?? defaultState.debrief,
    decisions: defaultState.decisions,
    capabilities: defaultState.capabilities,
    capabilitySummary,
    agents: defaultState.agents,
    vision: defaultState.vision,
    apiLive,
    refresh: () => {
      ctx.mutate();
      status.mutate();
      debrief.mutate();
    },
    refreshCapabilities: () => {
      capSummary.mutate();
    },
  };
}
