// Susan integration tools — bridge VoltAgent to Susan's RAG, foundry, and research
import { createTool } from "@voltagent/core";
import { z } from "zod";
import { execSync } from "child_process";

const SUSAN_BACKEND = process.env.SUSAN_BACKEND_PATH ||
  "/Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend";
const VENV_PYTHON = `${SUSAN_BACKEND}/.venv/bin/python`;

function runSusan(cmd: string, timeout = 30000): string {
  try {
    return execSync(cmd, { cwd: SUSAN_BACKEND, timeout }).toString();
  } catch (e: any) {
    return `Error: ${e.message}`;
  }
}

export const susanSearch = createTool({
  name: "susan_search",
  description: "Search Susan's RAG knowledge base (10K+ chunks, Voyage AI embeddings)",
  parameters: z.object({
    query: z.string().describe("Search query"),
    limit: z.number().default(5).describe("Max results"),
  }),
  execute: async ({ query, limit }) => {
    const escaped = query.replace(/'/g, "\\'");
    return runSusan(`${VENV_PYTHON} -c "
from rag_engine.retrieval import RAGRetriever
r = RAGRetriever()
results = r.search('${escaped}', top_k=${limit})
for doc in results:
    print('---')
    print(doc.page_content[:500])
    print(f'Source: {doc.metadata.get(\"source\", \"unknown\")}')
"`);
  },
});

export const susanFoundry = createTool({
  name: "susan_foundry",
  description: "Run Susan's capability foundry — capability mapping, team design, maturity scoring",
  parameters: z.object({
    company: z.string().describe("Company name"),
    mode: z.enum(["foundry", "route", "design", "status", "think", "fast"]).default("foundry"),
  }),
  execute: async ({ company, mode }) => {
    return runSusan(`${VENV_PYTHON} scripts/susan_cli.py ${mode} ${company}`, 60000);
  },
});

export const susanResearch = createTool({
  name: "susan_research",
  description: "Dispatch Susan's research pipeline — multi-source intelligence gathering",
  parameters: z.object({
    topic: z.string().describe("Research topic"),
    sources: z.array(z.string()).default(["web"]).describe("Sources: web, arxiv, reddit, appstore"),
  }),
  execute: async ({ topic, sources }) => {
    const escaped = topic.replace(/"/g, '\\"');
    return runSusan(
      `${VENV_PYTHON} -m research_daemon --command harvest --topic "${escaped}" --sources ${sources.join(",")}`,
      120000
    );
  },
});
