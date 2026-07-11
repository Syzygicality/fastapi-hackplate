import json
import subprocess
import time
from pathlib import Path
from typing import Literal

import httpx
import typer
from dotenv import get_key, load_dotenv, set_key

from app.hackplate.cli.utils import ROOT_DIR

KEYCLOAK_COMPOSE_FILE = (
    "app/hackplate/plates/auth_plates/keycloak/docker-compose.keycloak.yml"
)


def _compose_files(use_keycloak: bool) -> list[str]:
    files = ["-f", "docker-compose.yml"]
    if use_keycloak:
        files += ["-f", KEYCLOAK_COMPOSE_FILE]
    return files


def _keycloak_service(mode: Literal["dev", "prod"]) -> str:
    return "keycloak" if mode == "dev" else "keycloak-prod"


app = typer.Typer()


@app.command()
def run(
    mode: Literal["dev", "prod"] = typer.Option(
        "dev", "-m", "--mode", help="Run mode: dev (hot reload) or prod."
    ),
    docker: bool = typer.Option(False, "-dc", "--docker-compose"),
    args: list[str] = typer.Argument(default=None),
):
    """Start the uvicorn server, with the option to use docker. -m/--mode selects dev or prod (default: dev)."""
    extra = args or []

    if not docker:
        uvicorn_cmd = ["uv", "run", "uvicorn", "app.main:app"]
        if mode == "dev":
            uvicorn_cmd += ["--reload"]
        else:
            workers = get_key(Path(ROOT_DIR) / ".env", "HACKPLATE_WORKERS") or "4"
            uvicorn_cmd += ["--host", "0.0.0.0", "--port", "8000", "--workers", workers]
        subprocess.run([*uvicorn_cmd, *extra], check=True)
        return

    load_dotenv(verbose=True)
    auth_plate = get_key(Path(ROOT_DIR) / ".env", "HACKPLATE_AUTH")
    is_local = get_key(Path(ROOT_DIR) / ".env", "KEYCLOAK_USE_LOCAL")
    use_keycloak = bool(auth_plate == "keycloak" and is_local)

    command_prefix = [
        "docker",
        "compose",
        *_compose_files(use_keycloak),
        "--profile",
        mode,
    ]

    subprocess.run([*command_prefix, "up", "-d", *extra], check=True)

    if use_keycloak:
        wait_for_keycloak()
        subprocess.run(["hackplate", "kcsync", "--mode", mode], check=True)

    subprocess.run([*command_prefix, "logs", "-f"], check=True)


@app.command()
def down(args: list[str] = typer.Argument(default=None)):
    """Stop active docker containers."""
    extra = args or []
    subprocess.run(
        [
            "docker",
            "compose",
            *_compose_files(use_keycloak=True),
            "--profile",
            "*",
            "down",
            *extra,
        ],
        check=True,
    )


def _allow_keycloak_http(host: str, username: str, password: str, service: str):
    kcadm = [
        "docker",
        "compose",
        *_compose_files(use_keycloak=True),
        "exec",
        service,
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
    mode: Literal["dev", "prod"] = typer.Option(
        "dev",
        "-m",
        "--mode",
        help="Which running mode's Keycloak container to sync from.",
    ),
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

    _allow_keycloak_http(kc_host, kc_username, kc_password, _keycloak_service(mode))

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

    export_res = httpx.post(
        f"{kc_host}/admin/realms/{kc_realm}/partial-export",
        params={"exportClients": "true", "exportGroupsAndRoles": "true"},
        headers=headers,
    )
    export_res.raise_for_status()
    exported = export_res.json()

    clients = exported.get("clients", [])
    hackplate_client = next(
        (c for c in clients if c["clientId"] == settings.client_id), None
    )
    if hackplate_client is None:
        typer.echo(f"Could not find client '{settings.client_id}' in realm.", err=True)
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
    exported["clients"] = [
        {k: v for k, v in c.items() if k not in SENSITIVE_KEYS} for c in clients
    ]

    merged = exported

    out_path = (
        Path(ROOT_DIR) / "app/hackplate/plates/auth_plates/keycloak/settings.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, indent=2) + "\n")

    typer.echo("Keycloak synced!")
