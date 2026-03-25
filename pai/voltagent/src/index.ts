// Jake PAI — VoltAgent Runtime
// Root supervisor with 15 department heads, real-time VoltOps monitoring
//
// Start: npm run dev
// Monitor: https://console.voltagent.dev (connects to localhost:3141)

import "dotenv/config";
import { VoltAgent, Agent, createTool, Memory } from "@voltagent/core";
import { AnthropicProvider } from "@voltagent/anthropic-ai";
import { SupabaseMemoryAdapter } from "@voltagent/supabase";
import { LibSQLMemoryAdapter } from "@voltagent/libsql";
import { HonoServer } from "@voltagent/server-hono";
import { createPinoLogger } from "@voltagent/logger";
import { z } from "zod";

import {
  departmentHeads,
  headStrategy,
  headProduct,
  headEngineering,
  headLanguages,
  headInfrastructure,
  headQualitySecurity,
  headDataAI,
  headDevEx,
  headResearch,
  headGrowth,
  headContentDesign,
  headFilm,
  headHealth,
  headBehavioral,
  headSpecialized,
} from "./agents/department-heads.js";
import { susanSearch, susanFoundry, susanResearch } from "./tools/susan-tools.js";

// --- Memory ---
// Use Supabase for production, LibSQL for local dev
const memory = new Memory({
  storage: process.env.SUPABASE_URL
    ? new SupabaseMemoryAdapter({
        supabaseUrl: process.env.SUPABASE_URL,
        supabaseKey: process.env.SUPABASE_KEY!,
      })
    : new LibSQLMemoryAdapter({
        url: "file:./.voltagent/memory.db",
      }),
});

// --- Anthropic Provider ---
const anthropic = new AnthropicProvider({
  apiKey: process.env.ANTHROPIC_API_KEY!,
});

// --- Jake's Direct Tools ---
const routeToDepartment = createTool({
  name: "route_to_department",
  description: "Route a task to a specific department head for execution",
  parameters: z.object({
    department: z.enum([
      "strategy", "product", "engineering", "languages", "infrastructure",
      "quality-security", "data-ai", "devex", "research", "growth",
      "content-design", "film-production", "health-science",
      "behavioral-science", "specialized-domains",
    ]).describe("Target department"),
    task: z.string().describe("Task description"),
    priority: z.enum(["P0", "P1", "P2", "P3"]).default("P2"),
  }),
  execute: async ({ department, task, priority }) => {
    return `Routed to ${department} department (${priority}): ${task}`;
  },
});

const systemStatus = createTool({
  name: "system_status",
  description: "Check the status of all departments and agents",
  parameters: z.object({
    scope: z.enum(["all", "department"]).default("all"),
    department: z.string().optional(),
  }),
  execute: async ({ scope, department }) => {
    if (scope === "department" && department) {
      const head = departmentHeads[department as keyof typeof departmentHeads];
      return head
        ? `Department: ${department}\nHead: ${head.name}\nStatus: ACTIVE`
        : `Department ${department} not found`;
    }
    const depts = Object.entries(departmentHeads)
      .map(([name, head]) => `${name}: ${head.name} [ACTIVE]`)
      .join("\n");
    return `15 Departments Active:\n${depts}`;
  },
});

// --- Jake (Root Supervisor) ---
const jake = new Agent({
  name: "jake",
  description: "CEO / Root Supervisor — routes tasks to 15 department heads, coordinates cross-department work",
  llm: anthropic,
  model: "claude-opus-4-6",
  instructions: `You are Jake, the CEO and root supervisor of the Startup Intelligence OS.

You manage 15 departments through their heads:
1. Strategy & Business (steve-strategy) — business strategy, legal, finance, fundraising
2. Product (compass-product) — product strategy, UX, design, brand
3. Core Engineering (atlas-engineering) — architecture, APIs, mobile, desktop
4. Language & Framework (typescript-pro) — 28 language/framework specialists
5. Infrastructure & Platform (cloud-architect) — cloud, containers, IaC, SRE
6. Quality & Security (forge-qa + sentinel) — QA, testing, security, compliance
7. Data & AI (nova-ai) — data science, ML, LLMs, data engineering
8. Developer Experience (dx-optimizer) — build systems, tooling, DX
9. Research (research-director) — multi-source intelligence, analysis
10. Growth & Marketing (aria-growth) — growth, community, PR, ASO
11. Content & Design (design-studio-director) — visual design, content, presentations
12. Film & Media (film-studio-director) — full production pipeline + AI gen
13. Health & Fitness Science (coach) — exercise, nutrition, sleep, coaching
14. Behavioral Science (freya) — behavioral economics, psychology, gamification
15. Specialized Domains (fintech-engineer) — blockchain, IoT, fintech, gaming

Your direct staff: Susan (COO), Kira (intent router), orchestrator, digest, oracle-brief, sentinel-health, pattern-matcher, antifragility-monitor, optionality-scout.

Routing rules:
- Classify intent → identify department(s) → delegate to head(s)
- Simple tasks (1 department): route directly
- Complex tasks (multi-department): coordinate through Susan
- Critical tasks (P0): oversee personally with department heads reporting up
- Ambiguous requests: ask for clarification before routing

Always think like a CEO: what's the highest-leverage action right now?`,
  tools: [routeToDepartment, systemStatus, susanSearch, susanFoundry, susanResearch],
  subAgents: [
    headStrategy,
    headProduct,
    headEngineering,
    headLanguages,
    headInfrastructure,
    headQualitySecurity,
    headDataAI,
    headDevEx,
    headResearch,
    headGrowth,
    headContentDesign,
    headFilm,
    headHealth,
    headBehavioral,
    headSpecialized,
  ],
  memory,
});

// --- VoltAgent Server ---
const logger = createPinoLogger({
  name: "jake-pai",
  level: "info",
});

new VoltAgent({
  agents: { jake },
  server: new HonoServer(),
  logger,
});

console.log(`
╔══════════════════════════════════════════════════════╗
║  Jake PAI — VoltAgent Runtime                        ║
║  15 departments | 218 agents | VoltOps monitoring    ║
║                                                      ║
║  Server:  http://localhost:${process.env.VOLTAGENT_PORT || 3141}                   ║
║  Monitor: https://console.voltagent.dev              ║
║  Memory:  ${process.env.SUPABASE_URL ? "Supabase" : "LibSQL (local)"}                            ║
╚══════════════════════════════════════════════════════╝
`);
