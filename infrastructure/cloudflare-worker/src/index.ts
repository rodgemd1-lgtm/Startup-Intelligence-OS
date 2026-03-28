/**
 * Jake Gateway — Cloudflare Worker (V15)
 *
 * Edge gateway for JakeStudio.ai
 * Routes requests to Jake's local OpenClaw runtime via Cloudflare Tunnel
 * Provides always-on availability even when desktop is offline (graceful fallback)
 * Direct Supabase access for RAG queries when desktop is asleep
 */

interface Env {
  JAKE_STATE: R2Bucket;
  JAKE_CACHE: KVNamespace;
  ENVIRONMENT: string;
  JAKE_VERSION: string;
  SUPERMEMORY_API_KEY: string;
  SUPABASE_URL: string;
  SUPABASE_ANON_KEY: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // CORS headers for cross-origin access
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Health check endpoint
    if (url.pathname === '/health') {
      return Response.json({
        status: 'ok',
        version: env.JAKE_VERSION,
        environment: env.ENVIRONMENT,
        timestamp: new Date().toISOString(),
        gateway: 'jakestudio.ai',
        layers: {
          cloudflare: 'active',
          supabase: env.SUPABASE_URL ? 'configured' : 'missing',
          supermemory: env.SUPERMEMORY_API_KEY ? 'configured' : 'missing',
        },
      }, { headers: corsHeaders });
    }

    // API info endpoint
    if (url.pathname === '/' || url.pathname === '/api') {
      return Response.json({
        name: 'Jake Gateway',
        company: 'JakeStudio',
        domain: 'jakestudio.ai',
        version: env.JAKE_VERSION,
        departments: ['oracle-health', 'startup-intelligence-os'],
        endpoints: {
          health: '/health',
          api: '/api',
          tunnel: '/tunnel/status',
          memory: '/memory/search',
          rag: '/rag/query',
          oracle: '/oracle/brief',
          oracle_signals: '/oracle/signals',
        },
      }, { headers: corsHeaders });
    }

    // Tunnel status — check if desktop is reachable
    if (url.pathname === '/tunnel/status') {
      try {
        const tunnelResponse = await fetch('http://jake-desktop.jakestudio.ai:7841/health', {
          signal: AbortSignal.timeout(3000),
        });
        return Response.json({
          desktop: 'online',
          tunnelLatency: 'ok',
        }, { headers: corsHeaders });
      } catch {
        return Response.json({
          desktop: 'offline',
          message: 'Desktop tunnel not reachable — cloud-only mode active',
        }, { headers: corsHeaders });
      }
    }

    // SuperMemory proxy — search Jake's memory
    if (url.pathname === '/memory/search' && request.method === 'POST') {
      const body = await request.json() as Record<string, unknown>;
      const searchResponse = await fetch('https://api.supermemory.ai/v4/search', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.SUPERMEMORY_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          q: body.query || body.q,
          containerTag: body.containerTag || 'jake-system',
          limit: body.limit || 10,
        }),
      });
      const results = await searchResponse.json();
      return Response.json(results, { headers: corsHeaders });
    }

    // --- Oracle Health Department Endpoints (always-on, cloud-native) ---

    // RAG query — direct Supabase vector search (works when desktop is asleep)
    if (url.pathname === '/rag/query' && request.method === 'POST') {
      const body = await request.json() as Record<string, unknown>;
      const query = (body.query || body.q) as string;
      const domain = (body.domain || 'oracle_health_intelligence') as string;
      const limit = (body.limit || 10) as number;

      // Query Supabase RAG via PostgREST
      const ragResponse = await fetch(
        `${env.SUPABASE_URL}/rest/v1/rpc/match_documents`,
        {
          method: 'POST',
          headers: {
            'apikey': env.SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${env.SUPABASE_ANON_KEY}`,
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
        // Fallback: simple text search if vector function not available
        const fallbackResponse = await fetch(
          `${env.SUPABASE_URL}/rest/v1/susan_chunks?content=ilike.*${encodeURIComponent(query)}*&domain=eq.${domain}&limit=${limit}&order=created_at.desc`,
          {
            headers: {
              'apikey': env.SUPABASE_ANON_KEY,
              'Authorization': `Bearer ${env.SUPABASE_ANON_KEY}`,
            },
          }
        );
        const fallbackResults = await fallbackResponse.json();
        return Response.json({ results: fallbackResults, method: 'text_search' }, { headers: corsHeaders });
      }

      const results = await ragResponse.json();
      return Response.json({ results, method: 'vector_search' }, { headers: corsHeaders });
    }

    // Oracle Health brief — get latest intelligence
    if (url.pathname === '/oracle/brief') {
      const briefResponse = await fetch(
        `${env.SUPABASE_URL}/rest/v1/susan_chunks?domain=eq.oracle_health_intelligence&data_type=eq.executive_brief&order=created_at.desc&limit=1`,
        {
          headers: {
            'apikey': env.SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${env.SUPABASE_ANON_KEY}`,
          },
        }
      );
      const brief = await briefResponse.json();
      return Response.json({ brief, department: 'oracle_health' }, { headers: corsHeaders });
    }

    // Oracle Health signals — get recent competitive signals
    if (url.pathname === '/oracle/signals') {
      const days = url.searchParams.get('days') || '7';
      const since = new Date(Date.now() - parseInt(days) * 86400000).toISOString();

      const signalsResponse = await fetch(
        `${env.SUPABASE_URL}/rest/v1/susan_chunks?domain=eq.oracle_health_intelligence&data_type=in.(competitive_signal,market_signal)&created_at=gte.${since}&order=created_at.desc&limit=20`,
        {
          headers: {
            'apikey': env.SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${env.SUPABASE_ANON_KEY}`,
          },
        }
      );
      const signals = await signalsResponse.json();
      return Response.json({ signals, days_back: parseInt(days) }, { headers: corsHeaders });
    }

    // Default: proxy to desktop OpenClaw via tunnel (when online)
    try {
      const tunnelUrl = new URL(request.url);
      tunnelUrl.hostname = 'jake-desktop.jakestudio.ai';
      tunnelUrl.port = '7841';

      const proxyResponse = await fetch(new Request(tunnelUrl.toString(), {
        method: request.method,
        headers: request.headers,
        body: request.method !== 'GET' ? request.body : undefined,
      }), {
        signal: AbortSignal.timeout(10000),
      });

      return proxyResponse;
    } catch {
      return Response.json({
        error: 'Desktop offline',
        message: 'Jake\'s local runtime is not available. Cloud-only endpoints: /health, /api, /memory/search, /rag/query, /oracle/brief, /oracle/signals',
        hint: 'Start the desktop and Cloudflare Tunnel to enable full functionality',
      }, { status: 503, headers: corsHeaders });
    }
  },
} satisfies ExportedHandler<Env>;
