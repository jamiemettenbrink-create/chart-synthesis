// Cloudflare Worker — proxies un/charted requests to Anthropic and Human Design.
// API keys live as Worker secrets (set via `wrangler secret put …`), never in
// the static page. Only requests from the GitHub Pages origin are accepted.

const ALLOWED_ORIGINS = new Set([
  'https://jamiemettenbrink-create.github.io',
  'http://localhost:8000',
  'http://127.0.0.1:8000',
]);

const DEFAULT_ORIGIN = 'https://jamiemettenbrink-create.github.io';

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.has(origin) ? origin : DEFAULT_ORIGIN;
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders(origin) });
    }

    if (!ALLOWED_ORIGINS.has(origin)) {
      return new Response('Forbidden origin', { status: 403, headers: corsHeaders(origin) });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: corsHeaders(origin) });
    }

    try {
      if (url.pathname === '/anthropic') return await proxyAnthropic(request, env, origin);
      if (url.pathname === '/hd')        return await proxyHumanDesign(request, env, origin);
      return new Response('Not found', { status: 404, headers: corsHeaders(origin) });
    } catch (e) {
      return new Response(`Proxy error: ${e.message}`, { status: 502, headers: corsHeaders(origin) });
    }
  },
};

async function proxyAnthropic(request, env, origin) {
  if (!env.ANTHROPIC_API_KEY) {
    return new Response('ANTHROPIC_API_KEY secret is not set on the Worker', {
      status: 500, headers: corsHeaders(origin),
    });
  }
  const body = await request.arrayBuffer();
  const upstream = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body,
  });
  const headers = new Headers(corsHeaders(origin));
  const ct = upstream.headers.get('Content-Type');
  if (ct) headers.set('Content-Type', ct);
  // Pass the response body straight through — this preserves SSE streaming
  // for {"stream": true} requests.
  return new Response(upstream.body, { status: upstream.status, headers });
}

async function proxyHumanDesign(request, env, origin) {
  if (!env.HD_API_KEY) {
    return new Response('HD_API_KEY secret is not set on the Worker', {
      status: 500, headers: corsHeaders(origin),
    });
  }
  const body = await request.arrayBuffer();
  const upstream = await fetch('https://api.humandesignhub.app/v1/simple-bodygraph', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-KEY': env.HD_API_KEY,
    },
    body,
  });
  const headers = new Headers(corsHeaders(origin));
  const ct = upstream.headers.get('Content-Type');
  if (ct) headers.set('Content-Type', ct);
  return new Response(upstream.body, { status: upstream.status, headers });
}
