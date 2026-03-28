/**
 * Jake Gateway — Cloudflare Worker (V20)
 *
 * Central nervous system for the Startup Intelligence OS.
 * Edge gateway with D1 ops database, Workers AI, Susan Cloud proxy,
 * SuperMemory, Supabase RAG, and desktop tunnel fallback.
 */

interface Env {
  DB: D1Database;
  AI: Ai;
  JAKE_STATE: R2Bucket;
  JAKE_CACHE: KVNamespace;
  ENVIRONMENT: string;
  JAKE_VERSION: string;
  SUPERMEMORY_API_KEY: string;
  SUPABASE_URL: string;
  SUPABASE_ANON_KEY: string;
  SUSAN_CLOUD_URL: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const CORS: Record<string, string> = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}

function err(message: string, status = 400): Response {
  return json({ error: message }, status);
}

function id(): string {
  return crypto.randomUUID();
}

async function body(request: Request): Promise<Record<string, unknown>> {
  try {
    return (await request.json()) as Record<string, unknown>;
  } catch {
    return {};
  }
}

/** Simple path matcher — returns params or null */
function match(
  pathname: string,
  pattern: string
): Record<string, string> | null {
  const patternParts = pattern.split('/');
  const pathParts = pathname.split('/');
  if (patternParts.length !== pathParts.length) return null;
  const params: Record<string, string> = {};
  for (let i = 0; i < patternParts.length; i++) {
    if (patternParts[i].startsWith(':')) {
      params[patternParts[i].slice(1)] = pathParts[i];
    } else if (patternParts[i] !== pathParts[i]) {
      return null;
    }
  }
  return params;
}

// ---------------------------------------------------------------------------
// Route handler type
// ---------------------------------------------------------------------------

type Handler = (
  request: Request,
  env: Env,
  params: Record<string, string>
) => Promise<Response>;

interface Route {
  method: string;
  pattern: string;
  handler: Handler;
}

// ---------------------------------------------------------------------------
// Route definitions
// ---------------------------------------------------------------------------

function routes(): Route[] {
  return [
    // ===== Legacy / core endpoints =====
    { method: 'GET', pattern: '/', handler: handleApiInfo },
    { method: 'GET', pattern: '/api', handler: handleApiInfo },
    { method: 'GET', pattern: '/health', handler: handleHealth },
    { method: 'GET', pattern: '/tunnel/status', handler: handleTunnelStatus },
    { method: 'POST', pattern: '/memory/search', handler: handleMemorySearch },
    { method: 'POST', pattern: '/rag/query', handler: handleRagQuery },
    { method: 'GET', pattern: '/oracle/brief', handler: handleOracleBrief },
    { method: 'GET', pattern: '/oracle/signals', handler: handleOracleSignals },

    // ===== D1-backed CRUD — Goals =====
    { method: 'GET', pattern: '/goals', handler: handleGoalsList },
    { method: 'POST', pattern: '/goals', handler: handleGoalsCreate },
    { method: 'GET', pattern: '/goals/:id', handler: handleGoalsGet },
    { method: 'PUT', pattern: '/goals/:id', handler: handleGoalsUpdate },
    { method: 'DELETE', pattern: '/goals/:id', handler: handleGoalsDelete },
    { method: 'POST', pattern: '/goals/:id/decompose', handler: handleGoalsDecompose },

    // ===== D1-backed CRUD — Tasks =====
    { method: 'GET', pattern: '/tasks', handler: handleTasksList },
    { method: 'POST', pattern: '/tasks', handler: handleTasksCreate },
    { method: 'GET', pattern: '/tasks/next', handler: handleTasksNext },
    { method: 'PUT', pattern: '/tasks/:id', handler: handleTasksUpdate },
    { method: 'POST', pattern: '/tasks/:id/complete', handler: handleTasksComplete },
    { method: 'POST', pattern: '/tasks/:id/fail', handler: handleTasksFail },

    // ===== D1-backed CRUD — Briefs =====
    { method: 'GET', pattern: '/briefs', handler: handleBriefsList },
    { method: 'POST', pattern: '/briefs', handler: handleBriefsCreate },
    { method: 'GET', pattern: '/briefs/today', handler: handleBriefsToday },
    { method: 'GET', pattern: '/briefs/latest/:type', handler: handleBriefsLatest },

    // ===== D1-backed — Growth & Scrape =====
    { method: 'GET', pattern: '/growth', handler: handleGrowthList },
    { method: 'GET', pattern: '/growth/weekly', handler: handleGrowthWeekly },
    { method: 'GET', pattern: '/scrape-queue', handler: handleScrapeQueueList },
    { method: 'POST', pattern: '/scrape-queue', handler: handleScrapeQueueCreate },

    // ===== System status =====
    { method: 'GET', pattern: '/status', handler: handleStatus },

    // ===== Susan Cloud proxy =====
    { method: 'POST', pattern: '/susan/route', handler: susanProxy },
    { method: 'GET', pattern: '/susan/agents', handler: susanProxy },
    { method: 'POST', pattern: '/susan/foundry', handler: susanProxy },
    { method: 'POST', pattern: '/susan/rag/query', handler: susanProxy },
    { method: 'POST', pattern: '/susan/ingest', handler: susanProxy },
    { method: 'GET', pattern: '/susan/oracle/status', handler: susanProxy },
    { method: 'GET', pattern: '/susan/oracle/battlecard/:competitor', handler: susanProxy },
    { method: 'POST', pattern: '/susan/research/gaps', handler: susanProxy },
    { method: 'GET', pattern: '/susan/memory/stats', handler: susanProxy },
    { method: 'POST', pattern: '/susan/evolve/propose', handler: susanProxy },

    // ===== Workers AI =====
    { method: 'POST', pattern: '/ai/classify', handler: handleAiClassify },
    { method: 'POST', pattern: '/ai/summarize', handler: handleAiSummarize },
    { method: 'POST', pattern: '/ai/embed', handler: handleAiEmbed },
  ];
}

