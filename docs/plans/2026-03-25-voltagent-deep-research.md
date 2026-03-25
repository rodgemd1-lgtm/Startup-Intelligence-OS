# VoltAgent Deep Research — Full Platform Architecture
**Date:** 2026-03-25
**Purpose:** Comprehensive technical deep-dive into VoltAgent for potential 83-agent system redesign
**Source:** https://github.com/VoltAgent/voltagent (cloned and analyzed at source level)

---

## 1. Core Framework Architecture

### Package Structure (35 packages)
VoltAgent is a monorepo with these key packages:
- `@voltagent/core` — Agent, Tool, Memory, Workflow, Observability, Hooks, Guardrails
- `@voltagent/server-hono` — Hono-based HTTP server with OpenAPI/Swagger
- `@voltagent/server-elysia` — Elysia-based server alternative
- `@voltagent/serverless-hono` — Serverless (Cloudflare Workers, Vercel Edge, Deno)
- `@voltagent/libsql` — LibSQL/Turso memory + observability adapters
- `@voltagent/postgres` — PostgreSQL memory + vector adapters
- `@voltagent/supabase` — Supabase memory adapter
- `@voltagent/cloudflare-d1` — Cloudflare D1 adapter
- `@voltagent/logger` — Pino-based structured logging
- `@voltagent/voice` — Voice capabilities (ElevenLabs, OpenAI)
- `@voltagent/rag` — RAG/retrieval integration
- `@voltagent/sdk` — Client SDK
- `@voltagent/cli` — CLI scaffolding (`create-voltagent-app`)
- `@voltagent/evals` — Evaluation framework
- `@voltagent/scorers` — Scoring functions for evals
- `@voltagent/mcp-server` — MCP server exposure
- `@voltagent/a2a-server` — Agent-to-Agent protocol
- `@voltagent/langfuse-exporter` — Langfuse observability export
- `@voltagent/vercel-ai-exporter` — Vercel AI export
- `@voltagent/voltagent-memory` — VoltOps managed memory
- `@voltagent/resumable-streams` — Resumable stream support
- `@voltagent/sandbox-e2b` — E2B sandbox integration
- `@voltagent/sandbox-daytona` — Daytona sandbox integration
- `@voltagent/ag-ui` — AG-UI protocol support
- `@voltagent/shared` — Shared utilities

### The VoltAgent Bootstrap Class
`VoltAgent` is the top-level orchestrator. It:
1. Manages an `AgentRegistry` (singleton) for all agent instances
2. Manages a `WorkflowRegistry` (singleton) for all workflows
3. Manages a `TriggerRegistry` for event-driven triggers
4. Initializes global observability (OpenTelemetry-based)
5. Starts the HTTP server (Hono or Elysia)
6. Registers MCP servers and A2A servers
7. Sets global memory, logger, workspace, and tool routing defaults

```typescript
new VoltAgent({
  agents: { supervisorAgent, writerAgent, researchAgent },
  workflows: { contentPipeline, approvalWorkflow },
  memory: new Memory({ storage: new LibSQLMemoryAdapter() }),
  server: honoServer({ port: 3141 }),
  observability: new VoltAgentObservability({ storage: adapter }),
  logger: createPinoLogger({ name: "my-app" }),
  workspace: new Workspace({ rootDir: "./workspace" }),
  toolRouting: { enabled: true },
  mcpServers: { myMcp: mcpServer },
  a2aServers: { myA2a: a2aServer },
});
```

### The Agent Class

The `Agent` class (`packages/core/src/agent/agent.ts`, ~3000+ lines) is the central abstraction:

```typescript
export class Agent {
  readonly id: string;
  readonly name: string;
  readonly purpose?: string;
  readonly instructions: InstructionsDynamicValue;  // string or dynamic function
  readonly model: AgentModelValue;                   // string, LanguageModel, or fallback chain
  readonly hooks: AgentHooks;
  readonly maxSteps: number;
  readonly maxRetries: number;
  readonly markdown: boolean;
  readonly voice?: Voice;
  readonly retriever?: BaseRetriever;
  readonly supervisorConfig?: SupervisorConfig;

  // Private internals
  private readonly memoryManager: MemoryManager;
  private readonly toolManager: ToolManager;
  private readonly toolPoolManager: ToolManager;
  private readonly subAgentManager: SubAgentManager;
  private readonly inputGuardrails: NormalizedInputGuardrail[];
  private readonly outputGuardrails: NormalizedOutputGuardrail[];
  private readonly inputMiddlewares: NormalizedInputMiddleware[];
  private readonly outputMiddlewares: NormalizedOutputMiddleware[];
}
```

### Agent Constructor (`AgentOptions`)

