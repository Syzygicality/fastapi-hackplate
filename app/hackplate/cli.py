import subprocess
from pathlib import Path

import typer

app = typer.Typer(help="Hackplate dev CLI")


@app.command()
def clean():
    """Remove cache/metadata directories (.ruff_cache, .pytest_cache, *.egg-info)."""
    for folder in [".ruff_cache", ".pytest_cache", *Path(".").glob("*.egg-info")]:
        if Path(folder).exists():
            subprocess.run(["rm", "-r", f"./{folder}"], check=True)


@app.command()
def precommit():
    """Install and run pre-commit hooks on all files."""
    subprocess.run(["pre-commit", "install"], check=True)
    result = subprocess.run(["pre-commit", "run", "--all-files"])
    if result.returncode != 0:
        subprocess.run(["pre-commit", "run", "--all-files"])


@app.command()
def run():
    """Start the uvicorn development server with hot reload."""
    subprocess.run(["uv", "run", "uvicorn", "app.main:app", "--reload"])


if __name__ == "__main__":
    app()