// ---------------------------------------------------------------------------
// Core / legacy handlers
// ---------------------------------------------------------------------------

const handleHealth: Handler = async (_req, env) => {
  return json({
    status: 'ok',
    version: env.JAKE_VERSION,
    environment: env.ENVIRONMENT,
    timestamp: new Date().toISOString(),
    gateway: 'jakestudio.ai',
    architecture: 'v20',
    layers: {
      cloudflare: 'active',
      d1: env.DB ? 'configured' : 'missing',
      ai: env.AI ? 'configured' : 'missing',
      r2: env.JAKE_STATE ? 'configured' : 'missing',
      kv: env.JAKE_CACHE ? 'configured' : 'missing',
      supabase: env.SUPABASE_URL ? 'configured' : 'missing',
      supermemory: env.SUPERMEMORY_API_KEY ? 'configured' : 'missing',
      susan_cloud: env.SUSAN_CLOUD_URL ? 'configured' : 'missing',
    },
  });
};

const handleApiInfo: Handler = async (_req, env) => {
  return json({
    name: 'Jake Gateway',
    company: 'JakeStudio',
    domain: 'jakestudio.ai',
    version: env.JAKE_VERSION,
    architecture: 'v20',
    departments: ['oracle-health', 'startup-intelligence-os'],
    endpoints: {
      health: '/health',
      api: '/api',
      status: '/status',
      tunnel: '/tunnel/status',
      memory: '/memory/search',
      rag: '/rag/query',
      oracle: '/oracle/brief',
      oracle_signals: '/oracle/signals',
      goals: '/goals',
      tasks: '/tasks',
      briefs: '/briefs',
      growth: '/growth',
      scrape_queue: '/scrape-queue',
      ai_classify: '/ai/classify',
      ai_summarize: '/ai/summarize',
      ai_embed: '/ai/embed',
      susan_route: '/susan/route',
      susan_agents: '/susan/agents',
      susan_foundry: '/susan/foundry',
      susan_rag: '/susan/rag/query',
    },
  });
};

const handleTunnelStatus: Handler = async () => {
  try {
    await fetch('http://jake-desktop.jakestudio.ai:7841/health', {
      signal: AbortSignal.timeout(3000),
    });
    return json({ desktop: 'online', tunnelLatency: 'ok' });
  } catch {
    return json({
      desktop: 'offline',
      message: 'Desktop tunnel not reachable — cloud-only mode active',
    });
  }
};

