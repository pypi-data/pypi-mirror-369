"""Predict command for ML Assistant CLI."""

import json
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from mlcli.core.models import ModelTrainer
from mlcli.core.data import DataProcessor
from mlcli.core.exceptions import ModelError, DataError
from mlcli.utils.logging import get_logger

logger = get_logger(__name__)
console = Console()

app = typer.Typer()


@app.command()
def main(
    ctx: typer.Context,
    input_file: Path = typer.Option(..., "--input", "-i", help="Input data file for predictions"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for predictions"),
    model_path: Optional[Path] = typer.Option(None, "--model", "-m", help="Model file path"),
    include_probabilities: bool = typer.Option(False, "--probabilities", "-p", help="Include prediction probabilities (classification only)"),
    batch_size: int = typer.Option(1000, "--batch-size", "-b", help="Batch size for large datasets"),
) -> None:
    """Make batch predictions on new data using trained models."""
    
    config = ctx.obj["config"]
    project_dir = ctx.obj["project_dir"]
    
    # Set default paths
    if model_path is None:
        model_path = project_dir / "models" / "best_model.pkl"
    
    if output_file is None:
        output_file = project_dir / "predictions" / f"predictions_{input_file.stem}.csv"
    
    # Validate inputs
    if not input_file.exists():
        console.print(f"[red]Error:[/red] Input file not found: {input_file}")
        raise typer.Exit(1)
    
    if not model_path.exists():
        console.print(f"[red]Error:[/red] Model not found: {model_path}")
        console.print("[yellow]Hint:[/yellow] Run [cyan]mlcli train[/cyan] first to train models")
        raise typer.Exit(1)
    
    try:
        # Load input data
        console.print(f"[blue]Loading input data from:[/blue] {input_file}")
        input_df = pd.read_csv(input_file)
        console.print(f"[green]✓[/green] Loaded {len(input_df)} samples with {len(input_df.columns)} features")
        
        # Load model
        console.print(f"[blue]Loading model from:[/blue] {model_path}")
        trainer = ModelTrainer(config.model)
        model = trainer.load_model(model_path)
        
        # Load data processor if available
        data_processor = None
        preprocessor_path = project_dir / "data" / "processed" / "data_profile.json"
        if preprocessor_path.exists():
            console.print("[blue]Loading data preprocessing pipeline...[/blue]")
            data_processor = DataProcessor(config.data)
            # Note: In a full implementation, we'd save and load the fitted preprocessor
        
        # Detect task type from training summary
        task_type = "classification"  # Default
        training_summary_path = project_dir / "models" / "training_summary.json"
        if training_summary_path.exists():
            with open(training_summary_path, 'r') as f:
                training_summary = json.load(f)
                task_type = training_summary.get('task_type', 'classification')
        
        # Make predictions
        console.print("[blue]Making predictions...[/blue]")
        
        # Create output directory
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if len(input_df) > batch_size:
            # Process in batches for large datasets
            predictions_df = _predict_in_batches(
                input_df, model, trainer, task_type, 
                batch_size, include_probabilities
            )
        else:
            # Process all at once for small datasets
            predictions_df = _make_predictions(
                input_df, model, trainer, task_type, include_probabilities
            )
        
        # Save predictions
        predictions_df.to_csv(output_file, index=False)
        
        # Display results summary
        _display_prediction_summary(predictions_df, task_type, input_file, output_file)
        
        console.print(f"[green]✓[/green] Predictions saved to: {output_file}")
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Review the predictions in the output file")
        console.print("2. Use [cyan]mlcli evaluate[/cyan] if you have ground truth labels")
        console.print("3. Consider [cyan]mlcli package[/cyan] for deployment if satisfied with results")
        
    except (ModelError, DataError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        raise typer.Exit(1)


def _make_predictions(
    input_df: pd.DataFrame,
    model,
    trainer: ModelTrainer,
    task_type: str,
    include_probabilities: bool
) -> pd.DataFrame:
    """Make predictions on the input data."""
    
    # Make predictions
    predictions = trainer.predict(model, input_df)
    
    # Create results dataframe
    results_df = input_df.copy()
    results_df['prediction'] = predictions
    
    # Add probabilities for classification
    if task_type == "classification" and include_probabilities:
        probabilities = trainer.predict_proba(model, input_df)
        if probabilities is not None:
            # Add probability columns
            n_classes = probabilities.shape[1]
            for i in range(n_classes):
                results_df[f'probability_class_{i}'] = probabilities[:, i]
            
            # Add confidence (max probability)
            results_df['confidence'] = np.max(probabilities, axis=1)
    
    return results_df


def _predict_in_batches(
    input_df: pd.DataFrame,
    model,
    trainer: ModelTrainer,
    task_type: str,
    batch_size: int,
    include_probabilities: bool
) -> pd.DataFrame:
    """Make predictions in batches for large datasets."""
    
    n_samples = len(input_df)
    n_batches = (n_samples + batch_size - 1) // batch_size
    
    results_list = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Processing {n_batches} batches...", total=n_batches)
        
        for i in range(0, n_samples, batch_size):
            batch_df = input_df.iloc[i:i+batch_size]
            
            # Make predictions for this batch
            batch_results = _make_predictions(
                batch_df, model, trainer, task_type, include_probabilities
            )
            results_list.append(batch_results)
            
            progress.advance(task)
    
    # Combine all batches
    return pd.concat(results_list, ignore_index=True)


def _display_prediction_summary(
    predictions_df: pd.DataFrame,
    task_type: str,
    input_file: Path,
    output_file: Path
) -> None:
    """Display a summary of the predictions."""
    
    console.print("\n[bold]📊 Prediction Summary[/bold]")
    
    # Basic info table
    info_table = Table(title="Prediction Overview", show_header=True, header_style="bold magenta")
    info_table.add_column("Metric", style="cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Input File", str(input_file))
    info_table.add_row("Output File", str(output_file))
    info_table.add_row("Total Predictions", str(len(predictions_df)))
    info_table.add_row("Task Type", task_type.title())
    
    console.print(info_table)
    
    # Prediction distribution
    predictions = predictions_df['prediction']
    
    if task_type == "classification":
        # Show class distribution
        class_counts = predictions.value_counts().sort_index()
        
        dist_table = Table(title="Prediction Distribution", show_header=True, header_style="bold blue")
        dist_table.add_column("Class", style="cyan")
        dist_table.add_column("Count", style="green")
        dist_table.add_column("Percentage", style="yellow")
        
        for class_val, count in class_counts.items():
            percentage = (count / len(predictions)) * 100
            dist_table.add_row(str(class_val), str(count), f"{percentage:.1f}%")
        
        console.print(dist_table)
        
        # Show confidence statistics if available
        if 'confidence' in predictions_df.columns:
            confidence = predictions_df['confidence']
            console.print(f"\n[bold]Confidence Statistics:[/bold]")
            console.print(f"• Mean Confidence: [green]{confidence.mean():.3f}[/green]")
            console.print(f"• Min Confidence: [yellow]{confidence.min():.3f}[/yellow]")
            console.print(f"• Max Confidence: [green]{confidence.max():.3f}[/green]")
            
            # Low confidence warnings
            low_confidence = (confidence < 0.7).sum()
            if low_confidence > 0:
                console.print(f"• [red]⚠️  {low_confidence} predictions with low confidence (<0.7)[/red]")
    
    else:  # regression
        # Show prediction statistics
        stats_table = Table(title="Prediction Statistics", show_header=True, header_style="bold blue")
        stats_table.add_column("Statistic", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Mean", f"{predictions.mean():.4f}")
        stats_table.add_row("Median", f"{predictions.median():.4f}")
        stats_table.add_row("Std Dev", f"{predictions.std():.4f}")
        stats_table.add_row("Min", f"{predictions.min():.4f}")
        stats_table.add_row("Max", f"{predictions.max():.4f}")
        
        console.print(stats_table)
    
    # Sample predictions
    console.print(f"\n[bold]Sample Predictions (first 5 rows):[/bold]")
    sample_df = predictions_df.head()
    
    # Show only relevant columns for display
    display_cols = ['prediction']
    if 'confidence' in predictions_df.columns:
        display_cols.append('confidence')
    if task_type == "classification" and any(col.startswith('probability_') for col in predictions_df.columns):
        prob_cols = [col for col in predictions_df.columns if col.startswith('probability_')][:3]  # Show first 3 classes
        display_cols.extend(prob_cols)
    
    sample_table = Table(show_header=True, header_style="bold green")
    sample_table.add_column("Row", style="cyan")
    
    for col in display_cols:
        sample_table.add_column(col.replace('_', ' ').title(), style="white")
    
    for idx, row in sample_df.iterrows():
        row_data = [str(idx)]
        for col in display_cols:
            if col in row:
                if 'probability' in col or col == 'confidence':
                    row_data.append(f"{row[col]:.3f}")
                else:
                    row_data.append(str(row[col]))
            else:
                row_data.append("N/A")
        sample_table.add_row(*row_data)
    
    console.print(sample_table)