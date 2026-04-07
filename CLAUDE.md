# CLAUDE.md

Guidelines for Claude Code when working in this repository.

## Project Overview

FastAPI hackathon template for rapid prototyping. Supports multiple auth backends (Auth0, Keycloak, local) and database connections (Mongo, Postgres, SQLite).

## Dev Environment

- Python 3.13+, managed with `uv`
- Install deps: `uv sync`
- Run dev server: `inv run`
- Uses `docker-compose.yml` for local infrastructure (databases, etc.)

## Code Style

- Utilize `tasks.py`'s defined invoke commands.
- Plate usage is dictated by `.env` variables, customize there.
- Do not modify any code within /hackplate unless necessary.
- Respect documentation (.md files, docstrings) within /hackplate.
- Implement features via feature-based file structure within /app.
- Run `inv run`, `pytest`, and `inv precommit` before finishing. Resolve any errors which appear.

## Testing

- in /tests, write light API testing pytests after implementing new features to pin down feature functionality