const handleMemorySearch: Handler = async (req, env) => {
  const b = await body(req);
  const searchResponse = await fetch('https://api.supermemory.ai/v4/search', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.SUPERMEMORY_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      q: b.query || b.q,
      containerTag: b.containerTag || 'jake-system',
      limit: b.limit || 10,
    }),
  });
  const results = await searchResponse.json();
  return json(results);
};

const handleRagQuery: Handler = async (req, env) => {
  const b = await body(req);
  const query = (b.query || b.q) as string;
  const domain = (b.domain || 'oracle_health_intelligence') as string;
  const limit = (b.limit || 10) as number;

  const ragResponse = await fetch(
    `${env.SUPABASE_URL}/rest/v1/rpc/match_documents`,
    {
      method: 'POST',
      headers: {
        apikey: env.SUPABASE_ANON_KEY,
        Authorization: `Bearer ${env.SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query_text: query,
        match_count: limit,
        filter_domain: domain,
      }),
    }
  );

  if (!ragResponse.ok) {
    const fallbackResponse = await fetch(
      `${env.SUPABASE_URL}/rest/v1/knowledge_chunks?content=ilike.*${encodeURIComponent(query)}*&company_id=eq.oracle-health-ai-enablement&limit=${limit}&order=created_at.desc`,
      {
        headers: {
          apikey: env.SUPABASE_ANON_KEY,
          Authorization: `Bearer ${env.SUPABASE_ANON_KEY}`,
        },
      }
    );
    const fallbackResults = await fallbackResponse.json();
    return json({ results: fallbackResults, method: 'text_search' });
  }

  const results = await ragResponse.json();
  return json({ results, method: 'vector_search' });
};

const handleOracleBrief: Handler = async (_req, env) => {
  const briefResponse = await fetch(
    `${env.SUPABASE_URL}/rest/v1/knowledge_chunks?select=id,content,data_type,source,created_at&company_id=eq.oracle-health-ai-enablement&data_type=eq.executive_brief&order=created_at.desc&limit=1`,
    {
      headers: {
        apikey: env.SUPABASE_ANON_KEY,
        Authorization: `Bearer ${env.SUPABASE_ANON_KEY}`,
      },
    }
  );
  const brief = await briefResponse.json();
  return json({ brief, department: 'oracle_health' });
};

const handleOracleSignals: Handler = async (req, env) => {
  const url = new URL(req.url);
  const days = url.searchParams.get('days') || '7';
  const since = new Date(
    Date.now() - parseInt(days) * 86400000
  ).toISOString();

  const signalsResponse = await fetch(
    `${env.SUPABASE_URL}/rest/v1/knowledge_chunks?select=id,content,data_type,source,created_at&company_id=eq.oracle-health-ai-enablement&data_type=in.(competitive_signal,market_signal,market_research,studio_memory)&created_at=gte.${since}&order=created_at.desc&limit=20`,
    {
      headers: {
        apikey: env.SUPABASE_ANON_KEY,
        Authorization: `Bearer ${env.SUPABASE_ANON_KEY}`,
      },
    }
  );
  const signals = await signalsResponse.json();
  return json({ signals, days_back: parseInt(days) });
};

// ---------------------------------------------------------------------------
// D1 — Goals
// ---------------------------------------------------------------------------

const handleGoalsList: Handler = async (req, env) => {
  const url = new URL(req.url);
  const status = url.searchParams.get('status');
  const category = url.searchParams.get('category');
  const company = url.searchParams.get('company');

  let sql = 'SELECT * FROM goals WHERE 1=1';
  const params: unknown[] = [];
  if (status) { sql += ' AND status = ?'; params.push(status); }
  if (category) { sql += ' AND category = ?'; params.push(category); }
  if (company) { sql += ' AND company = ?'; params.push(company); }
  sql += ' ORDER BY updated_at DESC';

  const { results } = await env.DB.prepare(sql).bind(...params).all();
  return json({ goals: results });
};

const handleGoalsCreate: Handler = async (req, env) => {
  const b = await body(req);
  if (!b.title || !b.category || !b.target) {
    return err('title, category, and target are required');
  }
  const goalId = id();
  await env.DB.prepare(
    `INSERT INTO goals (id, title, category, company, target, current_value, target_value, cadence, status, notion_page_id)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(
      goalId,
      b.title as string,
      b.category as string,
      (b.company as string) || null,
      b.target as string,
      (b.current_value as number) ?? 0,
      (b.target_value as number) ?? 100,
      (b.cadence as string) || 'weekly',
      (b.status as string) || 'active',
      (b.notion_page_id as string) || null
    )
    .run();

  await logEvent(env, 'goal.created', 'gateway', { goalId, title: b.title });

  const { results } = await env.DB.prepare('SELECT * FROM goals WHERE id = ?').bind(goalId).all();
  return json({ goal: results[0] }, 201);
};

const handleGoalsGet: Handler = async (_req, env, params) => {
  const { results } = await env.DB.prepare('SELECT * FROM goals WHERE id = ?').bind(params.id).all();
  if (!results.length) return err('Goal not found', 404);
  return json({ goal: results[0] });
};

const handleGoalsUpdate: Handler = async (req, env, params) => {
  const b = await body(req);
  const fields: string[] = [];
  const values: unknown[] = [];

  for (const key of ['title', 'category', 'company', 'target', 'current_value', 'target_value', 'cadence', 'status', 'notion_page_id']) {
    if (b[key] !== undefined) {
      fields.push(`${key} = ?`);
      values.push(b[key]);
    }
  }
  if (!fields.length) return err('No fields to update');

  fields.push("updated_at = datetime('now')");
  values.push(params.id);

  await env.DB.prepare(`UPDATE goals SET ${fields.join(', ')} WHERE id = ?`).bind(...values).run();
  await logEvent(env, 'goal.updated', 'gateway', { goalId: params.id });

  const { results } = await env.DB.prepare('SELECT * FROM goals WHERE id = ?').bind(params.id).all();
  return json({ goal: results[0] });
};

const handleGoalsDelete: Handler = async (_req, env, params) => {
  await env.DB.prepare('DELETE FROM goals WHERE id = ?').bind(params.id).run();
  await logEvent(env, 'goal.deleted', 'gateway', { goalId: params.id });
  return json({ deleted: true, id: params.id });
};

const handleGoalsDecompose: Handler = async (req, env, params) => {
  const { results: goalRows } = await env.DB.prepare('SELECT * FROM goals WHERE id = ?').bind(params.id).all();
  if (!goalRows.length) return err('Goal not found', 404);
  const goal = goalRows[0] as Record<string, unknown>;

  // Use Workers AI to decompose goal into tasks
  const prompt = `You are Jake, an AI startup operator. Decompose this goal into 3-7 concrete, actionable tasks.

Goal: ${goal.title}
Target: ${goal.target}
Category: ${goal.category}
Company: ${goal.company || 'general'}

Return a JSON array of tasks. Each task should have:
- title (string, actionable verb phrase)
- description (string, 1-2 sentences)
- priority (P0/P1/P2/P3)
- executor (jake/mike/susan/agent)
- requires_gpu (boolean)
- requires_mike (boolean)

Return ONLY the JSON array, no other text.`;

  const aiResult = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
    prompt,
    max_tokens: 1024,
  }) as { response?: string };

  let tasks: Array<Record<string, unknown>> = [];
  try {
    const raw = (aiResult.response || '').trim();
    // Extract JSON array from response
    const arrayMatch = raw.match(/\[[\s\S]*\]/);
    if (arrayMatch) {
      tasks = JSON.parse(arrayMatch[0]);
    }
  } catch {
    return err('AI decomposition failed to produce valid JSON — try again', 500);
  }

  // Insert tasks into D1
  const createdTasks: unknown[] = [];
  for (const task of tasks) {
    const taskId = id();
    await env.DB.prepare(
      `INSERT INTO tasks (id, goal_id, title, description, priority, executor, requires_gpu, requires_mike, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'queued')`
    )
      .bind(
        taskId,
        params.id,
        task.title as string,
        (task.description as string) || null,
        (task.priority as string) || 'P2',
        (task.executor as string) || 'jake',
        task.requires_gpu ? 1 : 0,
        task.requires_mike ? 1 : 0
      )
      .run();
    createdTasks.push({ id: taskId, ...task });
  }

  await logEvent(env, 'goal.decomposed', 'gateway', {
    goalId: params.id,
    tasksCreated: createdTasks.length,
  });

  return json({ goal, tasks: createdTasks }, 201);
};

// ---------------------------------------------------------------------------
// D1 — Tasks
// ---------------------------------------------------------------------------

const handleTasksList: Handler = async (req, env) => {
  const url = new URL(req.url);
  const status = url.searchParams.get('status');
  const executor = url.searchParams.get('executor');
  const goalId = url.searchParams.get('goal_id');
  const priority = url.searchParams.get('priority');

  let sql = 'SELECT * FROM tasks WHERE 1=1';
  const params: unknown[] = [];
  if (status) { sql += ' AND status = ?'; params.push(status); }
  if (executor) { sql += ' AND executor = ?'; params.push(executor); }
  if (goalId) { sql += ' AND goal_id = ?'; params.push(goalId); }
  if (priority) { sql += ' AND priority = ?'; params.push(priority); }
  sql += ' ORDER BY created_at DESC';

  const { results } = await env.DB.prepare(sql).bind(...params).all();
  return json({ tasks: results });
};

const handleTasksCreate: Handler = async (req, env) => {
  const b = await body(req);
  if (!b.title) return err('title is required');
  const taskId = id();
  await env.DB.prepare(
    `INSERT INTO tasks (id, goal_id, title, description, priority, executor, requires_gpu, requires_mike, tool, scheduled_for, status)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(
      taskId,
      (b.goal_id as string) || null,
      b.title as string,
      (b.description as string) || null,
      (b.priority as string) || 'P2',
      (b.executor as string) || 'jake',
      b.requires_gpu ? 1 : 0,
      b.requires_mike ? 1 : 0,
      (b.tool as string) || null,
      (b.scheduled_for as string) || null,
      (b.status as string) || 'queued'
    )
    .run();

  await logEvent(env, 'task.created', 'gateway', { taskId, title: b.title });

  const { results } = await env.DB.prepare('SELECT * FROM tasks WHERE id = ?').bind(taskId).all();
  return json({ task: results[0] }, 201);
};

const handleTasksNext: Handler = async (req, env) => {
  const url = new URL(req.url);
  const executor = url.searchParams.get('executor') || 'jake';
  const requiresGpu = url.searchParams.get('requires_gpu') || '0';

  const { results } = await env.DB.prepare(
    `SELECT * FROM tasks
     WHERE status = 'queued'
       AND executor = ?
       AND requires_gpu <= ?
     ORDER BY
       CASE priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 ELSE 3 END,
       created_at ASC
     LIMIT 1`
  )
    .bind(executor, parseInt(requiresGpu))
    .all();

  if (!results.length) return json({ task: null, message: 'No queued tasks for this executor' });
  return json({ task: results[0] });
};

const handleTasksUpdate: Handler = async (req, env, params) => {
  const b = await body(req);
  const fields: string[] = [];
  const values: unknown[] = [];

  for (const key of ['goal_id', 'title', 'description', 'priority', 'executor', 'status', 'requires_gpu', 'requires_mike', 'tool', 'result', 'artifact_url', 'scheduled_for', 'error']) {
    if (b[key] !== undefined) {
      fields.push(`${key} = ?`);
      values.push(b[key]);
    }
  }
  if (!fields.length) return err('No fields to update');
  values.push(params.id);

  await env.DB.prepare(`UPDATE tasks SET ${fields.join(', ')} WHERE id = ?`).bind(...values).run();

  const { results } = await env.DB.prepare('SELECT * FROM tasks WHERE id = ?').bind(params.id).all();
  return json({ task: results[0] });
};

const handleTasksComplete: Handler = async (req, env, params) => {
  const b = await body(req);
  await env.DB.prepare(
    `UPDATE tasks SET status = 'done', result = ?, artifact_url = ?, completed_at = datetime('now') WHERE id = ?`
  )
    .bind(
      (b.result as string) || null,
      (b.artifact_url as string) || null,
      params.id
    )
    .run();

  await logEvent(env, 'task.completed', 'gateway', { taskId: params.id });

  const { results } = await env.DB.prepare('SELECT * FROM tasks WHERE id = ?').bind(params.id).all();
  return json({ task: results[0] });
};

const handleTasksFail: Handler = async (req, env, params) => {
  const b = await body(req);
  await env.DB.prepare(
    `UPDATE tasks SET status = 'failed', error = ?, completed_at = datetime('now') WHERE id = ?`
  )
    .bind((b.error as string) || 'Unknown error', params.id)
    .run();

  await logEvent(env, 'task.failed', 'gateway', { taskId: params.id, error: b.error });

  const { results } = await env.DB.prepare('SELECT * FROM tasks WHERE id = ?').bind(params.id).all();
  return json({ task: results[0] });
};

// ---------------------------------------------------------------------------
// D1 — Briefs
// ---------------------------------------------------------------------------

const handleBriefsList: Handler = async (req, env) => {
  const url = new URL(req.url);
  const type = url.searchParams.get('type');
  const limit = parseInt(url.searchParams.get('limit') || '20');

  let sql = 'SELECT * FROM briefs WHERE 1=1';
  const params: unknown[] = [];
  if (type) { sql += ' AND type = ?'; params.push(type); }
  sql += ' ORDER BY created_at DESC LIMIT ?';
  params.push(limit);

  const { results } = await env.DB.prepare(sql).bind(...params).all();
  return json({ briefs: results });
};

const handleBriefsCreate: Handler = async (req, env) => {
  const b = await body(req);
  if (!b.type || !b.content) return err('type and content are required');
  const briefId = id();
  await env.DB.prepare(
    `INSERT INTO briefs (id, type, content, goals_snapshot, tasks_completed, tasks_blocked, highlights, needs_mike, sent_via)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(
      briefId,
      b.type as string,
      b.content as string,
      (b.goals_snapshot as string) || null,
      (b.tasks_completed as number) ?? 0,
      (b.tasks_blocked as number) ?? 0,
      (b.highlights as string) || null,
      (b.needs_mike as string) || null,
      (b.sent_via as string) || null
    )
    .run();

  await logEvent(env, 'brief.created', 'gateway', { briefId, type: b.type });

  const { results } = await env.DB.prepare('SELECT * FROM briefs WHERE id = ?').bind(briefId).all();
  return json({ brief: results[0] }, 201);
};

const handleBriefsToday: Handler = async (_req, env) => {
  const today = new Date().toISOString().split('T')[0];
  const { results } = await env.DB.prepare(
    "SELECT * FROM briefs WHERE created_at >= ? ORDER BY created_at DESC"
  )
    .bind(today)
    .all();
  return json({ briefs: results, date: today });
};

const handleBriefsLatest: Handler = async (_req, env, params) => {
  const { results } = await env.DB.prepare(
    'SELECT * FROM briefs WHERE type = ? ORDER BY created_at DESC LIMIT 1'
  )
    .bind(params.type)
    .all();
  if (!results.length) return json({ brief: null, message: `No briefs of type '${params.type}' found` });
  return json({ brief: results[0] });
};

// ---------------------------------------------------------------------------
// D1 — Growth & Scrape Queue
// ---------------------------------------------------------------------------

const handleGrowthList: Handler = async (req, env) => {
  const url = new URL(req.url);
  const domain = url.searchParams.get('domain');
  const limit = parseInt(url.searchParams.get('limit') || '50');

  let sql = 'SELECT * FROM capability_growth WHERE 1=1';
  const params: unknown[] = [];
  if (domain) { sql += ' AND domain = ?'; params.push(domain); }
  sql += ' ORDER BY week_start DESC LIMIT ?';
  params.push(limit);

  const { results } = await env.DB.prepare(sql).bind(...params).all();
  return json({ growth: results });
};

const handleGrowthWeekly: Handler = async (_req, env) => {
  const { results } = await env.DB.prepare(
    `SELECT domain, agent_group,
            SUM(chunks_after - chunks_before) as total_chunks_added,
            AVG(quality_score) as avg_quality,
            SUM(sources_scraped) as total_sources,
            week_start
     FROM capability_growth
     GROUP BY week_start, domain
     ORDER BY week_start DESC
     LIMIT 20`
  ).all();
  return json({ weekly: results });
};

const handleScrapeQueueList: Handler = async (req, env) => {
  const url = new URL(req.url);
  const status = url.searchParams.get('status');
  const domain = url.searchParams.get('domain');

  let sql = 'SELECT * FROM scrape_queue WHERE 1=1';
  const params: unknown[] = [];
  if (status) { sql += ' AND status = ?'; params.push(status); }
  if (domain) { sql += ' AND domain = ?'; params.push(domain); }
  sql += ' ORDER BY created_at DESC LIMIT 50';

  const { results } = await env.DB.prepare(sql).bind(...params).all();
  return json({ queue: results });
};

const handleScrapeQueueCreate: Handler = async (req, env) => {
  const b = await body(req);
  if (!b.url || !b.domain || !b.agent_group) {
    return err('url, domain, and agent_group are required');
  }
  const itemId = id();
  await env.DB.prepare(
    `INSERT INTO scrape_queue (id, url, domain, agent_group, priority, discovered_by)
     VALUES (?, ?, ?, ?, ?, ?)`
  )
    .bind(
      itemId,
      b.url as string,
      b.domain as string,
      b.agent_group as string,
      (b.priority as string) || 'P2',
      (b.discovered_by as string) || 'manual'
    )
    .run();

  await logEvent(env, 'scrape.queued', 'gateway', { itemId, url: b.url });

  const { results } = await env.DB.prepare('SELECT * FROM scrape_queue WHERE id = ?').bind(itemId).all();
  return json({ item: results[0] }, 201);
};

// ---------------------------------------------------------------------------
// System status dashboard
// ---------------------------------------------------------------------------

const handleStatus: Handler = async (_req, env) => {
  const [goalsResult, tasksResult, briefsResult, eventsResult] = await Promise.all([
    env.DB.prepare("SELECT status, COUNT(*) as count FROM goals GROUP BY status").all(),
    env.DB.prepare("SELECT status, COUNT(*) as count FROM tasks GROUP BY status").all(),
    env.DB.prepare("SELECT COUNT(*) as count FROM briefs WHERE created_at >= date('now')").all(),
    env.DB.prepare("SELECT COUNT(*) as count FROM events WHERE created_at >= datetime('now', '-1 hour')").all(),
  ]);

  // Check tunnel
  let desktopOnline = false;
  try {
    await fetch('http://jake-desktop.jakestudio.ai:7841/health', {
      signal: AbortSignal.timeout(2000),
    });
    desktopOnline = true;
  } catch { /* offline */ }

  return json({
    version: env.JAKE_VERSION,
    architecture: 'v20',
    timestamp: new Date().toISOString(),
    desktop: desktopOnline ? 'online' : 'offline',
    d1: {
      goals: goalsResult.results,
      tasks: tasksResult.results,
      briefs_today: (briefsResult.results[0] as Record<string, unknown>)?.count ?? 0,
      events_last_hour: (eventsResult.results[0] as Record<string, unknown>)?.count ?? 0,
    },
    bindings: {
      d1: !!env.DB,
      ai: !!env.AI,
      r2: !!env.JAKE_STATE,
      kv: !!env.JAKE_CACHE,
      supabase: !!env.SUPABASE_URL,
      supermemory: !!env.SUPERMEMORY_API_KEY,
      susan_cloud: !!env.SUSAN_CLOUD_URL,
    },
  });
};

// ---------------------------------------------------------------------------
// Susan Cloud proxy
// ---------------------------------------------------------------------------

const susanProxy: Handler = async (req, env) => {
  const url = new URL(req.url);
  // Strip /susan prefix to get the target path
  const targetPath = url.pathname.replace(/^\/susan/, '');
  const targetUrl = `${env.SUSAN_CLOUD_URL}${targetPath}${url.search}`;

  try {
    const proxyHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const init: RequestInit = {
      method: req.method,
      headers: proxyHeaders,
    };

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      init.body = req.body;
    }

    const response = await fetch(targetUrl, {
      ...init,
      signal: AbortSignal.timeout(30000),
    });

    const data = await response.json();
    return json({ source: 'susan-cloud', path: targetPath, data }, response.status);
  } catch (e) {
    return json(
      {
        error: 'Susan Cloud unreachable',
        target: targetUrl,
        message: e instanceof Error ? e.message : 'Unknown error',
      },
      502
    );
  }
};

// ---------------------------------------------------------------------------
// Workers AI
// ---------------------------------------------------------------------------

const handleAiClassify: Handler = async (req, env) => {
  const b = await body(req);
  if (!b.text) return err('text is required');

  const labels = (b.labels as string[]) || [
    'strategy', 'product', 'engineering', 'growth', 'research',
    'operations', 'finance', 'legal', 'hiring', 'other',
  ];

  const result = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
    prompt: `Classify the following text into exactly one of these categories: ${labels.join(', ')}

Text: ${b.text}

Return ONLY the category name, nothing else.`,
    max_tokens: 32,
  }) as { response?: string };

  const category = (result.response || 'other').trim().toLowerCase();
  return json({ text: b.text, category, labels });
};

