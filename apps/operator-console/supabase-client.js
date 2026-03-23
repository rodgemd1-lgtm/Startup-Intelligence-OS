/**
 * Supabase client for Jake Ops Dashboard.
 * LOCAL TOOL ONLY — service key is acceptable for localhost use.
 * Never expose this file publicly.
 */

const SUPABASE_URL = 'https://zqsdadnnpgqhehqxplio.supabase.co';
// Service key — read-only queries only in this dashboard
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpxc2RhZG5ucGdxaGVocXhwbGlvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjgyNTUyNSwiZXhwIjoyMDg4NDAxNTI1fQ.9l4vu1zz-pW6GlhPhk8sRTcWGUvQcN3LGXy1jnKDAzk';

/** Generic Supabase REST query helper */
async function sbQuery(table, params = '') {
  const url = `${SUPABASE_URL}/rest/v1/${table}${params ? '?' + params : ''}`;
  const res = await fetch(url, {
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
    },
  });
  if (!res.ok) throw new Error(`${table}: ${res.status} ${res.statusText}`);
  return res.json();
}

/** Generic Supabase REST insert helper */
async function sbInsert(table, row) {
  const url = `${SUPABASE_URL}/rest/v1/${table}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
    },
    body: JSON.stringify(row),
  });
  if (!res.ok) throw new Error(`${table} insert: ${res.status} ${res.statusText}`);
  return res.json();
}

/** Generic Supabase REST update helper */
async function sbUpdate(table, id, updates) {
  const url = `${SUPABASE_URL}/rest/v1/${table}?id=eq.${id}`;
  const res = await fetch(url, {
    method: 'PATCH',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
    },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error(`${table} update: ${res.status} ${res.statusText}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Panel data fetchers
// ---------------------------------------------------------------------------

/** Panel 1: Task Board */
async function fetchTasks() {
  return sbQuery('jake_tasks', 'select=id,title,status,priority,assignee,created_at&order=created_at.desc&limit=50');
}

/** Panel 2: Brain Stats */
async function fetchBrainStats() {
  const [episodic, semantic, procedural, working, entities, relationships] = await Promise.allSettled([
    sbQuery('jake_episodic', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_episodic', 'select=count')),
    sbQuery('jake_semantic', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_semantic', 'select=count')),
    sbQuery('jake_procedural', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_procedural', 'select=count')),
    sbQuery('jake_working', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_working', 'select=count')),
    sbQuery('jake_entities', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_entities', 'select=count')),
    sbQuery('jake_relationships', 'select=id&limit=1&head=true').catch(() =>
      sbQuery('jake_relationships', 'select=count')),
  ]);
  // Get actual counts via select=*&limit with count headers
  const [epiCount, semCount, proCount, wrkCount, entCount, relCount] = await Promise.all([
    getCount('jake_episodic'),
    getCount('jake_semantic'),
    getCount('jake_procedural'),
    getCount('jake_working'),
    getCount('jake_entities'),
    getCount('jake_relationships'),
  ]);
  // Get last consolidation — most recent semantic created_at
  const lastSemantic = await sbQuery('jake_semantic', 'select=created_at&order=created_at.desc&limit=1').catch(() => []);
  return {
    episodic: epiCount,
    semantic: semCount,
    procedural: proCount,
    working: wrkCount,
    entities: entCount,
    relationships: relCount,
    lastConsolidation: lastSemantic[0]?.created_at || null,
  };
}

async function getCount(table) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?select=id`, {
    method: 'HEAD',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Prefer': 'count=exact',
    },
  });
  const countHeader = res.headers.get('content-range');
  if (countHeader) {
    const match = countHeader.match(/\/(\d+)/);
    if (match) return parseInt(match[1], 10);
  }
  return '?';
}

/** Panel 3: Agent Activity Log */
async function fetchActivityLog() {
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  return sbQuery('jake_episodic',
    `select=id,content,source,data_type,created_at&order=created_at.desc&limit=30&created_at=gte.${since}`
  ).catch(() =>
    sbQuery('jake_episodic', 'select=id,content,source,data_type,created_at&order=created_at.desc&limit=30')
  );
}

/** Panel 4: Cron Health */
async function fetchCronHealth() {
  // Try jake_cron_status table first (may not exist yet)
  try {
    return await sbQuery('jake_cron_status',
      'select=job_name,last_run,status,next_run,error_message&order=last_run.desc&limit=20'
    );
  } catch (e) {
    // Fall back to episodic entries with data_type matching cron runs
    const rows = await sbQuery('jake_episodic',
      `select=source,data_type,created_at,metadata&data_type=in.(self_improvement_run,research_daemon_run,collective_run,cron_run)&order=created_at.desc&limit=10`
    ).catch(() => []);
    return rows.map(r => ({
      job_name: r.source || r.data_type,
      last_run: r.created_at,
      status: r.metadata?.success ? 'ok' : 'error',
      next_run: null,
      error_message: r.metadata?.error || null,
    }));
  }
}

/** Panel 5: Goals Tracker */
async function fetchGoals() {
  return sbQuery('jake_goals',
    'select=id,title,status,target_value,current_value,deadline,priority&order=priority.asc,created_at.desc&limit=20'
  ).catch(() => []);
}

/** Panel 6 (Phase 4): Pipeline Runs */
async function fetchPipelineRuns() {
  try {
    return await sbQuery('jake_pipeline_runs',
      'select=id,pipeline_name,started_at,current_phase,status,completed_at,error_log&order=started_at.desc&limit=10'
    );
  } catch (e) {
    return [];
  }
}
