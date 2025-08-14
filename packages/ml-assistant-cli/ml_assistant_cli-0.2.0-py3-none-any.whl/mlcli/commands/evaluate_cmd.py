"""Evaluate command for ML Assistant CLI."""

import json
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd
import numpy as np
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve, precision_recall_curve,
    mean_squared_error, mean_absolute_error, r2_score
)

from mlcli.core.models import ModelTrainer
from mlcli.core.exceptions import ModelError, DataError
from mlcli.utils.logging import get_logger

logger = get_logger(__name__)
console = Console()

app = typer.Typer()


@app.command()
def main(
    ctx: typer.Context,
    test_data: Optional[Path] = typer.Option(None, "--test-data", "-t", help="Test data file path"),
    model_path: Optional[Path] = typer.Option(None, "--model", "-m", help="Model file path"),
    target_column: Optional[str] = typer.Option(None, "--target", help="Target column name"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for reports"),
) -> None:
    """Evaluate trained models and generate comprehensive performance reports."""
    
    config = ctx.obj["config"]
    project_dir = ctx.obj["project_dir"]
    
    # Set default paths
    if test_data is None:
        test_data = project_dir / "data" / "processed" / "test.csv"
    
    if model_path is None:
        model_path = project_dir / "models" / "best_model.pkl"
    
    if target_column is None:
        target_column = config.data.target_column
    
    if output_dir is None:
        output_dir = project_dir / "reports"
    
    # Validate inputs
    if not test_data.exists():
        console.print(f"[red]Error:[/red] Test data not found: {test_data}")
        console.print("[yellow]Hint:[/yellow] Run [cyan]mlcli preprocess[/cyan] first to generate test data")
        raise typer.Exit(1)
    
    if not model_path.exists():
        console.print(f"[red]Error:[/red] Model not found: {model_path}")
        console.print("[yellow]Hint:[/yellow] Run [cyan]mlcli train[/cyan] first to train models")
        raise typer.Exit(1)
    
    if not target_column:
        console.print("[red]Error:[/red] Target column not specified")
        console.print("[yellow]Hint:[/yellow] Use --target option or set target_column in mlcli.yaml")
        raise typer.Exit(1)
    
    try:
        # Load test data
        console.print(f"[blue]Loading test data from:[/blue] {test_data}")
        test_df = pd.read_csv(test_data)
        
        if target_column not in test_df.columns:
            raise DataError(f"Target column '{target_column}' not found in test data")
        
        # Separate features and target
        X_test = test_df.drop(columns=[target_column])
        y_test = test_df[target_column]
        
        # Load model
        console.print(f"[blue]Loading model from:[/blue] {model_path}")
        trainer = ModelTrainer(config.model)
        model = trainer.load_model(model_path)
        
        # Detect task type
        task_type = trainer.detect_task_type(y_test)
        
        # Make predictions
        console.print("[blue]Making predictions...[/blue]")
        y_pred = trainer.predict(model, X_test)
        y_pred_proba = trainer.predict_proba(model, X_test)
        
        # Generate evaluation report
        console.print("[blue]Generating evaluation report...[/blue]")
        evaluation_report = _generate_evaluation_report(
            y_test, y_pred, y_pred_proba, task_type
        )
        
        # Display results
        _display_evaluation_results(evaluation_report, task_type)
        
        # Save reports
        output_dir.mkdir(parents=True, exist_ok=True)
        _save_evaluation_report(evaluation_report, output_dir)
        
        # Generate visualizations
        if task_type == "classification":
            _generate_classification_plots(y_test, y_pred, y_pred_proba, output_dir)
        else:
            _generate_regression_plots(y_test, y_pred, output_dir)
        
        console.print(f"[green]✓[/green] Evaluation complete!")
        console.print(f"[green]✓[/green] Reports saved to: {output_dir}")
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Run [cyan]mlcli suggest[/cyan] to get improvement recommendations")
        console.print("2. Check the reports directory for detailed visualizations")
        console.print("3. Run [cyan]mlcli predict --input new_data.csv[/cyan] to make predictions")
        
    except (ModelError, DataError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        raise typer.Exit(1)


def _generate_evaluation_report(
    y_true: pd.Series, 
    y_pred: np.ndarray, 
    y_pred_proba: Optional[np.ndarray],
    task_type: str
) -> Dict[str, Any]:
    """Generate comprehensive evaluation report."""
    
    report = {
        "task_type": task_type,
        "sample_size": len(y_true),
        "predictions_made": len(y_pred)
    }
    
    if task_type == "classification":
        # Classification metrics
        report["metrics"] = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
        }
        
        # ROC AUC for binary classification
        if len(np.unique(y_true)) == 2 and y_pred_proba is not None:
            try:
                report["metrics"]["roc_auc"] = float(roc_auc_score(y_true, y_pred_proba[:, 1]))
            except:
                report["metrics"]["roc_auc"] = None
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        report["confusion_matrix"] = cm.tolist()
        
        # Classification report
        report["classification_report"] = classification_report(y_true, y_pred, output_dict=True)
        
    else:
        # Regression metrics
        report["metrics"] = {
            "r2_score": float(r2_score(y_true, y_pred)),
            "mean_squared_error": float(mean_squared_error(y_true, y_pred)),
            "root_mean_squared_error": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "mean_absolute_error": float(mean_absolute_error(y_true, y_pred))
        }
        
        # Additional regression metrics
        report["metrics"]["mean_absolute_percentage_error"] = float(
            np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        )
    
    return report


def _display_evaluation_results(report: Dict[str, Any], task_type: str) -> None:
    """Display evaluation results in formatted tables."""
    
    # Metrics table
    table = Table(title="Model Performance Metrics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Interpretation", style="white")
    
    metrics = report["metrics"]
    
    if task_type == "classification":
        interpretations = {
            "accuracy": _interpret_accuracy(metrics["accuracy"]),
            "precision": _interpret_precision(metrics["precision"]),
            "recall": _interpret_recall(metrics["recall"]),
            "f1_score": _interpret_f1(metrics["f1_score"]),
            "roc_auc": _interpret_roc_auc(metrics.get("roc_auc"))
        }
        
        for metric, value in metrics.items():
            if value is not None:
                table.add_row(
                    metric.replace("_", " ").title(),
                    f"{value:.4f}",
                    interpretations.get(metric, "")
                )
    else:
        interpretations = {
            "r2_score": _interpret_r2(metrics["r2_score"]),
            "mean_squared_error": "Lower is better",
            "root_mean_squared_error": "Lower is better (same units as target)",
            "mean_absolute_error": "Lower is better (same units as target)",
            "mean_absolute_percentage_error": _interpret_mape(metrics["mean_absolute_percentage_error"])
        }
        
        for metric, value in metrics.items():
            display_value = f"{value:.4f}"
            if "percentage" in metric:
                display_value = f"{value:.2f}%"
            
            table.add_row(
                metric.replace("_", " ").title(),
                display_value,
                interpretations.get(metric, "")
            )
    
    console.print(table)
    
    # Summary panel
    if task_type == "classification":
        accuracy = metrics["accuracy"]
        if accuracy >= 0.9:
            performance = "[green]Excellent[/green]"
        elif accuracy >= 0.8:
            performance = "[blue]Good[/blue]"
        elif accuracy >= 0.7:
            performance = "[yellow]Fair[/yellow]"
        else:
            performance = "[red]Needs Improvement[/red]"
    else:
        r2 = metrics["r2_score"]
        if r2 >= 0.9:
            performance = "[green]Excellent[/green]"
        elif r2 >= 0.7:
            performance = "[blue]Good[/blue]"
        elif r2 >= 0.5:
            performance = "[yellow]Fair[/yellow]"
        else:
            performance = "[red]Needs Improvement[/red]"
    
    summary = f"""
[bold]Overall Performance:[/bold] {performance}
[bold]Sample Size:[/bold] {report['sample_size']} samples
[bold]Task Type:[/bold] {task_type.title()}
    """
    
    console.print(Panel(summary.strip(), title="Evaluation Summary", border_style="blue"))


def _interpret_accuracy(accuracy: float) -> str:
    """Interpret accuracy score."""
    if accuracy >= 0.95:
        return "Excellent"
    elif accuracy >= 0.85:
        return "Very Good"
    elif accuracy >= 0.75:
        return "Good"
    elif accuracy >= 0.65:
        return "Fair"
    else:
        return "Poor"


def _interpret_precision(precision: float) -> str:
    """Interpret precision score."""
    if precision >= 0.9:
        return "High precision"
    elif precision >= 0.7:
        return "Good precision"
    else:
        return "Low precision"


def _interpret_recall(recall: float) -> str:
    """Interpret recall score."""
    if recall >= 0.9:
        return "High recall"
    elif recall >= 0.7:
        return "Good recall"
    else:
        return "Low recall"


def _interpret_f1(f1: float) -> str:
    """Interpret F1 score."""
    if f1 >= 0.9:
        return "Excellent balance"
    elif f1 >= 0.7:
        return "Good balance"
    else:
        return "Poor balance"


def _interpret_roc_auc(roc_auc: Optional[float]) -> str:
    """Interpret ROC AUC score."""
    if roc_auc is None:
        return "N/A"
    if roc_auc >= 0.9:
        return "Excellent discrimination"
    elif roc_auc >= 0.8:
        return "Good discrimination"
    elif roc_auc >= 0.7:
        return "Fair discrimination"
    else:
        return "Poor discrimination"


def _interpret_r2(r2: float) -> str:
    """Interpret R² score."""
    if r2 >= 0.9:
        return "Excellent fit"
    elif r2 >= 0.7:
        return "Good fit"
    elif r2 >= 0.5:
        return "Moderate fit"
    else:
        return "Poor fit"


def _interpret_mape(mape: float) -> str:
    """Interpret Mean Absolute Percentage Error."""
    if mape <= 10:
        return "Excellent accuracy"
    elif mape <= 20:
        return "Good accuracy"
    elif mape <= 50:
        return "Reasonable accuracy"
    else:
        return "Poor accuracy"


def _save_evaluation_report(report: Dict[str, Any], output_dir: Path) -> None:
    """Save evaluation report to JSON file."""
    report_path = output_dir / "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    logger.info(f"Evaluation report saved to: {report_path}")


def _generate_classification_plots(
    y_true: pd.Series, 
    y_pred: np.ndarray, 
    y_pred_proba: Optional[np.ndarray],
    output_dir: Path
) -> None:
    """Generate classification visualization plots."""
    try:
        plt.style.use('default')
        
        # Confusion Matrix
        fig, ax = plt.subplots(figsize=(8, 6))
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_title('Confusion Matrix')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        plt.tight_layout()
        plt.savefig(output_dir / "confusion_matrix.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # ROC Curve (binary classification only)
        if len(np.unique(y_true)) == 2 and y_pred_proba is not None:
            fig, ax = plt.subplots(figsize=(8, 6))
            fpr, tpr, _ = roc_curve(y_true, y_pred_proba[:, 1])
            roc_auc = roc_auc_score(y_true, y_pred_proba[:, 1])
            
            ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
            ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_xlabel('False Positive Rate')
            ax.set_ylabel('True Positive Rate')
            ax.set_title('Receiver Operating Characteristic (ROC) Curve')
            ax.legend(loc="lower right")
            plt.tight_layout()
            plt.savefig(output_dir / "roc_curve.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        logger.info("Classification plots generated successfully")
        
    except Exception as e:
        logger.warning(f"Error generating classification plots: {e}")


def _generate_regression_plots(
    y_true: pd.Series, 
    y_pred: np.ndarray,
    output_dir: Path
) -> None:
    """Generate regression visualization plots."""
    try:
        plt.style.use('default')
        
        # Actual vs Predicted
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(y_true, y_pred, alpha=0.6)
        ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        ax.set_xlabel('Actual Values')
        ax.set_ylabel('Predicted Values')
        ax.set_title('Actual vs Predicted Values')
        
        # Add R² score to plot
        r2 = r2_score(y_true, y_pred)
        ax.text(0.05, 0.95, f'R² = {r2:.3f}', transform=ax.transAxes, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_dir / "actual_vs_predicted.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Residuals plot
        fig, ax = plt.subplots(figsize=(8, 6))
        residuals = y_true - y_pred
        ax.scatter(y_pred, residuals, alpha=0.6)
        ax.axhline(y=0, color='r', linestyle='--')
        ax.set_xlabel('Predicted Values')
        ax.set_ylabel('Residuals')
        ax.set_title('Residuals Plot')
        plt.tight_layout()
        plt.savefig(output_dir / "residuals_plot.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Regression plots generated successfully")
        
    except Exception as e:
        logger.warning(f"Error generating regression plots: {e}")