```typescript
type AgentOptions = {
  // Identity
  id?: string;
  name: string;
  purpose?: string;

  // Core AI
  model: AgentModelValue;                    // "openai/gpt-4o" or LanguageModel or fallback chain
  instructions: InstructionsDynamicValue;     // string or dynamic function

  // Tools & Memory
  tools?: (Tool | Toolkit | VercelTool)[] | DynamicValue<(Tool | Toolkit)[]>;
  toolkits?: Toolkit[];
  toolRouting?: ToolRoutingConfig | false;
  workspace?: Workspace | WorkspaceConfig | false;
  memory?: Memory | false;
  summarization?: AgentSummarizationOptions | false;

  // Retriever/RAG
  retriever?: BaseRetriever;

  // SubAgents
  subAgents?: SubAgentConfig[];
  supervisorConfig?: SupervisorConfig;

  // Hooks
  hooks?: AgentHooks;

  // Guardrails
  inputGuardrails?: InputGuardrail[];
  outputGuardrails?: OutputGuardrail[];

  // Middleware
  inputMiddlewares?: InputMiddleware[];
  outputMiddlewares?: OutputMiddleware[];
  maxMiddlewareRetries?: number;

  // Configuration
  temperature?: number;
  maxOutputTokens?: number;
  maxSteps?: number;
  maxRetries?: number;
  stopWhen?: StopWhen;
  markdown?: boolean;

  // Voice, Workspace, Eval, Feedback
  voice?: Voice;
  eval?: AgentEvalConfig;
  feedback?: AgentFeedbackOptions | boolean;

  // System
  logger?: Logger;
  voltOpsClient?: VoltOpsClient;
  observability?: VoltAgentObservability;
  context?: ContextInput;
};
```

### Four Core Methods
The Agent exposes 4 interaction methods:
1. **`generateText(input, options?)`** — Returns full text response (blocking)
2. **`streamText(input, options?)`** — Returns streaming text response
3. **`generateObject(input, options?)`** — Returns structured object (validated by Zod schema)
4. **`streamObject(input, options?)`** — Returns streaming structured object

Each method follows this lifecycle:
1. Create OperationContext (userId, conversationId, operationId, tracing)
2. Run input middlewares
3. Run input guardrails
4. Prepare execution (resolve instructions, build messages, resolve tools)
5. Call the LLM via Vercel AI SDK
6. Run output guardrails
7. Run output middlewares
8. Persist to memory
9. Return result with context

### Provider Abstraction (Model Router)

VoltAgent uses a **model router** pattern based on Vercel AI SDK. Models are specified as strings:

```typescript
model: "openai/gpt-4o-mini"       // Auto-resolves via ModelProviderRegistry
model: "anthropic/claude-sonnet-4-20250514"
model: "google/gemini-2.0-flash"
model: "groq/llama-3.3-70b"
model: "openrouter/anthropic/claude-sonnet-4-20250514"
```

