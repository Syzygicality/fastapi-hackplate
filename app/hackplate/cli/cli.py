import typer

from app.hackplate.cli import feature, keycloak, mode, plate, start, utils

app = typer.Typer(help="Hackplate dev CLI")

app.add_typer(utils.app)
app.add_typer(feature.app)
app.add_typer(plate.app)
app.add_typer(mode.app)
app.add_typer(start.app)
app.add_typer(keycloak.app)


if __name__ == "__main__":
    app()
