"""Train command for ML Assistant CLI."""

from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from mlcli.core.models import ModelTrainer
from mlcli.core.exceptions import ModelError, DataError
from mlcli.utils.logging import get_logger

logger = get_logger(__name__)
console = Console()

app = typer.Typer()


@app.command()
def main(
    ctx: typer.Context,
    train_data: Optional[Path] = typer.Option(None, "--train-data", "-t", help="Training data file path"),
    test_data: Optional[Path] = typer.Option(None, "--test-data", help="Test data file path"),
    target_column: Optional[str] = typer.Option(None, "--target", help="Target column name"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for models"),
) -> None:
    """Train ML models with hyperparameter optimization."""
    
    config = ctx.obj["config"]
    project_dir = ctx.obj["project_dir"]
    
    # Set default paths
    if train_data is None:
        train_data = project_dir / "data" / "processed" / "train.csv"
    
    if test_data is None:
        test_data = project_dir / "data" / "processed" / "test.csv"
    
    if output_dir is None:
        output_dir = project_dir / "models"
    
    if target_column is None:
        target_column = config.data.target_column
    
    # Validate inputs
    if not train_data.exists():
        console.print(f"[red]Error:[/red] Training data not found: {train_data}")
        console.print("[yellow]Hint:[/yellow] Run [cyan]mlcli preprocess[/cyan] first to generate training data")
        raise typer.Exit(1)
    
    if not target_column:
        console.print("[red]Error:[/red] Target column not specified")
        console.print("[yellow]Hint:[/yellow] Use --target option or set target_column in mlcli.yaml")
        raise typer.Exit(1)
    
    try:
        # Load training data
        console.print(f"[blue]Loading training data from:[/blue] {train_data}")
        train_df = pd.read_csv(train_data)
        
        if target_column not in train_df.columns:
            raise DataError(f"Target column '{target_column}' not found in training data")
        
        # Separate features and target
        X_train = train_df.drop(columns=[target_column])
        y_train = train_df[target_column]
        
        # Load test data if available
        X_test, y_test = None, None
        if test_data.exists():
            console.print(f"[blue]Loading test data from:[/blue] {test_data}")
            test_df = pd.read_csv(test_data)
            if target_column in test_df.columns:
                X_test = test_df.drop(columns=[target_column])
                y_test = test_df[target_column]
        
        # Initialize model trainer
        trainer = ModelTrainer(config.model)
        
        # Train models with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Training models...", total=None)
            
            training_summary = trainer.train_models(
                X_train, y_train, X_test, y_test
            )
            
            progress.update(task, description="Training complete!")
        
        # Display results
        _display_training_results(training_summary, trainer.models)
        
        # Save models
        output_dir.mkdir(parents=True, exist_ok=True)
        trainer.save_models(output_dir)
        
        console.print(f"[green]✓[/green] Models saved to: {output_dir}")
        console.print(f"[green]✓[/green] Best model: {training_summary['best_model']} (score: {training_summary['best_score']:.4f})")
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Run [cyan]mlcli evaluate[/cyan] to get detailed performance metrics")
        console.print("2. Run [cyan]mlcli suggest[/cyan] to get improvement recommendations")
        console.print("3. Run [cyan]mlcli predict --input new_data.csv[/cyan] to make predictions")
        
    except (ModelError, DataError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        raise typer.Exit(1)


def _display_training_results(summary: dict, models: dict) -> None:
    """Display training results in a formatted table."""
    
    # Model comparison table
    table = Table(title="Model Training Results", show_header=True, header_style="bold magenta")
    table.add_column("Model", style="cyan")
    table.add_column("CV Score", style="green")
    table.add_column("Val Score", style="blue")
    table.add_column("Status", style="white")
    
    for model_name, result in models.items():
        if "error" in result:
            table.add_row(
                model_name,
                "N/A",
                "N/A", 
                f"[red]Error: {result['error'][:50]}...[/red]"
            )
        else:
            cv_score = f"{result.get('cv_score', 0.0):.4f}"
            val_score = f"{result.get('val_score', 0.0):.4f}" if result.get('val_score') else "N/A"
            status = "[green]✓ Success[/green]"
            
            # Highlight best model
            if model_name == summary.get('best_model'):
                model_name = f"[bold]{model_name} ⭐[/bold]"
                cv_score = f"[bold green]{cv_score}[/bold green]"
            
            table.add_row(model_name, cv_score, val_score, status)
    
    console.print(table)
    
    # Training summary
    console.print(f"\n[bold]Training Summary:[/bold]")
    console.print(f"• Task Type: [cyan]{summary['task_type'].title()}[/cyan]")
    console.print(f"• Models Trained: [cyan]{summary['models_trained']}[/cyan]")
    console.print(f"• Best Model: [green]{summary['best_model']}[/green]")
    console.print(f"• Best Score: [green]{summary['best_score']:.4f}[/green]")
    console.print(f"• Cross-Validation: [cyan]{summary['training_config']['cv_folds']} folds[/cyan]")
    console.print(f"• Scoring Metric: [cyan]{summary['training_config']['scoring_metric']}[/cyan]")