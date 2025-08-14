"""Configuration management for ML Assistant CLI."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, validator

from mlcli.core.exceptions import ConfigurationError


class DataConfig(BaseModel):
    """Data processing configuration."""
    
    target_column: Optional[str] = None
    feature_columns: Optional[List[str]] = None
    categorical_columns: Optional[List[str]] = None
    numerical_columns: Optional[List[str]] = None
    missing_value_strategy: str = Field(default="auto", pattern="^(auto|drop|mean|median|mode|constant)$")
    scaling_strategy: str = Field(default="standard", pattern="^(standard|minmax|robust|none)$")
    encoding_strategy: str = Field(default="auto", pattern="^(auto|onehot|label|target)$")
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)
    random_state: int = Field(default=42)


class ModelConfig(BaseModel):
    """Model training configuration."""
    
    algorithms: List[str] = Field(default=["logistic_regression", "random_forest"])
    hyperparameter_tuning: bool = Field(default=True)
    cv_folds: int = Field(default=5, ge=3, le=10)
    scoring_metric: str = Field(default="accuracy")
    max_iter: int = Field(default=1000)
    random_state: int = Field(default=42)
    
    @validator("algorithms")
    def validate_algorithms(cls, v: List[str]) -> List[str]:
        valid_algorithms = {
            "logistic_regression", "random_forest", "xgboost", 
            "svm", "naive_bayes", "knn"
        }
        for algo in v:
            if algo not in valid_algorithms:
                raise ValueError(f"Invalid algorithm: {algo}")
        return v


class DeploymentConfig(BaseModel):
    """Deployment configuration."""
    
    provider: str = Field(default="bentocloud")
    service_name: Optional[str] = None
    scaling_min: int = Field(default=1, ge=1)
    scaling_max: int = Field(default=3, ge=1)
    instance_type: str = Field(default="cpu.2")
    strategy: str = Field(default="RollingUpdate")
    environment: Dict[str, str] = Field(default_factory=dict)
    secrets: Dict[str, str] = Field(default_factory=dict)
    timeout: int = Field(default=300, ge=60)


class MLCLIConfig(BaseModel):
    """Main configuration for ML Assistant CLI."""
    
    project_name: str
    version: str = Field(default="0.1.0")
    description: Optional[str] = None
    data: DataConfig = Field(default_factory=DataConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    deployment: DeploymentConfig = Field(default_factory=DeploymentConfig)
    
    class Config:
        extra = "forbid"


def load_config_file(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error reading configuration file: {e}")


def get_config(
    config_file: Optional[Path] = None, 
    project_dir: Optional[Path] = None
) -> MLCLIConfig:
    """Get configuration from file or defaults."""
    project_dir = project_dir or Path.cwd()
    
    # Default config file locations
    config_paths = [
        config_file,
        project_dir / "mlcli.yaml",
        project_dir / "mlcli.yml",
        project_dir / ".mlcli.yaml",
        project_dir / ".mlcli.yml",
    ]
    
    config_data = {}
    config_found = False
    
    for path in config_paths:
        if path and path.exists():
            config_data = load_config_file(path)
            config_found = True
            break
    
    # If no config file found and no project name provided, use directory name
    if not config_found and "project_name" not in config_data:
        config_data["project_name"] = project_dir.name
    
    try:
        return MLCLIConfig(**config_data)
    except Exception as e:
        raise ConfigurationError(f"Invalid configuration: {e}")


def save_config(config: MLCLIConfig, config_path: Path) -> None:
    """Save configuration to YAML file."""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                config.dict(exclude_unset=True), 
                f, 
                default_flow_style=False,
                sort_keys=False
            )
    except Exception as e:
        raise ConfigurationError(f"Error saving configuration: {e}")