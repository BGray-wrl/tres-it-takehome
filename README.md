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

---

## Approach, Tools Used & Assumptions

### Approach

The core insight from stakeholder interviews is that most TTB label review is pure **matching** — does the label say what the application says? This lends itself well to a multimodal LLM that can read an image and answer structured questions about it.

The app is intentionally minimal: a single HTML file for the UI, a single serverless function for the backend. No framework, no build step, no database. Labels are never stored — each request is stateless.

Checks implemented:
- **Brand name**: Case-insensitive match with tolerance for capitalization variants (e.g. "Stone's Throw" ↔ "STONE'S THROW"), per Dave Morrison's feedback on false positives from strict matching.
- **ABV**: Exact numeric match. Accepts input with or without the `%` suffix.
- **Government warning**: Checks word-for-word accuracy of the full mandated statement, that `"GOVERNMENT WARNING:"` appears in all caps (not title case), and that the text is legibly displayed — per Jenny Park's note that agents reject labels using title case or burying the warning in unreadably small print.

Multiple labels are processed **in parallel** (Promise.all), addressing Sarah Chen's batch-upload requirement for high-volume importers.

### Tools Used

| Layer | Choice | Reason |
|---|---|---|
| Frontend | Vanilla HTML/CSS/JS | Zero dependencies, zero build step; works on any browser without install |
| Backend | Cloudflare Pages Functions (JS) | Native runtime on Cloudflare — no cold start, no container, free tier |
| LLM | Google Gemini Flash via OpenRouter | Fastest multimodal model available; sub-5s response time meets Sarah's hard requirement from the failed scanning-vendor pilot |
| Hosting | Cloudflare Pages | Free, git-integrated, global CDN, supports serverless functions alongside static files |

### Assumptions & Trade-offs

- **No persistence**: Labels and results are not stored anywhere. For a production system, you'd want audit logs and document retention — Marcus flagged federal compliance requirements. Out of scope for a prototype.
- **Single brand/ABV per batch**: All uploaded images in one session are checked against the same brand name and ABV. A production workflow would likely tie each image to its own application record from COLA.
- **Network access**: OpenRouter must be reachable from Cloudflare's network. If deployed inside TTB's internal Azure environment, the firewall restrictions Marcus mentioned would need to be addressed (likely via an approved proxy or using Azure-hosted models).
- **Image quality**: The LLM handles moderate rotation, glare, and lighting variation reasonably well (as Jenny hoped). Severely degraded images will return null/fail with a note — agents should re-photograph and resubmit.
- **No auth**: The prototype has no login. A production system would require SSO and role-based access.
