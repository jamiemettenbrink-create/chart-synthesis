# un/charted — API proxy (Cloudflare Worker)

Tiny Cloudflare Worker that lets the static `app.html` page call the Anthropic
and Human Design APIs without ever exposing the keys in the browser.

```
browser  ─►  https://<your-worker>.workers.dev/anthropic  ─►  api.anthropic.com
browser  ─►  https://<your-worker>.workers.dev/hd         ─►  api.humandesignhub.app
```

The keys live as encrypted Worker secrets. The Worker only accepts requests
from origins listed in `ALLOWED_ORIGINS` inside `worker.js`.

---

## One-time deploy

You'll need a Cloudflare account (free; sign up at <https://dash.cloudflare.com/sign-up>)
and Node.js installed locally.

### 1. Install Wrangler

```sh
npm install -g wrangler
```

### 2. Log in

```sh
wrangler login
```

This opens a browser tab to authorize Wrangler against your Cloudflare account.

### 3. Deploy the Worker

From this `proxy/` directory:

```sh
cd proxy
wrangler deploy
```

On first deploy Wrangler will:
- Provision a `workers.dev` subdomain for your account if you don't have one
- Print the live URL, something like
  `https://chart-synthesis-proxy.<your-subdomain>.workers.dev`

**Copy that URL — you'll paste it into `app.html` in step 5.**

### 4. Set the secrets

```sh
wrangler secret put ANTHROPIC_API_KEY
# paste your new Anthropic key when prompted, then Enter

wrangler secret put HD_API_KEY
# paste your Human Design key (or any value if you don't use HD), then Enter
```

The secrets are encrypted at rest on Cloudflare and never appear in source or
in deploys.

### 5. Point `app.html` at the Worker

Open `app.html` and set `CONFIG.proxyUrl` near the top of the script tag to the
URL from step 3 (no trailing slash):

```js
const CONFIG = {
  proxyUrl: 'https://chart-synthesis-proxy.<your-subdomain>.workers.dev',
  …
};
```

Commit and push. GitHub Pages will pick it up.

### 6. Smoke-test

Open the live page, generate a reading, and watch the Network tab. You should
see requests to `…workers.dev/anthropic` (streaming) and `…workers.dev/hd`,
both with a 200. No `x-api-key` header on the browser side.

---

## Day-to-day

- **Rotating a key**: re-run `wrangler secret put ANTHROPIC_API_KEY` with the
  new value. Takes effect on the next request — no redeploy needed.
- **Updating the Worker code**: edit `worker.js`, then `wrangler deploy`.
- **Adding a new allowed origin** (e.g. a custom domain or staging): add it to
  `ALLOWED_ORIGINS` in `worker.js` and redeploy.
- **Local dev**: `wrangler dev` starts the Worker on `http://localhost:8787`.
  Set `CONFIG.proxyUrl` to that URL when developing locally.

## Notes on abuse

The Worker URL is embedded in the public HTML, so anyone who views the page
can find it. The `Origin` header check rejects requests from other websites,
but a determined caller can still spoof the header from a script. If usage
grows, add a Cloudflare WAF rate-limit rule (free tier includes a basic one)
or move to a per-user auth flow.
