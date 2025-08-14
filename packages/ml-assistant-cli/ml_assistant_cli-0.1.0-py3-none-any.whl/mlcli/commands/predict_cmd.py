"""Predict command for ML Assistant CLI."""

import typer
from rich.console import Console

console = Console()
app = typer.Typer()


@app.command()
def main(ctx: typer.Context) -> None:
    """Make predictions on new data using trained models."""
    console.print("[yellow]🚧 Prediction command coming soon![/yellow]")
    console.print("This will enable batch predictions on new datasets.")