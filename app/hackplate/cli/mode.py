import shutil
from pathlib import Path
from typing import Literal

import typer

from app.hackplate.cli.utils import ROOT_DIR

app = typer.Typer()


@app.command()
def setmode(mode: Literal["safe", "fast"]):
    """Switch the Claude Code operating mode. Writes to the gitignored modes/CLAUDE.mode.md."""
    mode_path = Path(ROOT_DIR) / "modes" / "CLAUDE.mode.md"
    mode_path.write_text(f"@modes/CLAUDE.{mode}.md\n")
    shutil.copy(
        Path(ROOT_DIR) / "modes" / f"settings.{mode}.json",
        Path(ROOT_DIR) / ".claude" / "settings.json",
    )
    typer.echo(
        f"Claude mode set to '{mode}'. Restart your session for {mode} mode to take effect"
    )


@app.command()
def getmode():
    """Show the current Claude Code operating mode."""
    mode_path = Path(ROOT_DIR) / "modes" / "CLAUDE.mode.md"
    if not mode_path.exists():
        typer.echo("mode: (not set)")
        return
    content = mode_path.read_text().strip()
    mode = content.removeprefix("@modes/CLAUDE.").removesuffix(".md")
    typer.echo(f"mode: {mode}")