const handleAiSummarize: Handler = async (req, env) => {
  const b = await body(req);
  if (!b.text) return err('text is required');

  const maxLength = (b.max_length as number) || 200;
  const style = (b.style as string) || 'concise';

  const result = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
    prompt: `Summarize the following text in a ${style} style. Keep it under ${maxLength} words.

Text: ${b.text}

Summary:`,
    max_tokens: 512,
  }) as { response?: string };

  return json({ summary: (result.response || '').trim(), style, original_length: (b.text as string).length });
};

const handleAiEmbed: Handler = async (req, env) => {
  const b = await body(req);
  if (!b.text) return err('text is required');

  const texts = Array.isArray(b.text) ? (b.text as string[]) : [b.text as string];

  const result = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
    text: texts,
  }) as { data?: number[][] };

  return json({
    embeddings: result.data || [],
    model: 'bge-base-en-v1.5',
    dimensions: result.data?.[0]?.length || 0,
    count: texts.length,
  });
};

// ---------------------------------------------------------------------------
// Event logging helper
// ---------------------------------------------------------------------------

async function logEvent(
  env: Env,
  type: string,
  source: string,
  data: unknown
): Promise<void> {
  try {
    await env.DB.prepare(
      'INSERT INTO events (id, type, source, data) VALUES (?, ?, ?, ?)'
    )
      .bind(id(), type, source, JSON.stringify(data))
      .run();
  } catch {
    // Non-critical — don't fail the request if event logging fails
  }
}