The `ModelProviderRegistry` auto-discovers providers by:
1. Looking for env vars (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
2. Lazy-loading the npm provider package (@ai-sdk/openai, @ai-sdk/anthropic, etc.)
3. Caching the resolved `LanguageModel` factory

**Model Fallback Chains** — agents can specify multiple models with retry/fallback:

```typescript
model: [
  { model: "openai/gpt-4o", maxRetries: 2 },
  { model: "anthropic/claude-sonnet-4-20250514", maxRetries: 1 },
  { model: "openai/gpt-4o-mini" },  // final fallback
]
```

### Dynamic Instructions

Instructions can be static strings or async functions resolved per-call:

```typescript
instructions: "You are a helpful assistant"

// Or dynamic:
instructions: async ({ context }) => {
  const prompt = await fetchPromptFromDB(context.userId);
  return prompt;
}
```

---

## 2. Supervisor / Sub-Agent Model

### How Supervisors Work

Any agent with `subAgents` automatically becomes a **supervisor**. The framework generates delegation tools for each sub-agent, creating a tool-based handoff pattern.

```typescript
const contentCreator = new Agent({
  name: "ContentCreator",
  purpose: "Drafts short content",
  instructions: "Creates short text content on requested topics",
  model: "openai/gpt-4o-mini",
});

const formatter = new Agent({
  name: "Formatter",
  purpose: "Cleans and formats text",
  instructions: "Formats and styles text content",
  model: "openai/gpt-4o-mini",
  tools: [uppercaseTool],
});

const supervisor = new Agent({
  name: "Supervisor",
  instructions: "Coordinates between content creation and formatting agents",
  model: "openai/gpt-4o-mini",
  subAgents: [contentCreator, formatter],
  supervisorConfig: {
    fullStreamEventForwarding: {
      types: ["tool-call", "tool-result", "text-delta"],
    },
  },
});
```

### Supervisor System Message (Auto-Generated)

The `SubAgentManager.generateSupervisorSystemMessage()` builds a structured prompt:

```
You are a supervisor agent that coordinates between specialized agents:

<specialized_agents>
- ContentCreator: Drafts short content
- Formatter: Cleans and formats text
</specialized_agents>

<instructions>
Coordinates between content creation and formatting agents
</instructions>

<guidelines>
- Provide a final answer to the User when you have a response from all agents.
- Do not mention the name of any agent in your response.
- Make sure that you optimize your communication by contacting MULTIPLE agents at the same time whenever possible.
- Keep your communications with other agents concise and terse.
- Agents are not aware of each other's existence. You need to act as the sole intermediary.
- Provide full context and details when necessary.
- Only communicate with the agents that are necessary for the query.
- Never assume any parameter values while invoking a function.
</guidelines>

<agents_memory>
{previous interaction history}
</agents_memory>
```

### Routing Algorithm

The supervisor delegates via **auto-generated tools** — one tool per sub-agent. The LLM decides which agent(s) to call based on:
1. Agent names and purposes in the system message
2. The user's query
3. Previous agent interaction history (`<agents_memory>`)

The supervisor can call multiple sub-agents simultaneously (parallel tool calls).

### Context Flow

1. Supervisor receives user input
2. LLM generates tool call(s) targeting sub-agent(s)
3. `SubAgentManager.handoffTask()` creates a new operation context for the sub-agent
4. Sub-agent executes with the task as input (can use streamText or generateText)
5. Sub-agent result flows back as tool result to the supervisor
6. Supervisor synthesizes final response

### SubAgent Configuration Types

Sub-agents can be configured with different execution methods:

```typescript
// Direct agent (defaults to streamText)
subAgents: [myAgent]

// Explicit method configuration
subAgents: [
  createSubagent({ agent: myAgent, method: "streamText" }),
  createSubagent({ agent: myAgent, method: "generateText" }),
  createSubagent({ agent: myAgent, method: "generateObject", schema: mySchema }),
]
```

### Multi-Level Hierarchies

Sub-agents can themselves have sub-agents, creating arbitrary depth:

```typescript
const researcher = new Agent({ name: "Researcher", ... });
const writer = new Agent({ name: "Writer", ... });
const editor = new Agent({ name: "Editor", ... });

const contentTeam = new Agent({
  name: "ContentTeam",
  subAgents: [researcher, writer],
  ...
});

const topSupervisor = new Agent({
  name: "TopSupervisor",
  subAgents: [contentTeam, editor],
  ...
});
```

Stream events carry `agentPath` metadata: `["TopSupervisor", "ContentTeam", "Writer"]`.

### SupervisorConfig

```typescript
type SupervisorConfig = {
  systemMessage?: string;               // Override default supervisor prompt
  includeAgentsMemory?: boolean;         // Include agent interaction history (default: true)
  customGuidelines?: string[];           // Extra guidelines appended to defaults
  fullStreamEventForwarding?: {
    types?: StreamEventType[];           // Events to forward from sub-agents
  };
  throwOnStreamError?: boolean;          // Throw on sub-agent errors (default: false)
  includeErrorInEmptyResponse?: boolean; // Include error text when no content (default: true)
};
```

---

## 3. Memory System

### Architecture

Memory in VoltAgent uses a **three-adapter pattern**:

```typescript
const memory = new Memory({
  storage: new LibSQLMemoryAdapter(),           // REQUIRED: conversation/message persistence
  embedding: "openai/text-embedding-3-small",   // OPTIONAL: embedding model
  vector: new InMemoryVectorAdapter(),          // OPTIONAL: vector similarity search
  workingMemory: {                              // OPTIONAL: per-conversation state
    enabled: true,
    scope: "conversation",                      // or "user"
    schema: z.object({ preferences: z.string() }), // or template string
  },
  enableCache: true,
  cacheSize: 1000,
  cacheTTL: 3600000,
});
```

### Storage Adapters (Conversation Persistence)

| Adapter | Package | Backend |
|---------|---------|---------|
| `LibSQLMemoryAdapter` | `@voltagent/libsql` | LibSQL/Turso (SQLite) |
| `PostgresMemoryAdapter` | `@voltagent/postgres` | PostgreSQL |
| `SupabaseMemoryAdapter` | `@voltagent/supabase` | Supabase |
| `CloudflareD1MemoryAdapter` | `@voltagent/cloudflare-d1` | Cloudflare D1 |
| `InMemoryStorageAdapter` | `@voltagent/core` | In-memory (dev/test) |

### Vector Adapters (Similarity Search)

| Adapter | Package |
|---------|---------|
| `InMemoryVectorAdapter` | `@voltagent/core` |
| `LibSQLVectorAdapter` | `@voltagent/libsql` |
| `PostgresVectorAdapter` | `@voltagent/postgres` |

External vector DB examples exist for: Pinecone, Qdrant, ChromaDB, LanceDB.

### Embedding Adapters

Can be a string model ID (`"openai/text-embedding-3-small"`) or a custom adapter implementing:
```typescript
interface EmbeddingAdapter {
  embed(text: string): Promise<number[]>;
  embedBatch(texts: string[]): Promise<number[][]>;
}
```

### Memory Scoping

- **Per-Agent**: Each agent gets its own memory instance (or inherits global)
- **Global Agent Memory**: Set via `VoltAgent({ agentMemory: memory })`, shared by all agents
- **Global Workflow Memory**: Set via `VoltAgent({ workflowMemory: memory })`, shared by all workflows
- **Agent-Specific Override**: `new Agent({ memory: mySpecificMemory })` overrides global
- **Disabled**: `new Agent({ memory: false })` for stateless agents

### Memory Operations

```typescript
// Core operations on Memory class
await memory.getMessages(userId, conversationId, options?);
await memory.addMessage(message, userId, conversationId);
await memory.addMessages(messages, userId, conversationId);
await memory.clearMessages(userId, conversationId?);
await memory.search(query, userId, options?);           // Semantic search
await memory.getConversation(userId, conversationId);
await memory.createConversation(input);
await memory.listConversations(options?);
```

### Working Memory

Working memory is agent-scoped state that persists across turns but is separate from conversation history:

```typescript
// Schema-based (JSON)
workingMemory: {
  enabled: true,
  scope: "conversation",
  schema: z.object({
    userPreferences: z.string(),
    taskProgress: z.number(),
  }),
}

// Template-based (Markdown)
workingMemory: {
  enabled: true,
  template: `
    ## User Context
    - Name: {{name}}
    - Preferences: {{preferences}}
  `,
}
```

### Conversation Persistence Modes

```typescript
conversationPersistence: {
  mode: "step",         // Persist after each step (default)
  // mode: "finish",    // Persist only at operation completion
  debounceMs: 200,      // Debounce for step-level persistence
  flushOnToolResult: true, // Flush on tool completion
}
```

### Summarization

Built-in conversation summarization to manage context windows:

```typescript
summarization: {
  enabled: true,
  triggerTokens: 8000,    // Summarize when conversation exceeds this
  keepMessages: 4,         // Keep last N messages unsummarized
  maxOutputTokens: 500,
  systemPrompt: "Summarize the key points...",
  model: "openai/gpt-4o-mini",  // Can use cheaper model for summarization
}
```

---

## 4. Workflow Engine

### Two APIs: Functional and Fluent Chain

**Functional API (`createWorkflow`)**:
```typescript
const workflow = createWorkflow(
  {
    id: "order-processing",
    name: "Order Processing",
    input: z.object({ orderId: z.string(), amount: z.number() }),
    result: z.object({ status: z.string(), total: z.number() }),
  },
  andThen({ id: "validate", execute: async ({ data }) => ... }),
  andAgent(promptFn, agent, { schema }),
  andThen({ id: "finalize", execute: async ({ data }) => ... }),
);
```

**Fluent Chain API (`createWorkflowChain`)**:
```typescript
const workflow = createWorkflowChain({
  id: "research",
  input: z.object({ topic: z.string() }),
  result: z.object({ text: z.string() }),
})
  .andThen({ id: "research", execute: async ({ data }) => ... })
  .andThen({ id: "write", execute: async ({ data }) => ... });
```

### Step Types (17 total)

| Step | Purpose |
|------|---------|
| `andThen` | Sequential computation — transform data |
| `andAgent` | Call an AI agent with dynamic prompt |
| `andWhen` | Conditional — execute only if condition is true |
| `andAll` | Parallel — run multiple steps concurrently |
| `andRace` | Parallel — first to complete wins |
| `andTap` | Side effect — logging, metrics (data passes through) |
| `andGuardrail` | Apply input/output guardrails |
| `andSleep` | Pause for duration (ms) |
| `andSleepUntil` | Pause until specific datetime |
| `andForEach` | Iterate array items (with concurrency control) |
| `andBranch` | Multi-branch conditional routing |
| `andDoWhile` | Loop while condition is true |
| `andDoUntil` | Loop until condition becomes true |
| `andMap` | Transform/reshape data declaratively |
| `andWorkflow` | Nest another workflow as a step |

### State Management

Each step receives a `WorkflowStepContext`:

```typescript
interface WorkflowStepContext<T> {
  data: T;                                    // Current step's input data
  input: unknown;                              // Original workflow input
  workflowState: WorkflowStateStore;           // Shared mutable state
  setWorkflowState: WorkflowStateUpdater;      // Update shared state
  getStepData: (stepId: string) => StepData;   // Access previous step results
  suspend: (reason, metadata?) => Promise<void>; // Human-in-the-loop suspend
  resumeData?: unknown;                         // Data from resume after suspend
  signal: AbortSignal;                          // Cancellation signal
  stream: WorkflowStreamWriter;                 // Write events to stream
}
```

### Suspend/Resume (Human-in-the-Loop)

Workflows support suspension for human approval:

```typescript
andThen({
  id: "approval",
  resumeSchema: z.object({
    approved: z.boolean(),
    managerId: z.string(),
  }),
  execute: async ({ data, suspend, resumeData }) => {
    if (resumeData) {
      return { ...data, approved: resumeData.approved };
    }
    if (data.amount > 500) {
      await suspend("Manager approval required", { amount: data.amount });
    }
    return { ...data, approved: true };
  },
});

// Execution:
const result = await workflow.run({ input: data });
// result.status === "suspended"
// Later:
const resumed = await result.resume({ approved: true, managerId: "mgr-1" });
```

### Error Handling and Retry

Workflows support per-workflow retry configuration and step-level error serialization. Steps that throw are caught, serialized, and can trigger workflow-level error handlers.

### Workflow Hooks

```typescript
type WorkflowHooks = {
  onStart?: (ctx: WorkflowHookContext) => void;
  onStepStart?: (ctx: WorkflowHookContext, stepId: string) => void;
  onStepEnd?: (ctx: WorkflowHookContext, stepId: string, status: string) => void;
  onEnd?: (ctx: WorkflowHookContext, status: string) => void;
  onError?: (ctx: WorkflowHookContext, error: unknown) => void;
};
```

### Workflow Guardrails

Guardrails can be applied at workflow level or step level:

```typescript
createWorkflow({
  inputGuardrails: [trimInput],       // Applied to workflow input
  outputGuardrails: [redactNumbers],  // Applied to workflow output
}, ...steps);

// Or per-step:
andGuardrail({
  id: "sanitize",
  outputGuardrails: [redactNumbers],
});
```

---

## 5. Tool System

### Tool Definition with Zod

```typescript
const weatherTool = createTool({
  name: "get_weather",
  description: "Get current weather for a location",
  parameters: z.object({
    location: z.string().describe("City name"),
    unit: z.enum(["celsius", "fahrenheit"]).optional(),
  }),
  outputSchema: z.object({               // Optional output validation
    temperature: z.number(),
    condition: z.string(),
  }),
  execute: async ({ location, unit }, options?) => {
    // options includes: context, abortSignal, toolCallId, messages
    return { temperature: 22, condition: "sunny" };
  },
  hooks: {
    onStart: async ({ tool, args }) => { /* pre-execution */ },
    onEnd: async ({ tool, args, output, error }) => { /* post-execution */ },
  },
  tags: ["weather", "external-api"],
  needsApproval: true,  // or a function for dynamic approval
});
```

### Tool Class Properties

```typescript
class Tool<T, O> {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly parameters: T;          // Zod schema
  readonly outputSchema?: O;       // Optional Zod output schema
  readonly tags?: string[];
  readonly needsApproval?: boolean | Function;
  readonly providerOptions?: ProviderOptions;  // e.g., Anthropic cache control
  readonly toModelOutput?: (args) => ToolResultOutput;  // Multi-modal output
  readonly execute?: (args, options?) => ToolExecutionResult;
  readonly hooks?: ToolHooks;
  readonly type = "user-defined";
}
```

### Toolkits

Groups of related tools:

```typescript
const toolkit = createToolkit({
  name: "database-toolkit",
  tools: [queryTool, insertTool, updateTool],
});

const agent = new Agent({
  toolkits: [toolkit],
  ...
});
```

### Dynamic Tools

Tools can be resolved per-call:

```typescript
const agent = new Agent({
  tools: async ({ context }) => {
    const userRole = context.get("userRole");
    return userRole === "admin" ? adminTools : basicTools;
  },
});
```

### Tool Routing (Semantic Search)

For agents with many tools, VoltAgent supports semantic tool routing:

```typescript
const agent = new Agent({
  toolRouting: {
    enabled: true,
    topK: 3,                                    // Return top 3 matching tools
    enforceSearchBeforeCall: true,               // Must search before calling
    strategy: createEmbeddingToolSearchStrategy({
      model: "openai/text-embedding-3-small",
    }),
  },
  tools: [...hundredsOfTools],
});
```

This replaces exposing all tools to the LLM with two meta-tools: `searchTools` and `callTool`.

### MCP Tool Integration

```typescript
const mcpConfig = new MCPConfiguration({
  servers: {
    exa: {
      type: "stdio",
      command: "npx",
      args: ["-y", "mcp-remote", "https://mcp.exa.ai/..."],
    },
    filesystem: {
      type: "sse",
      url: "http://localhost:3001/sse",
    },
  },
});

const agent = new Agent({
  tools: await mcpConfig.getTools(),   // MCP tools become VoltAgent tools
  ...
});
```

### Client-Side Tools

Tools without an `execute` function are flagged as client-side, allowing the frontend to handle execution.

### Provider Tools

Vercel AI SDK provider-defined tools (like `openai.tools.webSearch()`) are supported natively.

---

## 6. Hooks System

### Agent Hooks (12 hooks)

```typescript
type AgentHooks = {
  onStart?: (args: OnStartHookArgs) => void;
  onEnd?: (args: OnEndHookArgs) => void;
  onHandoff?: (args: OnHandoffHookArgs) => void;
  onHandoffComplete?: (args: OnHandoffCompleteHookArgs) => void;
  onToolStart?: (args: OnToolStartHookArgs) => void;
  onToolEnd?: (args: OnToolEndHookArgs) => OnToolEndHookResult | void;
  onToolError?: (args: OnToolErrorHookArgs) => OnToolErrorHookResult | void;
  onPrepareMessages?: (args: OnPrepareMessagesHookArgs) => OnPrepareMessagesHookResult;
  onPrepareModelMessages?: (args: OnPrepareModelMessagesHookArgs) => OnPrepareModelMessagesHookResult;
  onError?: (args: OnErrorHookArgs) => void;
  onStepFinish?: (args: OnStepFinishHookArgs) => void;
  onRetry?: (args: OnRetryHookArgs) => void;
  onFallback?: (args: OnFallbackHookArgs) => void;
};
```

### Hook Details

**`onStart`** — Fires when an agent operation begins. Access: agent, context (userId, conversationId, operationId).

**`onEnd`** — Fires when operation completes (success or error). Access: conversationId, agent, output, error, context.

**`onHandoff`** — Fires when a supervisor delegates to a sub-agent. Access: target agent, source agent.

**`onHandoffComplete`** — Fires after sub-agent returns. Access: agent, sourceAgent, result, messages, usage, context. Has a `bail()` function to skip supervisor processing and return sub-agent result directly.

**`onToolStart`** — Before tool execution. Can throw `ToolDeniedError` to block execution (authorization).

**`onToolEnd`** — After tool execution. Can modify the output via return value `{ output: modifiedOutput }`.

**`onToolError`** — On tool failure. Can provide replacement output via return value.

**`onPrepareMessages`** — Transform messages before they go to the LLM. This is the primary hook for context injection:

```typescript
onPrepareMessages: async ({ messages, agent, context }) => {
  const enhanced = messages.map(msg =>
    messageHelpers.addTimestampToMessage(msg, new Date().toISOString())
  );
  return { messages: enhanced };
},
```

**`onPrepareModelMessages`** — Transform at the model-message level (after UIMessage conversion).

**`onRetry`** — Fires on LLM retry or middleware retry. Access: attempt number, max retries, error, model info.

**`onFallback`** — Fires when falling back to next model in a fallback chain. Access: fromModel, nextModel, error.

### Tool-Level Hooks

```typescript
const myTool = createTool({
  hooks: {
    onStart: async ({ tool, args }) => { /* log, validate */ },
    onEnd: async ({ tool, args, output, error }) => { /* transform, log */ },
  },
});
```

### Use Cases for Hooks

1. **Authorization** — `onToolStart` throwing `ToolDeniedError`
2. **Observability** — `onStart`/`onEnd` for tracing
3. **Context Injection** — `onPrepareMessages` adding system context
4. **Guardrails** — `onToolEnd` validating/modifying outputs
5. **Audit Logging** — `onEnd` persisting to external systems
6. **Cost Tracking** — `onEnd` with usage info
7. **Fallback Monitoring** — `onRetry`/`onFallback` for reliability alerts

---

## 7. Guardrails and Middleware

### Input Guardrails

Validate/transform input before LLM processing:

```typescript
const trimInput = createInputGuardrail({
  name: "trim-input",
  description: "Trim whitespace from input",
  severity: "info",
  handler: async ({ input, inputText, originalInput, agent, context }) => ({
    pass: true,
    action: "modify",                     // "allow" | "modify" | "block"
    modifiedInput: typeof input === "string" ? input.trim() : input,
  }),
});
```

### Output Guardrails

Validate/transform output after LLM processing:

```typescript
const redactPII = createOutputGuardrail({
  name: "redact-pii",
  severity: "critical",
  handler: async ({ output, outputText, agent, context }) => ({
    pass: true,
    action: "modify",
    modifiedOutput: output.replace(/\d{3}-\d{2}-\d{4}/g, "***-**-****"),
  }),
});
```

### Built-in Guardrails

VoltAgent ships with factory functions for common guardrails:
- `createSensitiveNumberGuardrail()`
- `createEmailRedactorGuardrail()`
- `createPhoneNumberGuardrail()`
- `createProfanityGuardrail()`
- `createMaxLengthGuardrail()`
- `createPromptInjectionGuardrail()`
- `createPIIInputGuardrail()`
- `createHTMLSanitizerInputGuardrail()`
- `createDefaultSafetyGuardrails()` — Combines multiple
- `createDefaultPIIGuardrails()` — PII-focused bundle

### Middleware (Retry-Capable)

Middleware is similar to guardrails but supports retry loops:

```typescript
const authMiddleware = createInputMiddleware({
  name: "auth-check",
  handler: async ({ input, context, abort, retryCount }) => {
    if (!context.get("authToken")) {
      abort("Unauthorized", { httpStatus: 401 });
    }
    return input; // pass-through
  },
});

// On the agent:
const agent = new Agent({
  inputMiddlewares: [authMiddleware],
  outputMiddlewares: [outputValidator],
  maxMiddlewareRetries: 3,
});
```

---

## 8. Example Agents — Gold Standard Patterns

### Pattern 1: Simple Agent with Tools

```typescript
const agent = new Agent({
  name: "WeatherAssistant",
  instructions: "A helpful assistant that provides weather information",
  model: "openai/gpt-4o-mini",
  tools: [weatherTool, calendarTool],
  memory: new Memory({ storage: new LibSQLMemoryAdapter() }),
});
```

### Pattern 2: Supervisor with Sub-Agents

```typescript
const contentCreator = new Agent({
  name: "ContentCreator",
  purpose: "Drafts short content",
  instructions: "Creates short text content on requested topics",
  model: "openai/gpt-4o-mini",
  memory,
});

const formatter = new Agent({
  name: "Formatter",
  purpose: "Cleans and formats text",
  instructions: "Formats and styles text content",
  model: "openai/gpt-4o-mini",
  tools: [uppercaseTool],
  memory,
});

const supervisor = new Agent({
  name: "Supervisor",
  instructions: "Coordinates between content creation and formatting agents",
  model: "openai/gpt-4o-mini",
  memory,
  subAgents: [contentCreator, formatter],
  supervisorConfig: {
    fullStreamEventForwarding: {
      types: ["tool-call", "tool-result", "text-delta"],
    },
  },
});
```

### Pattern 3: Research Assistant with MCP + Workflow Chain

```typescript
const mcpConfig = new MCPConfiguration({
  servers: {
    exa: { type: "stdio", command: "npx", args: ["-y", "mcp-remote", url] },
  },
});

const assistant = new Agent({
  name: "Assistant",
  instructions: "Generate search queries using exa tools.",
  model: "openai/gpt-4o-mini",
  tools: await mcpConfig.getTools(),
});

const writer = new Agent({
  name: "Writer",
  instructions: "Write a report according to instructions.",
  model: "openai/gpt-4o",
  tools: await mcpConfig.getTools(),
  markdown: true,
  maxSteps: 50,
});

const workflow = createWorkflowChain({
  id: "research",
  input: z.object({ topic: z.string() }),
  result: z.object({ text: z.string() }),
})
  .andThen({
    id: "research",
    execute: async ({ data }) => {
      const result = await assistant.generateText(`Generate queries for ${data.topic}`);
      return { text: result.text };
    },
  })
  .andThen({
    id: "write",
    execute: async ({ data }) => {
      const result = await writer.generateText(`Write report based on: ${data.text}`);
      return { text: result.text };
    },
  });
```

### Pattern 4: Agent with Full Hooks + Guardrails

```typescript
const agent = new Agent({
  name: "SecureAgent",
  instructions: "A secure, audited assistant",
  model: "openai/gpt-4o",
  tools: [weatherTool],
  memory,
  hooks: {
    onStart: async ({ agent, context }) => { log("started", context.operationId); },
    onToolStart: async ({ tool, args, context }) => {
      if (args.location === "restricted" && context.userId === "guest") {
        throw new ToolDeniedError({ toolName: tool.name, message: "Forbidden" });
      }
    },
    onToolEnd: async ({ tool, output }) => { log("tool done", output); },
    onEnd: async ({ output, error }) => { auditLog(output, error); },
    onPrepareMessages: async ({ messages }) => {
      return { messages: messages.map(m => addTimestamp(m)) };
    },
  },
  inputGuardrails: [createPromptInjectionGuardrail()],
  outputGuardrails: [createPIIInputGuardrail()],
});
```

### Pattern 5: Workflow with Agent Steps, Branching, and Loops

See the full workflow example in Section 4 above. The key patterns:
- `andAgent()` wraps any Agent into a workflow step with dynamic prompts and typed output schemas
- `andBranch()` enables conditional routing
- `andDoWhile()`/`andDoUntil()` enable iterative processing
- `andForEach()` enables batch processing with concurrency control
- `suspend()`/`resume()` enables human-in-the-loop approval flows

---

## 9. Deployment Model

### VoltAgent Server (Hono-Based)

The default server is Hono (fast, lightweight, runs on Node.js, Bun, Deno):

```typescript
new VoltAgent({
  server: honoServer({
    port: 3141,
    enableSwaggerUI: true,
    corsOrigin: "*",
  }),
});
```

### API Endpoints Exposed

The server automatically exposes:
- `GET /api/agents` — List all registered agents
- `GET /api/agents/:id` — Get agent details (tools, sub-agents, memory state)
- `POST /api/agents/:id/generate` — Generate text
- `POST /api/agents/:id/stream` — Stream text
- `POST /api/agents/:id/generate-object` — Generate structured object
- `POST /api/agents/:id/stream-object` — Stream structured object
- `GET /api/workflows` — List all workflows
- `GET /api/workflows/:id` — Workflow details
- `POST /api/workflows/:id/run` — Run workflow
- `POST /api/workflows/:id/stream` — Stream workflow
- Swagger UI at `/docs` (optional)

### Serverless Deployment

```typescript
import { serverlessHono } from "@voltagent/serverless-hono";

const app = new VoltAgent({
  serverless: serverlessHono({ corsOrigin: "*" }),
  agents: { myAgent },
});

// Cloudflare Workers
export default app.serverless.toCloudflareWorker();

// Vercel Edge
export default app.serverless.toVercelEdge();

// Deno
export default app.serverless.toDeno();
```

### VoltOps Dev Console

VoltOps is a cloud-hosted dev console (console.voltagent.dev) that provides:
- Real-time agent monitoring and tracing
- Conversation history viewer
- Tool execution visualization
- Prompt management (remote prompts)
- Feedback collection
- Trigger management

Connection is via API key:
```typescript
new VoltAgent({
  voltOpsClient: new VoltOpsClient({
    publicKey: process.env.VOLTAGENT_PUBLIC_KEY,
    secretKey: process.env.VOLTAGENT_SECRET_KEY,
  }),
});
```

### MCP Server Exposure

Agents can be exposed as MCP servers:

```typescript
import { MCPServer } from "@voltagent/mcp-server";

new VoltAgent({
  mcpServers: {
    main: new MCPServer({ name: "my-agents" }),
  },
});
```

### A2A Protocol

Agent-to-Agent protocol for cross-system agent communication:

```typescript
import { A2AServer } from "@voltagent/a2a-server";

new VoltAgent({
  a2aServers: {
    main: new A2AServer({ name: "my-a2a" }),
  },
});
```

---

## 10. Key Architectural Decisions for 83-Agent Redesign

### What VoltAgent Does Well

1. **TypeScript-native** — Full type safety with Zod schemas everywhere
2. **Provider-agnostic** — Model router supports 20+ providers via string IDs
3. **Memory is pluggable** — Storage/embedding/vector adapters are independent
4. **Workflow engine is comprehensive** — 17 step types cover most orchestration patterns
5. **Hooks are rich** — 12 agent hooks + tool hooks enable deep customization
6. **Sub-agent model is automatic** — Just add `subAgents[]` and the framework handles routing
7. **Guardrails are first-class** — Built-in guardrail library + custom guardrail support
8. **Observability is built-in** — OpenTelemetry tracing from day one
9. **Tool routing** — Semantic search over tool pools solves the "too many tools" problem
10. **Serverless-ready** — Same code runs on Node, Bun, CF Workers, Vercel Edge

### Considerations for 83-Agent System

1. **Flat Registration** — VoltAgent registers all agents in a flat registry. With 83 agents, you would organize via supervisor hierarchies (supervisor-of-supervisors), not flat lists.

2. **Memory Sharing** — Global memory is shared, but per-agent memory is easy. For 83 agents, you would likely use shared memory for coordination agents and isolated memory for specialist agents.

3. **Tool Routing** — With 83 agents each having tools, tool routing (semantic search) is essential. Set `toolRouting: { enabled: true }` globally.

4. **Model Fallback Chains** — Critical for reliability at scale. Each agent can specify primary + fallback models.

5. **Workflow Composition** — Complex pipelines can be built by nesting workflows (`andWorkflow`) and composing agents within steps.

6. **Dynamic Agent Resolution** — Instructions and tools can be resolved dynamically per-call, enabling runtime configuration.

7. **Cost Management** — Use cheaper models (gpt-4o-mini) for coordinator/routing agents and powerful models (claude-sonnet, gpt-4o) for specialist agents.

8. **Evaluation** — Built-in eval framework (`@voltagent/evals`, `@voltagent/scorers`) enables quality monitoring per agent.

---

## 11. Package Dependency Graph

```
@voltagent/core (foundation)
  |-- ai (Vercel AI SDK)
  |-- zod
  |-- @opentelemetry/api
  |
  +-- @voltagent/server-hono (HTTP server)
  |     |-- hono
  |
  +-- @voltagent/libsql (storage)
  |     |-- @libsql/client
  |
  +-- @voltagent/postgres (storage)
  |     |-- pg
  |
  +-- @voltagent/supabase (storage)
  |     |-- @supabase/supabase-js
  |
  +-- @voltagent/logger
  |     |-- pino
  |
  +-- @voltagent/sdk (client)
  +-- @voltagent/evals (testing)
  +-- @voltagent/mcp-server
  +-- @voltagent/a2a-server
  +-- @voltagent/voice
  +-- @voltagent/rag
```
