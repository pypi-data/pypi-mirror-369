"""Initialize command for ML Assistant CLI."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from mlcli.core.config import MLCLIConfig, save_config
from mlcli.core.exceptions import ConfigurationError
from mlcli.utils.logging import get_logger

logger = get_logger(__name__)
console = Console()

app = typer.Typer()


@app.command()
def main(
    ctx: typer.Context,
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing configuration"),
) -> None:
    """Initialize a new ML project with configuration and directory structure."""
    
    project_dir = ctx.obj["project_dir"]
    config_file = project_dir / "mlcli.yaml"
    
    # Check if project already exists
    if config_file.exists() and not force:
        if not Confirm.ask(f"Project configuration already exists at {config_file}. Overwrite?"):
            console.print("[yellow]Initialization cancelled.[/yellow]")
            raise typer.Exit(0)
    
    # Interactive project setup
    if not name:
        name = Prompt.ask(
            "Project name", 
            default=project_dir.name,
            show_default=True
        )
    
    if not description:
        description = Prompt.ask(
            "Project description (optional)", 
            default="",
            show_default=False
        )
    
    # Create project structure
    try:
        _create_project_structure(project_dir)
        
        # Create configuration
        config = MLCLIConfig(
            project_name=name,
            description=description or None
        )
        
        save_config(config, config_file)
        
        console.print(f"[green]✓[/green] Initialized ML project: [bold]{name}[/bold]")
        console.print(f"[green]✓[/green] Configuration saved to: {config_file}")
        console.print(f"[green]✓[/green] Project structure created in: {project_dir}")
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Add your dataset to the [cyan]data/raw/[/cyan] directory")
        console.print("2. Run [cyan]mlcli preprocess --input data/raw/your_data.csv[/cyan]")
        console.print("3. Run [cyan]mlcli train[/cyan] to start training models")
        
    except Exception as e:
        raise ConfigurationError(f"Failed to initialize project: {e}")


def _create_project_structure(project_dir: Path) -> None:
    """Create the standard ML project directory structure."""
    
    directories = [
        "data/raw",
        "data/processed",
        "data/external",
        "models",
        "notebooks",
        "reports/figures",
        "src",
        "tests",
        "deployments",
        "logs",
    ]
    
    for dir_path in directories:
        full_path = project_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep files for empty directories
        gitkeep = full_path / ".gitkeep"
        if not any(full_path.iterdir()):
            gitkeep.touch()
    
    # Create essential files
    files_to_create = {
        "README.md": _get_readme_template(),
        ".gitignore": _get_gitignore_template(),
        "requirements.txt": _get_requirements_template(),
    }
    
    for filename, content in files_to_create.items():
        file_path = project_dir / filename
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")


def _get_readme_template() -> str:
    """Get README.md template."""
    return """# ML Project

This project was initialized with ML Assistant CLI.

## Getting Started

1. Add your dataset to `data/raw/`
2. Run preprocessing: `mlcli preprocess --input data/raw/your_data.csv`
3. Train models: `mlcli train`
4. Evaluate performance: `mlcli evaluate`
5. Get suggestions: `mlcli suggest`
6. Make predictions: `mlcli predict --input new_data.csv`

## Project Structure

```
├── data/
│   ├── raw/          # Original, immutable data
│   ├── processed/    # Cleaned and preprocessed data
│   └── external/     # External datasets
├── models/           # Trained models and artifacts
├── notebooks/        # Jupyter notebooks for exploration
├── reports/          # Analysis reports and figures
├── src/              # Source code
├── tests/            # Unit tests
├── deployments/      # Deployment configurations
└── logs/             # Application logs
```

## Configuration

Edit `mlcli.yaml` to customize your ML pipeline settings.
"""


def _get_gitignore_template() -> str:
    """Get .gitignore template."""
    return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# ML specific
*.pkl
*.joblib
*.h5
*.hdf5
models/checkpoints/
logs/*.log
data/raw/*.csv
data/raw/*.json
data/raw/*.parquet

# BentoML
bentofile.yaml
bentos/
"""


def _get_requirements_template() -> str:
    """Get requirements.txt template."""
    return """# ML Assistant CLI
mlcli

# Data processing
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# ML libraries
xgboost>=1.7.0

# Deployment
bentoml>=1.2.0

# Utilities
pyyaml>=6.0
rich>=13.0.0
"""