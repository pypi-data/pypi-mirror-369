"""Deploy command for ML Assistant CLI."""

import typer
from rich.console import Console

console = Console()
app = typer.Typer()


@app.command()
def main(ctx: typer.Context) -> None:
    """Deploy packaged models to cloud providers."""
    console.print("[yellow]🚧 Deployment command coming soon![/yellow]")
    console.print("This will support BentoCloud, Azure ML, and AWS SageMaker HyperPod deployments.")