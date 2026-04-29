import subprocess
from pathlib import Path
from typing import Literal
from dotenv import set_key, load_dotenv, get_key
import secrets

import typer


app = typer.Typer(help="Hackplate dev CLI")


ROOT_DIR = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()


@app.command()
def regenkey(length: int = typer.Option(32, "-l", "--length", min=8)):
    """Set/regenerate the secret key used for the authentication plate."""
    key = secrets.token_hex(length)
    set_key(Path(ROOT_DIR) / ".env", "SECRET_KEY", key, quote_mode="never")


@app.command()
def startfeature(feature_name: str):
    """Autogenerate feature files and directory."""
    feature_dir = Path(ROOT_DIR) / "app" / feature_name
    feature_dir.mkdir(exist_ok=True)
    for filename in ["routes.py", "schemas.py", "crud.py", "models.py", "__init__.py"]:
        (feature_dir / filename).touch()


@app.command()
def setplate(plate_type: Literal["auth", "db"], plate_name: str):
    """Set/update the authentication and database plates being used by Hackplate."""
    from app.hackplate.config import database_plate_list, auth_plate_list

    plates = {"auth": auth_plate_list, "db": database_plate_list}
    if plate_name not in plates[plate_type]:
        raise typer.BadParameter(
            f"{plate_name} is not a valid plate. {list(plates[plate_type])}"
        )
    set_key(
        Path(ROOT_DIR) / ".env",
        {"db": "HACKPLATE_DB", "auth": "HACKPLATE_AUTH"}[plate_type],
        plate_name,
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
def run(
    docker: bool = typer.Option(False, "-dc", "--docker-compose"),
    args: list[str] = typer.Argument(default=None),
):
    """Start the uvicorn development server with hot reload, with the option to use docker."""
    extra = args or []
    if not docker:
        subprocess.run(
            ["uv", "run", "uvicorn", "app.main:app", "--reload", *extra], check=True
        )
        return

    command_prefix = ["docker", "compose"]

    load_dotenv(verbose=True)
    auth_plate = get_key(Path(ROOT_DIR) / ".env", "HACKPLATE_AUTH")
    if auth_plate and auth_plate == "keycloak":
        command_prefix += ["--profile", "keycloak"]

    subprocess.run([*command_prefix, "up", "-d", *extra], check=True)
    subprocess.run([*command_prefix, "logs", "-f"], check=True)


@app.command()
def down(args: list[str] = typer.Argument(default=None)):
    """Stop active docker containers."""
    extra = args or []
    subprocess.run(["docker", "compose", "--profile", "*", "down", *extra], check=True)


if __name__ == "__main__":
    app()
