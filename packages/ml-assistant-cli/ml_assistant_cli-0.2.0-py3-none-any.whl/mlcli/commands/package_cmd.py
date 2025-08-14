"""Package command for ML Assistant CLI."""

import typer
from rich.console import Console

console = Console()
app = typer.Typer()


@app.command()
def main(ctx: typer.Context) -> None:
    """Package trained model as BentoML service for deployment."""
    console.print("[yellow]🚧 Packaging command coming soon![/yellow]")
    console.print("This will create BentoML services for local serving and cloud deployment.")