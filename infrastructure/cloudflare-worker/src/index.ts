/**
 * Jake Gateway — Cloudflare Worker
 *
 * Edge gateway for JakeStudio.ai
 * Routes requests to Jake's local OpenClaw runtime via Cloudflare Tunnel
 * Provides always-on availability even when desktop is offline (graceful fallback)
 */

interface Env {
  JAKE_STATE: R2Bucket;
  JAKE_CACHE: KVNamespace;
  ENVIRONMENT: string;
  JAKE_VERSION: string;
  SUPERMEMORY_API_KEY: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Health check endpoint
    if (url.pathname === '/health') {
      return Response.json({
        status: 'ok',
        version: env.JAKE_VERSION,
        environment: env.ENVIRONMENT,
        timestamp: new Date().toISOString(),
        gateway: 'jakestudio.ai',
      });
    }

    // API info endpoint
    if (url.pathname === '/' || url.pathname === '/api') {
      return Response.json({
        name: 'Jake Gateway',
        company: 'JakeStudio',
        domain: 'jakestudio.ai',
        divisions: ['oracle-health', 'startup-intelligence-os'],
        version: env.JAKE_VERSION,
        endpoints: {
          health: '/health',
          api: '/api',
          tunnel: '/tunnel/status',
          memory: '/memory/search',
        },
      });
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
        });
      } catch {
        return Response.json({
          desktop: 'offline',
          message: 'Desktop tunnel not reachable — cloud-only mode active',
        });
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
      return Response.json(results);
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
        message: 'Jake\'s local runtime is not available. Cloud-only endpoints: /health, /api, /memory/search',
        hint: 'Start the desktop and Cloudflare Tunnel to enable full functionality',
      }, { status: 503 });
    }
  },
} satisfies ExportedHandler<Env>;
