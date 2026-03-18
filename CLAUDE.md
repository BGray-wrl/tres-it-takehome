# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Demo AI-Powered Alcohol Label Verification App for the TTB (Alcohol and Tobacco Tax and Trade Bureau).

## Package Manager

Use `uv` for all Python package management:

```bash
uv run <command>          # run a script
source .venv/bin/activate # activate virtualenv
```

No `pyproject.toml` or `requirements.txt` exists yet — the project is greenfield.

## Architecture (To Be Built)

**Deployment target:** Cloudflare (requires build command + output directory)

**APIs available** (keys in `.env`):
- `OPENROUTER_API_KEY` — access to multimodal LLMs (Gemini, Claude, GPT, etc.)
- `GEMINI_API_KEY` — direct Gemini API access
- `GITHUB_TOKEN` — CI/CD integration

**LLM selection:** `docs/model_specs_for_openrouter.md` documents available models with pricing. Prefer fast multimodal models (e.g., Gemini 3.0 Flash) given the <5 second per-label performance requirement.

## Docs

- `docs/requirements-and-spec.md` — core functional requirements
- `docs/interview-notes.md` — stakeholder interviews (critical context on user needs and technical constraints)
- `docs/human-notes.md` — quick-reference stakeholder summary
- `docs/model_specs_for_openrouter.md` — LLM options and pricing via OpenRouter
