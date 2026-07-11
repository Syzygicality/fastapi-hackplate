import secrets
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from dotenv import set_key

ROOT_DIR = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

app = typer.Typer()


@app.command()
def init():
    """Initialize the repo for development. Prompts for plates and sets up .env. Runs once."""
    from app.hackplate.config import database_plate_list, auth_plate_list

    sentinel = Path(ROOT_DIR) / ".hackplate_init"
    if sentinel.exists():
        typer.echo("Already initialized. Delete .hackplate_init to re-run.", err=True)
        raise typer.Exit(code=1)

    if not shutil.which("uv"):
        typer.echo("Installing uv...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)

    typer.echo("Running uv sync...")
    subprocess.run(["uv", "sync"], check=True, cwd=ROOT_DIR)

    env_path = Path(ROOT_DIR) / ".env"
    template_path = Path(ROOT_DIR) / ".env.example"

    if not env_path.exists():
        shutil.copy(template_path, env_path)
        typer.echo("Created .env from .env.example")

    auth_choices = list(auth_plate_list)
    typer.echo(f"\nAvailable auth plates: {', '.join(auth_choices)}")
    auth_plate = typer.prompt("Auth plate", default="local")
    while auth_plate not in auth_choices:
        typer.echo(f"Invalid choice. Pick one of: {', '.join(auth_choices)}")
        auth_plate = typer.prompt("Auth plate", default="local")

    db_choices = list(database_plate_list)
    typer.echo(f"\nAvailable database plates: {', '.join(db_choices)}")
    db_plate = typer.prompt("Database plate", default="sqlite")
    while db_plate not in db_choices:
        typer.echo(f"Invalid choice. Pick one of: {', '.join(db_choices)}")
        db_plate = typer.prompt("Database plate", default="sqlite")

    set_key(env_path, "HACKPLATE_AUTH", auth_plate, quote_mode="never")
    set_key(env_path, "HACKPLATE_DB", db_plate, quote_mode="never")

    key = secrets.token_urlsafe(32)[:32]
    set_key(env_path, "SECRET_KEY", key, quote_mode="never")

    typer.echo("\nInstalling pre-commit hooks...")
    subprocess.run(["uv", "run", "pre-commit", "install"], check=True, cwd=ROOT_DIR)

    subprocess.run(["hackplate", "setmode", "safe"], check=True, cwd=ROOT_DIR)

    sentinel.touch()

    typer.echo(f"\nInitialized: auth={auth_plate}, db={db_plate}")
    typer.echo("Secret key generated. Fill in remaining values in .env before running.")


@app.command()
def regenkey(length: int = typer.Option(32, "-l", "--length", min=8)):
    """Set/regenerate the secret key used for the local authentication plate."""
    key = secrets.token_urlsafe(length)[:length]
    set_key(Path(ROOT_DIR) / ".env", "SECRET_KEY", key, quote_mode="never")
    typer.echo("A new key has been set on SECRET_KEY.")


@app.command()
def clean():
    """Remove cache/metadata directories (.ruff_cache, .pytest_cache, __pycache__, *.egg-info)."""
    root = Path(ROOT_DIR)
    for folder in [".ruff_cache", ".pytest_cache", *root.glob("*.egg-info")]:
        target: Path = root / folder
        if target.exists():
            subprocess.run(["rm", "-r", str(target)], check=True)
    for pycache in root.rglob("__pycache__"):
        if pycache.exists():
            subprocess.run(["rm", "-r", str(pycache)], check=True)


@app.command()
def precommit():
    """Install and run pre-commit hooks on all files."""
    subprocess.run(["pre-commit", "install"], check=True)
    result = subprocess.run(["pre-commit", "run", "--all-files"])
    if result.returncode != 0:
        subprocess.run(["pre-commit", "run", "--all-files"])
