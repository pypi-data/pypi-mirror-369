"""Suggest command for ML Assistant CLI."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List

import pandas as pd
import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mlcli.core.exceptions import DataError
from mlcli.utils.logging import get_logger

logger = get_logger(__name__)
console = Console()

app = typer.Typer()


@app.command()
def main(
    ctx: typer.Context,
    data_profile: Optional[Path] = typer.Option(None, "--data-profile", help="Data profile JSON file"),
    evaluation_report: Optional[Path] = typer.Option(None, "--evaluation", help="Evaluation report JSON file"),
    training_summary: Optional[Path] = typer.Option(None, "--training", help="Training summary JSON file"),
) -> None:
    """Get AI-guided suggestions for improving your ML pipeline."""
    
    config = ctx.obj["config"]
    project_dir = ctx.obj["project_dir"]
    
    # Set default paths
    if data_profile is None:
        data_profile = project_dir / "data" / "processed" / "data_profile.json"
    
    if evaluation_report is None:
        evaluation_report = project_dir / "reports" / "evaluation_report.json"
    
    if training_summary is None:
        training_summary = project_dir / "models" / "training_summary.json"
    
    console.print("[blue]🤖 Analyzing your ML pipeline...[/blue]")
    
    # Load available reports
    reports = {}
    
    if data_profile.exists():
        with open(data_profile, 'r') as f:
            reports['data_profile'] = json.load(f)
        console.print(f"[green]✓[/green] Loaded data profile")
    
    if evaluation_report.exists():
        with open(evaluation_report, 'r') as f:
            reports['evaluation'] = json.load(f)
        console.print(f"[green]✓[/green] Loaded evaluation report")
    
    if training_summary.exists():
        with open(training_summary, 'r') as f:
            reports['training'] = json.load(f)
        console.print(f"[green]✓[/green] Loaded training summary")
    
    if not reports:
        console.print("[yellow]⚠️  No reports found. Run the following commands first:[/yellow]")
        console.print("1. [cyan]mlcli preprocess[/cyan] - to generate data profile")
        console.print("2. [cyan]mlcli train[/cyan] - to generate training summary")
        console.print("3. [cyan]mlcli evaluate[/cyan] - to generate evaluation report")
        raise typer.Exit(0)
    
    # Generate suggestions
    suggestions = _generate_suggestions(reports, config)
    
    # Display suggestions
    _display_suggestions(suggestions)
    
    # Save suggestions
    suggestions_path = project_dir / "reports" / "suggestions.json"
    suggestions_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(suggestions_path, 'w') as f:
        json.dump(suggestions, f, indent=2)
    
    console.print(f"\n[green]✓[/green] Suggestions saved to: {suggestions_path}")


def _generate_suggestions(reports: Dict[str, Any], config) -> Dict[str, Any]:
    """Generate AI-guided suggestions based on available reports."""
    
    suggestions = {
        "data_suggestions": [],
        "model_suggestions": [],
        "performance_suggestions": [],
        "deployment_suggestions": [],
        "priority_actions": []
    }
    
    # Data-based suggestions
    if 'data_profile' in reports:
        data_suggestions = _analyze_data_quality(reports['data_profile'])
        suggestions["data_suggestions"].extend(data_suggestions)
    
    # Model-based suggestions
    if 'training' in reports:
        model_suggestions = _analyze_model_performance(reports['training'])
        suggestions["model_suggestions"].extend(model_suggestions)
    
    # Performance-based suggestions
    if 'evaluation' in reports:
        performance_suggestions = _analyze_evaluation_results(reports['evaluation'])
        suggestions["performance_suggestions"].extend(performance_suggestions)
    
    # Deployment suggestions
    deployment_suggestions = _generate_deployment_suggestions(reports, config)
    suggestions["deployment_suggestions"].extend(deployment_suggestions)
    
    # Priority actions
    priority_actions = _determine_priority_actions(suggestions)
    suggestions["priority_actions"] = priority_actions
    
    return suggestions


def _analyze_data_quality(data_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze data quality and suggest improvements."""
    suggestions = []
    
    # Check data size
    original_shape = data_profile.get('original_shape', [0, 0])
    n_samples, n_features = original_shape
    
    if n_samples < 1000:
        suggestions.append({
            "category": "Data Size",
            "priority": "High",
            "issue": f"Small dataset ({n_samples} samples)",
            "suggestion": "Consider collecting more data or using data augmentation techniques",
            "impact": "More data typically leads to better model performance"
        })
    
    if n_features > n_samples:
        suggestions.append({
            "category": "Dimensionality",
            "priority": "High", 
            "issue": f"More features ({n_features}) than samples ({n_samples})",
            "suggestion": "Apply feature selection or dimensionality reduction (PCA, feature selection)",
            "impact": "Reduces overfitting and improves model generalization"
        })
    
    # Check feature engineering
    processed_shape = data_profile.get('processed_shape', [0, 0])
    if processed_shape[1] > original_shape[1] * 2:
        suggestions.append({
            "category": "Feature Engineering",
            "priority": "Medium",
            "issue": f"Many engineered features ({processed_shape[1]} from {original_shape[1]})",
            "suggestion": "Consider feature selection to reduce dimensionality",
            "impact": "Prevents overfitting and improves interpretability"
        })
    
    # Check categorical columns
    categorical_cols = data_profile.get('categorical_columns', [])
    if len(categorical_cols) > 5:
        suggestions.append({
            "category": "Categorical Features",
            "priority": "Medium",
            "issue": f"Many categorical features ({len(categorical_cols)})",
            "suggestion": "Consider target encoding or feature selection for high-cardinality categories",
            "impact": "Reduces model complexity and training time"
        })
    
    return suggestions


