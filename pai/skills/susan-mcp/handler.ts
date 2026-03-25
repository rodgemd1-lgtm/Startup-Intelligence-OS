// pai/skills/susan-mcp/handler.ts
// OpenClaw skill handler — bridges requests to Susan's department-based agent organization
// V2.0: Department routing, direct agent access, foundry, research, roster queries

import { execSync } from "child_process";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

const SUSAN_BACKEND = "/Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/backend";
const AGENTS_DIR = "/Users/michaelrodgers/Desktop/Startup-Intelligence-OS/susan-team-architect/agents";
const DEPT_DIR = join(AGENTS_DIR, "departments");
const VENV_PYTHON = `${SUSAN_BACKEND}/.venv/bin/python`;

// Department head mapping
const DEPARTMENT_HEADS: Record<string, string> = {
  "strategy": "head-strategy",
  "product": "head-product",
  "engineering": "head-engineering",
  "languages": "head-languages",
  "infrastructure": "head-infrastructure",
  "quality-security": "head-quality-security",
  "data-ai": "head-data-ai",
  "devex": "head-devex",
  "research": "head-research",
  "growth": "head-growth",
  "content-design": "head-content-design",
  "film-production": "head-film-production",
  "health-science": "head-health-science",
  "behavioral-science": "head-behavioral-science",
  "specialized-domains": "head-specialized-domains",
};

interface ToolCall {
  name: string;
  parameters: Record<string, any>;
}

function escapeShell(str: string): string {
  return str.replace(/'/g, "'\\''");
}

export async function handle(tool: ToolCall): Promise<string> {
  const { name, parameters } = tool;

  switch (name) {
    case "susan_search": {
      const query = escapeShell(parameters.query);
      const limit = parameters.limit || 5;
      const cmd = `${VENV_PYTHON} -c "
from rag_engine.retrieval import RAGRetriever
r = RAGRetriever()
results = r.search('${query}', top_k=${limit})
for doc in results:
    print('---')
    print(doc.page_content[:500])
    print(f'Source: {doc.metadata.get(\"source\", \"unknown\")}')
    print(f'Type: {doc.metadata.get(\"data_type\", \"unknown\")}')
"`;
      try {
        return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 30000 }).toString();
      } catch (e: any) {
        return `Search error: ${e.message}`;
      }
    }

    case "susan_department": {
      const dept = parameters.department;
      const head = DEPARTMENT_HEADS[dept];
      if (!head) {
        return `Unknown department: ${dept}. Available: ${Object.keys(DEPARTMENT_HEADS).join(", ")}`;
      }

      const headFile = join(DEPT_DIR, `${head}.md`);
      if (!existsSync(headFile)) {
        return `Department head file not found: ${headFile}. Department may not be built yet.`;
      }

      const headContent = readFileSync(headFile, "utf-8");
      const task = escapeShell(parameters.task);
      const context = escapeShell(parameters.context || "");
      const priority = parameters.priority || "P2";

      // Build department routing prompt
      const routingPrompt = `You are the department head for ${dept}.
Task (${priority}): ${task}
Context: ${context}

Based on your team roster, delegate this to the right specialist(s) and provide your analysis.`;

      // Route through Susan CLI
      const cmd = `${VENV_PYTHON} scripts/susan_cli.py route startup-intelligence-os "${escapeShell(routingPrompt)}"`;
      try {
        return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 60000 }).toString();
      } catch (e: any) {
        return `Department routing error: ${e.message}`;
      }
    }

    case "susan_agent": {
      const agent = escapeShell(parameters.agent);
      const prompt = escapeShell(parameters.prompt);
      const company = parameters.company || "startup-intelligence-os";
      const cmd = `${VENV_PYTHON} scripts/susan_cli.py route ${company} "${prompt}" --agent ${agent}`;
      try {
        return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 60000 }).toString();
      } catch (e: any) {
        return `Agent invocation error: ${e.message}`;
      }
    }

    case "susan_foundry": {
      const company = escapeShell(parameters.company);
      const mode = parameters.mode || "foundry";
      const cmd = `${VENV_PYTHON} scripts/susan_cli.py ${mode} ${company}`;
      try {
        return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 60000 }).toString();
      } catch (e: any) {
        return `Foundry error: ${e.message}`;
      }
    }

    case "susan_research": {
      const topic = escapeShell(parameters.topic);
      const sources = (parameters.sources || ["web"]).join(",");
      const depth = parameters.depth || "standard";
      const cmd = `${VENV_PYTHON} -m research_daemon --command harvest --topic "${topic}" --sources ${sources} --depth ${depth}`;
      try {
        return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 120000 }).toString();
      } catch (e: any) {
        return `Research error: ${e.message}`;
      }
    }

    case "susan_roster": {
      const action = parameters.action;

      switch (action) {
        case "list-departments": {
          const depts = Object.entries(DEPARTMENT_HEADS).map(([dept, head]) => {
            const headFile = join(DEPT_DIR, `${head}.md`);
            const exists = existsSync(headFile);
            return `${dept}: ${head} [${exists ? "ACTIVE" : "PENDING"}]`;
          });
          return `15 Departments:\n${depts.join("\n")}`;
        }

        case "list-agents": {
          const dept = parameters.query;
          if (dept && DEPARTMENT_HEADS[dept]) {
            const headFile = join(DEPT_DIR, `${DEPARTMENT_HEADS[dept]}.md`);
            if (existsSync(headFile)) {
              const content = readFileSync(headFile, "utf-8");
              // Extract team roster from the file
              const teamMatch = content.match(/## Team Roster[\s\S]*?(?=\n## )/);
              return teamMatch ? teamMatch[0] : "Team roster section not found in department head file.";
            }
          }
          // List all agent files
          try {
            const result = execSync(`ls ${AGENTS_DIR}/*.md ${DEPT_DIR}/*.md 2>/dev/null | wc -l`).toString().trim();
            return `Total agent files: ${result}`;
          } catch {
            return "Error listing agents.";
          }
        }

        case "find-agent": {
          const query = (parameters.query || "").toLowerCase();
          // Search agent files for matching content
          try {
            const cmd = `grep -rl "${escapeShell(query)}" ${AGENTS_DIR}/ ${DEPT_DIR}/ 2>/dev/null | head -10`;
            const matches = execSync(cmd).toString().trim();
            return matches || "No matching agents found.";
          } catch {
            return "No matching agents found.";
          }
        }

        case "department-status": {
          const activeCount = Object.values(DEPARTMENT_HEADS).filter(head =>
            existsSync(join(DEPT_DIR, `${head}.md`))
          ).length;
          return `Department status: ${activeCount}/15 active heads built.`;
        }

        default:
          return `Unknown roster action: ${action}. Use: list-departments, list-agents, find-agent, department-status`;
      }
    }

    default:
      return `Unknown tool: ${name}. Available: susan_search, susan_department, susan_agent, susan_foundry, susan_research, susan_roster`;
  }
}
