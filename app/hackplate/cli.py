import subprocess
from pathlib import Path
from typing import Literal
from dotenv import set_key

import typer


app = typer.Typer(help="Hackplate dev CLI")


ROOT_DIR = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()


@app.command()
def startfeature(feature_name: str):
    feature_dir = Path(ROOT_DIR) / "app" / feature_name
    feature_dir.mkdir(exist_ok=True)

    for filename in ["routes.py", "schemas.py", "crud.py", "models.py", "__init__.py"]:
        (feature_dir / filename).touch()


@app.command()
def set(plate_type: Literal["auth", "db"], name: str):
    from app.hackplate.config import database_plates, auth_plates

    plates = {"auth": auth_plates.keys(), "db": database_plates.keys()}
    if name not in plates[plate_type]:
        raise typer.BadParameter(
            f"{name} is not a valid plate. ({list(plates[plate_type])})"
        )
    set_key(
        Path(ROOT_DIR) / ".env",
        {"db": "HACKPLATE_DB", "auth": "HACKPLATE_AUTH"}[plate_type],
        name,
        quote_mode="never",
    )


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
