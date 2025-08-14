"""Preprocess command for ML Assistant CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from mlcli.core.data import DataProcessor
from mlcli.core.exceptions import DataError
from mlcli.utils.logging import get_logger

logger = get_logger(__name__)
console = Console()

app = typer.Typer()


@app.command()
def main(
    ctx: typer.Context,
    input_file: Path = typer.Option(..., "--input", "-i", help="Input data file path"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    target_column: Optional[str] = typer.Option(None, "--target", "-t", help="Target column name"),
    analyze_only: bool = typer.Option(False, "--analyze-only", help="Only analyze data, don't preprocess"),
) -> None:
    """Preprocess and analyze data for ML training."""
    
    config = ctx.obj["config"]
    project_dir = ctx.obj["project_dir"]
    
    # Set default output directory
    if output_dir is None:
        output_dir = project_dir / "data" / "processed"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize data processor
        processor = DataProcessor(config.data)
        
        # Load data
        console.print(f"[blue]Loading data from:[/blue] {input_file}")
        df = processor.load_data(input_file)
        
        # Analyze data
        console.print("[blue]Analyzing data...[/blue]")
        analysis = processor.analyze_data(df)
        
        # Display analysis results
        _display_analysis(analysis)
        
        if analyze_only:
            console.print("[green]✓[/green] Data analysis complete")
            return
        
        # Preprocess data
        console.print("[blue]Preprocessing data...[/blue]")
        
        # Override target column if provided
        if target_column:
            config.data.target_column = target_column
        
        X_processed, y_processed, preprocessing_report = processor.preprocess_data(df, target_column)
        
        # Split data
        X_train, X_test, y_train, y_test = processor.split_data(X_processed, y_processed)
        
        # Save processed data
        train_path = output_dir / "train.csv"
        test_path = output_dir / "test.csv"
        
        train_data = X_train.copy()
        train_data[config.data.target_column] = y_train
        train_data.to_csv(train_path, index=False)
        
        test_data = X_test.copy()
        test_data[config.data.target_column] = y_test
        test_data.to_csv(test_path, index=False)
        
        # Save preprocessing artifacts
        processor.save_preprocessing_artifacts(output_dir, preprocessing_report)
        
        # Display results
        console.print(f"[green]✓[/green] Preprocessing complete")
        console.print(f"[green]✓[/green] Training data saved: {train_path} ({len(X_train)} samples)")
        console.print(f"[green]✓[/green] Test data saved: {test_path} ({len(X_test)} samples)")
        console.print(f"[green]✓[/green] Data profile saved: {output_dir / 'data_profile.json'}")
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Run [cyan]mlcli train[/cyan] to start training models")
        console.print("2. Run [cyan]mlcli evaluate[/cyan] to evaluate model performance")
        
    except DataError as e:
        console.print(f"[red]Data Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
        raise typer.Exit(1)


def _display_analysis(analysis: dict) -> None:
    """Display data analysis results in a formatted table."""
    
    # Basic info table
    info_table = Table(title="Dataset Overview", show_header=True, header_style="bold magenta")
    info_table.add_column("Metric", style="cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Rows", str(analysis["shape"][0]))
    info_table.add_row("Columns", str(analysis["shape"][1]))
    info_table.add_row("Duplicates", str(analysis["duplicates"]))
    info_table.add_row("Memory Usage", f"{analysis['memory_usage'] / 1024 / 1024:.2f} MB")
    
    console.print(info_table)
    
    # Missing values table
    missing_data = [(col, count, f"{pct:.1f}%") 
                   for col, count in analysis["missing_values"].items() 
                   if count > 0]
    
    if missing_data:
        missing_table = Table(title="Missing Values", show_header=True, header_style="bold red")
        missing_table.add_column("Column", style="cyan")
        missing_table.add_column("Count", style="white")
        missing_table.add_column("Percentage", style="yellow")
        
        for col, count, pct in missing_data:
            missing_table.add_row(col, str(count), pct)
        
        console.print(missing_table)
    
    # Data quality issues
    issues = analysis.get("quality_issues", {})
    if any(issues.values()):
        console.print("\n[bold red]⚠️  Data Quality Issues Detected:[/bold red]")
        
        for issue_type, issue_list in issues.items():
            if issue_list:
                issue_name = issue_type.replace("_", " ").title()
                console.print(f"[yellow]• {issue_name}:[/yellow] {', '.join(map(str, issue_list))}")
    
    # Column types
    if "numeric_columns" in analysis:
        console.print(f"\n[bold]Numeric columns ({len(analysis['numeric_columns'])}):[/bold] {', '.join(analysis['numeric_columns'])}")
    
    if "categorical_columns" in analysis:
        console.print(f"[bold]Categorical columns ({len(analysis['categorical_columns'])}):[/bold] {', '.join(analysis['categorical_columns'])}")