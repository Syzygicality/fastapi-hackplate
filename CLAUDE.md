# CLAUDE.md

Guidelines for Claude Code when working in this repository.

## Project Overview

FastAPI hackathon template for rapid prototyping. Supports multiple auth backends (Auth0, Keycloak, local) and multiple databases (Mongo, Postgres, SQLite).

## Dev Environment

- Python 3.13+, managed with `uv`
- Install deps: `uv sync`
- Run dev server: `inv run`
- Uses `docker-compose.yml` for local infrastructure (databases, etc.)

## Code Style

- Follow existing patterns in each module — don't introduce new conventions without reason
- Keep route handlers thin; push logic into service/utility layers
- Config lives in `app/config/config.py` — extend it there, not inline

## Testing

- (Tests not yet configured — add guidance here when set up)

## Common Tasks

- Add a new route: create a router module, mount it in `app/main.py`
- Add a new auth backend: follow the pattern in `app/auth/`
- Add a new DB backend: follow the pattern in `app/db/`