def _analyze_model_performance(training_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze model training results and suggest improvements."""
    suggestions = []
    
    model_scores = training_summary.get('model_scores', {})
    best_score = training_summary.get('best_score', 0)
    task_type = training_summary.get('task_type', 'classification')
    
    # Check if performance is poor
    threshold = 0.7 if task_type == 'classification' else 0.5
    if best_score < threshold:
        suggestions.append({
            "category": "Model Performance",
            "priority": "High",
            "issue": f"Low {task_type} performance ({best_score:.3f})",
            "suggestion": "Try advanced algorithms (XGBoost, Neural Networks) or ensemble methods",
            "impact": "Significant improvement in model accuracy"
        })
    
    # Check model diversity
    if len(model_scores) < 3:
        suggestions.append({
            "category": "Model Selection",
            "priority": "Medium",
            "issue": "Limited model algorithms tested",
            "suggestion": "Try more diverse algorithms (SVM, XGBoost, Neural Networks)",
            "impact": "Find the best algorithm for your specific problem"
        })
    
    # Check score variance
    if len(model_scores) > 1:
        scores = list(model_scores.values())
        score_std = np.std(scores)
        if score_std < 0.01:
            suggestions.append({
                "category": "Model Diversity",
                "priority": "Low",
                "issue": "All models perform similarly",
                "suggestion": "Data might be too simple or need feature engineering",
                "impact": "Better feature engineering could improve all models"
            })
    
    return suggestions


def _analyze_evaluation_results(evaluation_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze evaluation results and suggest improvements."""
    suggestions = []
    
    metrics = evaluation_report.get('metrics', {})
    task_type = evaluation_report.get('task_type', 'classification')
    
    if task_type == 'classification':
        accuracy = metrics.get('accuracy', 0)
        precision = metrics.get('precision', 0)
        recall = metrics.get('recall', 0)
        f1 = metrics.get('f1_score', 0)
        
        # Check for class imbalance
        if abs(precision - recall) > 0.2:
            suggestions.append({
                "category": "Class Imbalance",
                "priority": "High",
                "issue": f"Large gap between precision ({precision:.3f}) and recall ({recall:.3f})",
                "suggestion": "Address class imbalance with SMOTE, class weights, or stratified sampling",
                "impact": "Better balanced performance across all classes"
            })
        
        # Check overall performance
        if accuracy < 0.8:
            suggestions.append({
                "category": "Classification Performance",
                "priority": "High",
                "issue": f"Low accuracy ({accuracy:.3f})",
                "suggestion": "Try feature engineering, hyperparameter tuning, or ensemble methods",
                "impact": "Significant improvement in prediction accuracy"
            })
    
    else:  # regression
        r2 = metrics.get('r2_score', 0)
        mape = metrics.get('mean_absolute_percentage_error', 100)
        
        if r2 < 0.5:
            suggestions.append({
                "category": "Regression Performance",
                "priority": "High",
                "issue": f"Low R² score ({r2:.3f})",
                "suggestion": "Try polynomial features, regularization, or advanced algorithms",
                "impact": "Better explanation of target variable variance"
            })
        
        if mape > 20:
            suggestions.append({
                "category": "Prediction Accuracy",
                "priority": "Medium",
                "issue": f"High prediction error ({mape:.1f}% MAPE)",
                "suggestion": "Consider feature scaling, outlier removal, or ensemble methods",
                "impact": "More accurate predictions for business use"
            })
    
    return suggestions


def _generate_deployment_suggestions(reports: Dict[str, Any], config) -> List[Dict[str, Any]]:
    """Generate deployment-related suggestions."""
    suggestions = []
    
    # Model size and complexity
    if 'training' in reports:
        model_scores = reports['training'].get('model_scores', {})
        best_model = reports['training'].get('best_model', '')
        
        if 'xgboost' in best_model.lower():
            suggestions.append({
                "category": "Deployment",
                "priority": "Medium",
                "issue": "XGBoost models can be large",
                "suggestion": "Consider model compression or simpler alternatives for production",
                "impact": "Faster inference and lower resource usage"
            })
    
    # Data preprocessing complexity
    if 'data_profile' in reports:
        n_features = reports['data_profile'].get('processed_shape', [0, 0])[1]
        if n_features > 100:
            suggestions.append({
                "category": "Deployment",
                "priority": "Low",
                "issue": f"Many features ({n_features}) may slow inference",
                "suggestion": "Consider feature selection for production deployment",
                "impact": "Faster prediction response times"
            })
    
    # General deployment readiness
    suggestions.append({
        "category": "Deployment",
        "priority": "Medium",
        "issue": "Model ready for deployment",
        "suggestion": "Use 'mlcli package' to create BentoML service for deployment",
        "impact": "Easy deployment to cloud platforms"
    })
    
    return suggestions


def _determine_priority_actions(suggestions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Determine the top priority actions based on all suggestions."""
    
    all_suggestions = []
    for category, suggestion_list in suggestions.items():
        if category != "priority_actions":
            all_suggestions.extend(suggestion_list)
    
    # Sort by priority (High > Medium > Low)
    priority_order = {"High": 3, "Medium": 2, "Low": 1}
    all_suggestions.sort(key=lambda x: priority_order.get(x.get("priority", "Low"), 1), reverse=True)
    
    # Return top 5 priority actions
    return all_suggestions[:5]


def _display_suggestions(suggestions: Dict[str, Any]) -> None:
    """Display suggestions in a formatted way."""
    
    console.print("\n[bold]🤖 AI-Guided Suggestions for Your ML Pipeline[/bold]")
    
    # Priority Actions
    priority_actions = suggestions.get("priority_actions", [])
    if priority_actions:
        console.print("\n[bold red]🔥 Top Priority Actions[/bold red]")
        
        for i, action in enumerate(priority_actions, 1):
            priority_color = {
                "High": "red",
                "Medium": "yellow", 
                "Low": "blue"
            }.get(action.get("priority", "Low"), "white")
            
            panel_content = f"""
[bold]Issue:[/bold] {action.get('issue', 'N/A')}
[bold]Suggestion:[/bold] {action.get('suggestion', 'N/A')}
[bold]Impact:[/bold] {action.get('impact', 'N/A')}
            """
            
            console.print(Panel(
                panel_content.strip(),
                title=f"{i}. {action.get('category', 'General')} [{priority_color}]{action.get('priority', 'Low')}[/{priority_color}]",
                border_style=priority_color
            ))
    
    # Detailed suggestions by category
    categories = ["data_suggestions", "model_suggestions", "performance_suggestions", "deployment_suggestions"]
    category_titles = {
        "data_suggestions": "📊 Data Quality Improvements",
        "model_suggestions": "🤖 Model Selection & Training",
        "performance_suggestions": "📈 Performance Optimization", 
        "deployment_suggestions": "🚀 Deployment Recommendations"
    }
    
    for category in categories:
        category_suggestions = suggestions.get(category, [])
        if category_suggestions:
            console.print(f"\n[bold]{category_titles[category]}[/bold]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Priority", style="cyan", width=8)
            table.add_column("Issue", style="red", width=30)
            table.add_column("Suggestion", style="green", width=40)
            table.add_column("Impact", style="blue", width=30)
            
            for suggestion in category_suggestions:
                priority = suggestion.get("priority", "Low")
                priority_style = {
                    "High": "[red]High[/red]",
                    "Medium": "[yellow]Medium[/yellow]",
                    "Low": "[blue]Low[/blue]"
                }.get(priority, priority)
                
                table.add_row(
                    priority_style,
                    suggestion.get("issue", "N/A"),
                    suggestion.get("suggestion", "N/A"),
                    suggestion.get("impact", "N/A")
                )
            
            console.print(table)
    
    # Summary
    total_suggestions = sum(len(suggestions.get(cat, [])) for cat in categories)
    high_priority = sum(1 for cat in categories for s in suggestions.get(cat, []) if s.get("priority") == "High")
    
    summary = f"""
[bold]Summary:[/bold]
• Total suggestions: {total_suggestions}
• High priority actions: {high_priority}
• Focus on high priority items first for maximum impact
    """
    
    console.print(Panel(summary.strip(), title="Suggestion Summary", border_style="green"))