from invoke import task, Context
from pathlib import Path


@task
def clean(c: Context):
    for cache in [".ruff_cache", ".pytest_cache"]:
        if Path(cache).exists():
            c.run(f"rm -r ./{cache}")


@task
def precommit(c: Context):
    c.run("pre-commit install")
    result = c.run("pre-commit run --all-files")
    if not result.ok:
        c.run("pre-commit run --all-files")


@task
def run(c: Context):
    c.run("uv run uvicorn app.main:app --reload")
