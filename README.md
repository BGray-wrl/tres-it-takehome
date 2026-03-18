# TTB Label Verification App

AI-powered alcohol label verification demo for TTB (Alcohol and Tobacco Tax and Trade Bureau) agents.

Upload label photos and instantly verify:
- **Brand name** match (case-insensitive)
- **ABV** (alcohol by volume) value
- **Government warning statement** presence and format

---

## How It Works

1. Agent uploads one or more label images
2. Enters the expected brand name and ABV
3. Each label is sent (in parallel) to the backend, which calls **Google Gemini Flash** via OpenRouter
4. Results render in a table — pass/fail per check with found values from the label

---

## Cloudflare Pages Deployment

| Setting | Value |
|---|---|
| **Build command** | *(leave empty)* |
| **Build output directory** | `public` |
| **Environment variable** | `OPENROUTER_API_KEY` → set in Cloudflare Pages dashboard |

The app uses a [Cloudflare Pages Function](https://developers.cloudflare.com/pages/functions/) at `functions/api/verify.js` — no build step required. Cloudflare automatically deploys it alongside the static files in `public/`.

### Steps

1. Connect this GitHub repo to a new Cloudflare Pages project
2. Set **Output directory** to `public` (build command empty)
3. Add `OPENROUTER_API_KEY` under **Settings → Environment variables**
4. Deploy — the app is live

---

## Local Development

Test locally using [Wrangler](https://developers.cloudflare.com/workers/wrangler/):

```bash
npm install -g wrangler

# Create a local .dev.vars file with your key (do NOT commit this)
echo 'OPENROUTER_API_KEY=sk-or-...' > .dev.vars

wrangler pages dev public --compatibility-flag=nodejs_compat
```

Then open `http://localhost:8788` in your browser.

---

## Project Structure

```
public/
  index.html          # Full UI (single file, no build needed)
functions/
  api/
    verify.js         # Cloudflare Pages Function — proxies to OpenRouter
docs/
  requirements-and-spec.md
  interview-notes.md
  model_specs_for_openrouter.md
```

---

## Environment Variables

| Variable | Where |
|---|---|
| `OPENROUTER_API_KEY` | Cloudflare Pages dashboard (production) or `.dev.vars` (local) |
