# Review Mode

Read-only. Investigate and report — do not modify anything.

- Never use `Edit`, `Write`, or `NotebookEdit`. Do not create, delete, move, or rename files.
- Do not run commands that write to the filesystem, git history, the database, or any external service: no `git add/commit/push`, no `uv add/remove`, no `hackplate run/up/down/init/setmode/setplate/startfeature/dropfeature/regenkey/clean/precommit/keycloak`, no `alembic upgrade/downgrade`, no `docker compose up/down`.
- Stick to inspection commands: `git status`, `git log`, `git diff`, `git show`, `find`, `grep`, `hackplate getplates`, `hackplate getmode`, `hackplate check`.
- If the task requires a change, describe it precisely instead of making it: which file, which lines, what the diff should be. Whoever applies it can switch to `fast` or `safe` mode to do so.
- Flag anything destructive or irreversible you notice (missing migrations, secrets in tracked files, etc.) rather than fixing it yourself.

## Testing

Don't run the test suite — it can write to a database or leave artifacts on disk. Read the relevant tests and reason about expected behavior instead.

## Before Finishing

Summarize findings only. Do not run `hackplate run`, `hackplate precommit`, or anything else that touches the repo or environment.
