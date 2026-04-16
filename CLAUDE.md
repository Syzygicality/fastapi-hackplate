# CLAUDE.md

Guidelines for Claude Code when working in this repository.

## Project Overview

FastAPI hackathon template for rapid prototyping. Supports multiple auth backends (Auth0, Keycloak, local) and database connections (Mongo, Postgres, SQLite).

## Dev Environment

- Python 3.13+, managed with `uv`
- Install deps: `uv sync`
- Setup `.env`: `cp template.env .env` and fill in values
- Run dev server: `hackplate run`
- Uses `docker-compose.yml` for local infrastructure (databases, etc.)

## Code Style

- Use the `hackplate` CLI for dev tasks (`hackplate run`, `hackplate precommit`, `hackplate clean`).
- Plate usage is dictated by `.env` variables, customize there.
- Do not modify any code within /app/hackplate unless necessary.
- Respect documentation (.md files, docstrings) within /app/hackplate.
- Implement features via feature-based file structure within /app.
- Run `hackplate run`, `pytest`, and `hackplate precommit` before finishing. Resolve any errors which appear. Close server when done

## Testing

- in /tests, write light API testing pytests after implementing new features to pin down feature functionality

TODO: write AGENTS.md
