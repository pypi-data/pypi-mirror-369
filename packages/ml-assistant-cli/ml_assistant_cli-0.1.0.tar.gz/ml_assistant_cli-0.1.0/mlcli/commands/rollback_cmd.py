"""Rollback command for ML Assistant CLI."""

import typer
from rich.console import Console

console = Console()
app = typer.Typer()


@app.command()
def main(ctx: typer.Context) -> None:
    """Rollback deployments to previous versions."""
    console.print("[yellow]🚧 Rollback command coming soon![/yellow]")
    console.print("This will enable safe rollbacks across all supported cloud providers.")