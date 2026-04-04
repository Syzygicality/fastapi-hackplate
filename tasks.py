from invoke import task, Context


@task
def hello(c: Context):
    print("hello world!")


@task
def clean(c: Context):
    c.run("rm -r ./.ruff_cache")
    c.run("rm -r ./.pytest_cache")
