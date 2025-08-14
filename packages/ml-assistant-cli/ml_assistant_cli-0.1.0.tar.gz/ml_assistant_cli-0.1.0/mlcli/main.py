"""Main CLI application entry point."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.traceback import install

from mlcli.commands import (
    deploy_cmd,
    evaluate_cmd,
    init_cmd,
    monitor_cmd,
    package_cmd,
    predict_cmd,
    preprocess_cmd,
    rollback_cmd,
    suggest_cmd,
    train_cmd,
)
from mlcli.core.config import get_config
from mlcli.core.exceptions import MLCLIError
from mlcli.utils.logging import setup_logging

# Install rich traceback handler for better error display
install(show_locals=True)

# Initialize console for rich output
console = Console()

# Create main Typer app
app = typer.Typer(
    name="mlcli",
    help="🚀 ML Assistant CLI - From dataset to deployed API in minutes",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)

# Add commands
app.add_typer(init_cmd.app, name="init", help="Initialize a new ML project")
app.add_typer(preprocess_cmd.app, name="preprocess", help="Preprocess and clean data")
app.add_typer(train_cmd.app, name="train", help="Train ML models")
app.add_typer(evaluate_cmd.app, name="evaluate", help="Evaluate model performance")
app.add_typer(suggest_cmd.app, name="suggest", help="Get AI-guided improvement suggestions")
app.add_typer(predict_cmd.app, name="predict", help="Make predictions on new data")
app.add_typer(package_cmd.app, name="package", help="Package model as BentoML service")
app.add_typer(deploy_cmd.app, name="deploy", help="Deploy to cloud providers")
app.add_typer(monitor_cmd.app, name="monitor", help="Monitor deployed models")
app.add_typer(rollback_cmd.app, name="rollback", help="Rollback deployments")


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    project_dir: Optional[Path] = typer.Option(
        None, "--project-dir", "-p", help="Project directory path"
    ),
) -> None:
    """ML Assistant CLI - End-to-end ML workflow automation."""
    # Setup logging
    setup_logging(verbose=verbose)
    
    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config_file"] = config_file
    ctx.obj["project_dir"] = project_dir or Path.cwd()
    
    # Load and validate configuration
    try:
        config = get_config(config_file, ctx.obj["project_dir"])
        ctx.obj["config"] = config
    except MLCLIError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        raise typer.Exit(1)


def cli_main() -> None:
    """Entry point for the CLI application."""
    try:
        app()
    except MLCLIError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    cli_main()