// ---------------------------------------------------------------------------
// Main fetch handler with router
// ---------------------------------------------------------------------------

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    const url = new URL(request.url);
    const pathname = url.pathname.replace(/\/$/, '') || '/';

    // Try each route
    for (const route of routes()) {
      if (route.method !== request.method) continue;
      const params = match(pathname, route.pattern);
      if (params !== null) {
        try {
          return await route.handler(request, env, params);
        } catch (e) {
          const message = e instanceof Error ? e.message : 'Internal error';
          return json({ error: message, route: route.pattern }, 500);
        }
      }
    }

    // Fallback: proxy to desktop tunnel
    try {
      const tunnelUrl = new URL(request.url);
      tunnelUrl.hostname = 'jake-desktop.jakestudio.ai';
      tunnelUrl.port = '7841';

      const proxyResponse = await fetch(
        new Request(tunnelUrl.toString(), {
          method: request.method,
          headers: request.headers,
          body: request.method !== 'GET' ? request.body : undefined,
        }),
        { signal: AbortSignal.timeout(10000) }
      );

      return proxyResponse;
    } catch {
      return json(
        {
          error: 'Not found',
          message:
            "No matching route and desktop tunnel is offline. Use /api to see available endpoints.",
          hint: 'Start the desktop and Cloudflare Tunnel to enable full functionality',
        },
        404
      );
    }
  },
} satisfies ExportedHandler<Env>;
