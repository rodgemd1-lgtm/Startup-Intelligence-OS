"use client";
import useSWR from "swr";
import { api } from "@/lib/api";
import type {
  ActionPacket,
  CapabilitySummary,
  DecisionRecord,
  DepartmentPack,
  SignalEvent,
} from "@/lib/api";
import { defaultState } from "@/lib/state";

function deriveAgentsFromDepartments(departments: DepartmentPack[]) {
  const seen = new Set<string>();
  const derived = [];
  for (const department of departments) {
    const agents = [department.owner_agent, ...department.supporting_agents];
    for (const agent of agents) {
      if (!agent || seen.has(agent)) continue;
      seen.add(agent);
      derived.push({
        name: agent,
        group: department.name,
        role: agent === department.owner_agent ? "owner" : "support",
      });
    }
  }
  return derived;
}

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
  const decisions = useSWR("decisions", () => api.decisions(), {
    fallbackData: defaultState.decisions as unknown as DecisionRecord[],
    onError: () => {},
    refreshInterval: 30000,
  });
  const departments = useSWR("departments", () => api.departments(), {
    fallbackData: [] as DepartmentPack[],
    onError: () => {},
    refreshInterval: 30000,
  });
  const signals = useSWR("signals", () => api.signals(), {
    fallbackData: [] as SignalEvent[],
    onError: () => {},
    refreshInterval: 30000,
  });
  const actionPackets = useSWR("actionPackets", () => api.actionPackets(), {
    fallbackData: [] as ActionPacket[],
    onError: () => {},
    refreshInterval: 30000,
  });
  const graph = useSWR("graph", () => api.graph(), {
    onError: () => {},
    refreshInterval: 30000,
  });

  const apiLive = !ctx.error && !status.error;

  const capabilitySummary: CapabilitySummary[] | null = capSummary.data ?? null;
  const departmentData = departments.data ?? [];
  const derivedAgents = departmentData.length > 0
    ? deriveAgentsFromDepartments(departmentData)
    : defaultState.agents;

  return {
    context: (ctx.data as unknown as typeof defaultState.context) ?? defaultState.context,
    status: (status.data as unknown as typeof defaultState.status) ?? defaultState.status,
    debrief: (debrief.data as unknown as typeof defaultState.debrief) ?? defaultState.debrief,
    decisions: (decisions.data as unknown as typeof defaultState.decisions) ?? defaultState.decisions,
    capabilities: defaultState.capabilities,
    capabilitySummary,
    departments: departmentData,
    signals: signals.data ?? [],
    actionPackets: actionPackets.data ?? [],
    graph: graph.data ?? null,
    agents: derivedAgents,
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
    refreshOperator: () => {
      decisions.mutate();
      departments.mutate();
      signals.mutate();
      actionPackets.mutate();
      graph.mutate();
      debrief.mutate();
      status.mutate();
    },
  };
}
