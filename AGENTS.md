# AGENTS.md

Guidelines for AI agents (Codex, Claude, etc.) working in this repository.

## Repository Layout

```
app/
  auth/         # Auth backends: auth0/, keycloak/, local/
  config/       # App config, logging, exception handlers
  db/           # DB backends: mongo/, postgres/, sqlite/
  lifespan.py   # FastAPI lifespan (startup/shutdown)
  main.py       # App entrypoint, router mounting
```

## Ground Rules

- Do not modify `uv.lock` manually — let `uv` manage it
- Do not commit secrets; use `template.env` as the reference for env vars
- Keep changes scoped — one concern per PR

## Adding Features

- New auth backend: add a subdir under `app/auth/`, mirror the interface of an existing backend
- New DB backend: add a subdir under `app/db/`, mirror the interface of an existing backend
- New API routes: add a router module, import and mount in `app/main.py`

## Environment Variables

Copy `template.env` to `.env` and fill in values. Never commit `.env`.

## Dependencies

Add packages with `uv add <package>`. Do not edit `pyproject.toml` dependencies by hand unless necessary.
