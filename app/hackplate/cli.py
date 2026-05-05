import subprocess
from pathlib import Path
from typing import Literal
from dotenv import set_key, load_dotenv, get_key
import secrets
import typer
import time
import httpx
import json
import shutil


app = typer.Typer(help="Hackplate dev CLI")

ROOT_DIR = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()


@app.command()
def regenkey(length: int = typer.Option(32, "-l", "--length", min=8)):
    """Set/regenerate the secret key used for the local authentication plate."""
    key = secrets.token_urlsafe(length)[:length]
    set_key(Path(ROOT_DIR) / ".env", "SECRET_KEY", key, quote_mode="never")
    typer.echo("A new key has been set on SECRET_KEY.")


@app.command()
def startfeature(feature_name: str):
    """Autogenerate feature files and directory."""
    feature_dir = Path(ROOT_DIR) / "app" / feature_name
    try:
        feature_dir.mkdir(exist_ok=False)
    except Exception:
        typer.BadParameter(f"feature directory /{feature_name} already exists.")
    for filename in ["routes.py", "schemas.py", "crud.py", "models.py", "__init__.py"]:
        (feature_dir / filename).touch()
    registry = Path(ROOT_DIR) / "migrations" / "register_models.py"
    current = registry.read_text()
    import_line = f"import app.{feature_name}.models  # noqa: F401\n"
    registry.write_text(current + import_line)
    typer.echo(f"Started feature '{feature_name}'.")


@app.command()
def dropfeature(feature_name: str):
    """Remove a feature directory and its registration from register_models.py."""
    feature_dir = Path(ROOT_DIR) / "app" / feature_name
    if not feature_dir.exists():
        typer.echo(f"Feature directory /app/{feature_name} does not exist.", err=True)
        raise typer.Exit(code=1)
    typer.confirm(
        f"Drop feature '{feature_name}'? This will delete /app/{feature_name} and its model import.",
        abort=True,
    )

    registry = Path(ROOT_DIR) / "migrations" / "register_models.py"
    import_line = f"import app.{feature_name}.models  # noqa: F401\n"
    registry.write_text(registry.read_text().replace(import_line, ""))
    shutil.rmtree(feature_dir)
    typer.echo(f"Dropped feature '{feature_name}'.")


@app.command()
def getplates():
    """Show the current auth and database plates in use."""
    load_dotenv(Path(ROOT_DIR) / ".env")
    auth = get_key(Path(ROOT_DIR) / ".env", "HACKPLATE_AUTH") or "(not set)"
    db = get_key(Path(ROOT_DIR) / ".env", "HACKPLATE_DB") or "(not set)"
    typer.echo(f"auth: {auth}")
    typer.echo(f"db:   {db}")


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
def down(args: list[str] = typer.Argument(default=None)):
    """Stop active docker containers."""
    extra = args or []
    subprocess.run(["docker", "compose", "--profile", "*", "down", *extra], check=True)


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

    if auth_plate and auth_plate == "keycloak":
        wait_for_keycloak()
        subprocess.run(["hackplate", "kcsync"], check=True)

    subprocess.run([*command_prefix, "logs", "-f"], check=True)


def _allow_keycloak_http(host: str, username: str, password):
    kcadm = [
        "docker",
        "compose",
        "--profile",
        "keycloak",
        "exec",
        "keycloak",
        "/opt/keycloak/bin/kcadm.sh",
    ]
    subprocess.run(
        [
            *kcadm,
            "config",
            "credentials",
            "--server",
            host,
            "--realm",
            "master",
            "--user",
            username,
            "--password",
            password,
        ],
        check=True,
    )
    subprocess.run(
        [*kcadm, "update", "realms/master", "-s", "sslRequired=none"],
        check=True,
    )


def wait_for_keycloak(host: str | None = None, retries: int = 20, delay: float = 1.0):
    from app.hackplate.plates.auth_plates.keycloak.config import KeycloakSettings

    kc_host = host or KeycloakSettings().external_url
    typer.echo("Waiting for Keycloak to start up...")
    for _ in range(retries):
        try:
            httpx.get(f"{kc_host}/realms/master", timeout=2)
            return
        except Exception:
            time.sleep(delay)
    typer.echo("Keycloak did not become ready in time.", err=True)
    raise typer.Exit(code=1)


@app.command()
def kcsync(
    host: str | None = typer.Option(None, "-h", "--host"),
    realm: str | None = typer.Option(None, "-r", "--realm"),
    username: str | None = typer.Option(None, "-u", "--username"),
    password: str | None = typer.Option(None, "-p", "--password"),
):
    """Sync Keycloak realm config to app/hackplate/plates/auth_plates/keycloak/settings.json."""
    from app.hackplate.plates.auth_plates.keycloak.config import KeycloakSettings

    settings = KeycloakSettings()

    kc_host = host or settings.external_url
    kc_realm = realm or settings.realm
    kc_username = username or settings.admin_username
    kc_password = password or settings.admin_password

    _allow_keycloak_http(kc_host, kc_username, kc_password)

    try:
        token_res = httpx.post(
            f"{kc_host}/realms/master/protocol/openid-connect/token",
            data={
                "client_id": "admin-cli",
                "username": kc_username,
                "password": kc_password,
                "grant_type": "password",
            },
        )
    except Exception as e:
        typer.echo(f"Could not reach Keycloak at {kc_host}: {e}", err=True)
        raise typer.Exit(code=1)
    if not token_res.is_success:
        typer.echo(
            f"Keycloak token request failed ({token_res.status_code}): {token_res.text}",
            err=True,
        )
        raise typer.Exit(code=1)

    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    realm_data = httpx.get(f"{kc_host}/admin/realms/{kc_realm}", headers=headers)
    realm_data.raise_for_status()
    clients_data = httpx.get(
        f"{kc_host}/admin/realms/{kc_realm}/clients", headers=headers
    )
    clients_data.raise_for_status()
    roles_data = httpx.get(f"{kc_host}/admin/realms/{kc_realm}/roles", headers=headers)
    roles_data.raise_for_status()

    clients = clients_data.json()
    hackplate_client = next(
        (c for c in clients if c["clientId"] == settings.client_id), None
    )
    if hackplate_client is None:
        typer.echo(f"Could not find client '{kc_realm}' in realm.", err=True)
        raise typer.Exit(code=1)

    secret_res = httpx.get(
        f"{kc_host}/admin/realms/{kc_realm}/clients/{hackplate_client['id']}/client-secret",
        headers=headers,
    )
    secret_res.raise_for_status()
    client_secret = secret_res.json().get("value")

    if client_secret:
        set_key(
            Path(ROOT_DIR) / ".env",
            "KEYCLOAK_CLIENT_SECRET",
            client_secret,
            quote_mode="never",
        )
        typer.echo("Client secret written to .env")

    SENSITIVE_KEYS = {"secret", "registrationAccessToken"}
    sanitized_clients = [
        {k: v for k, v in c.items() if k not in SENSITIVE_KEYS} for c in clients
    ]

    merged = realm_data.json()
    merged["clients"] = sanitized_clients
    merged["roles"] = {"realm": roles_data.json()}

    out_path = (
        Path(ROOT_DIR) / "app/hackplate/plates/auth_plates/keycloak/settings.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, indent=2) + "\n")

    typer.echo("Keycloak synced!")


if __name__ == "__main__":
    app()
