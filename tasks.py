from invoke import task, Context


@task
def clean(c: Context):
    c.run("rm -r ./.ruff_cache")
    c.run("rm -r ./.pytest_cache")


@task
def precommit(c: Context):
    c.run("pre-commit run --all-files")


@task
def run(c: Context):
    c.run("uv run uvicorn app.main:app --reload")
