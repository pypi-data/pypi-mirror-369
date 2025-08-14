"""Model training and hyperparameter optimization module."""

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
import xgboost as xgb

from mlcli.core.config import ModelConfig
from mlcli.core.exceptions import ModelError
from mlcli.utils.logging import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """Advanced model training with hyperparameter optimization."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.models = {}
        self.best_model = None
        self.best_score = None
        self.task_type = None
        
    def get_model_definitions(self, task_type: str) -> Dict[str, Dict[str, Any]]:
        """Get model definitions with hyperparameters for the task type."""
        
        if task_type == "classification":
            return {
                "logistic_regression": {
                    "model": LogisticRegression(random_state=self.config.random_state, max_iter=self.config.max_iter),
                    "params": {
                        "C": [0.1, 1.0, 10.0, 100.0],
                        "penalty": ["l1", "l2"],
                        "solver": ["liblinear", "saga"]
                    }
                },
                "random_forest": {
                    "model": RandomForestClassifier(random_state=self.config.random_state),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [None, 10, 20, 30],
                        "min_samples_split": [2, 5, 10],
                        "min_samples_leaf": [1, 2, 4]
                    }
                },
                "xgboost": {
                    "model": xgb.XGBClassifier(random_state=self.config.random_state, eval_metric='logloss'),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [3, 6, 9],
                        "learning_rate": [0.01, 0.1, 0.2],
                        "subsample": [0.8, 0.9, 1.0]
                    }
                },
                "svm": {
                    "model": SVC(random_state=self.config.random_state, probability=True),
                    "params": {
                        "C": [0.1, 1.0, 10.0],
                        "kernel": ["rbf", "linear"],
                        "gamma": ["scale", "auto"]
                    }
                },
                "naive_bayes": {
                    "model": GaussianNB(),
                    "params": {
                        "var_smoothing": [1e-9, 1e-8, 1e-7, 1e-6]
                    }
                },
                "knn": {
                    "model": KNeighborsClassifier(),
                    "params": {
                        "n_neighbors": [3, 5, 7, 9],
                        "weights": ["uniform", "distance"],
                        "metric": ["euclidean", "manhattan"]
                    }
                }
            }
        else:  # regression
            return {
                "linear_regression": {
                    "model": LinearRegression(),
                    "params": {
                        "fit_intercept": [True, False],
                        "positive": [True, False]
                    }
                },
                "random_forest": {
                    "model": RandomForestRegressor(random_state=self.config.random_state),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [None, 10, 20, 30],
                        "min_samples_split": [2, 5, 10],
                        "min_samples_leaf": [1, 2, 4]
                    }
                },
                "xgboost": {
                    "model": xgb.XGBRegressor(random_state=self.config.random_state),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [3, 6, 9],
                        "learning_rate": [0.01, 0.1, 0.2],
                        "subsample": [0.8, 0.9, 1.0]
                    }
                },
                "svm": {
                    "model": SVR(),
                    "params": {
                        "C": [0.1, 1.0, 10.0],
                        "kernel": ["rbf", "linear"],
                        "gamma": ["scale", "auto"]
                    }
                },
                "knn": {
                    "model": KNeighborsRegressor(),
                    "params": {
                        "n_neighbors": [3, 5, 7, 9],
                        "weights": ["uniform", "distance"],
                        "metric": ["euclidean", "manhattan"]
                    }
                }
            }
    
    def detect_task_type(self, y: pd.Series) -> str:
        """Detect if the task is classification or regression."""
        unique_values = y.nunique()
        
        # If target has few unique values and is numeric, likely classification
        if unique_values <= 10 and y.dtype in ['int64', 'int32', 'float64', 'float32']:
            # Check if values are mostly integers
            if y.dtype in ['int64', 'int32'] or (y % 1 == 0).all():
                return "classification"
        
        # If target is object/string type, definitely classification
        if y.dtype == 'object' or y.dtype.name == 'category':
            return "classification"
        
        # If many unique values, likely regression
        if unique_values > 10:
            return "regression"
        
        # Default to classification for small datasets
        return "classification"
    
    def train_models(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """Train multiple models with hyperparameter optimization."""
        
        # Detect task type
        self.task_type = self.detect_task_type(y_train)
        logger.info(f"Detected task type: {self.task_type}")
        
        # Get model definitions
        model_definitions = self.get_model_definitions(self.task_type)
        
        # Filter models based on config
        available_models = {
            name: definition for name, definition in model_definitions.items()
            if name in self.config.algorithms
        }
        
        if not available_models:
            raise ModelError(f"No valid models found. Available: {list(model_definitions.keys())}")
        
        training_results = {}
        
        for model_name, model_def in available_models.items():
            logger.info(f"Training {model_name}...")
            
            try:
                # Train model with hyperparameter optimization
                result = self._train_single_model(
                    model_name, 
                    model_def, 
                    X_train, 
                    y_train,
                    X_val,
                    y_val
                )
                training_results[model_name] = result
                
                # Track best model
                if self.best_score is None or result["cv_score"] > self.best_score:
                    self.best_score = result["cv_score"]
                    self.best_model = result["model"]
                    self.best_model_name = model_name
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                training_results[model_name] = {
                    "error": str(e),
                    "cv_score": 0.0
                }
        
        # Store models
        self.models = training_results
        
        # Create training summary
        summary = {
            "task_type": self.task_type,
            "best_model": self.best_model_name,
            "best_score": self.best_score,
            "models_trained": len(training_results),
            "training_config": {
                "algorithms": self.config.algorithms,
                "cv_folds": self.config.cv_folds,
                "scoring_metric": self.config.scoring_metric,
                "hyperparameter_tuning": self.config.hyperparameter_tuning
            },
            "model_scores": {
                name: result.get("cv_score", 0.0) 
                for name, result in training_results.items()
                if "error" not in result
            }
        }
        
        logger.info(f"Training complete. Best model: {self.best_model_name} (score: {self.best_score:.4f})")
        
        return summary
    
    def _train_single_model(
        self, 
        model_name: str, 
        model_def: Dict[str, Any], 
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """Train a single model with hyperparameter optimization."""
        
        model = model_def["model"]
        param_grid = model_def["params"]
        
        if self.config.hyperparameter_tuning and param_grid:
            # Use GridSearchCV for hyperparameter optimization
            search = GridSearchCV(
                model,
                param_grid,
                cv=self.config.cv_folds,
                scoring=self._get_scoring_metric(),
                n_jobs=-1,
                verbose=0
            )
            
            search.fit(X_train, y_train)
            best_model = search.best_estimator_
            best_params = search.best_params_
            cv_score = search.best_score_
            
        else:
            # Train with default parameters
            model.fit(X_train, y_train)
            best_model = model
            best_params = {}
            
            # Get cross-validation score
            cv_scores = cross_val_score(
                model, X_train, y_train, 
                cv=self.config.cv_folds,
                scoring=self._get_scoring_metric()
            )
            cv_score = cv_scores.mean()
        
        # Validation score if validation set provided
        val_score = None
        if X_val is not None and y_val is not None:
            if self.task_type == "classification":
                y_pred = best_model.predict(X_val)
                val_score = accuracy_score(y_val, y_pred)
            else:
                y_pred = best_model.predict(X_val)
                val_score = r2_score(y_val, y_pred)
        
        return {
            "model": best_model,
            "best_params": best_params,
            "cv_score": cv_score,
            "val_score": val_score,
            "model_name": model_name
        }
    
    def _get_scoring_metric(self) -> str:
        """Get the appropriate scoring metric for the task."""
        if self.task_type == "classification":
            metric_map = {
                "accuracy": "accuracy",
                "precision": "precision_macro",
                "recall": "recall_macro",
                "f1": "f1_macro",
                "roc_auc": "roc_auc"
            }
        else:
            metric_map = {
                "r2": "r2",
                "mse": "neg_mean_squared_error",
                "mae": "neg_mean_absolute_error",
                "rmse": "neg_root_mean_squared_error"
            }
        
        return metric_map.get(self.config.scoring_metric, "accuracy" if self.task_type == "classification" else "r2")
    
    def save_models(self, output_dir: Path) -> None:
        """Save trained models and training summary."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save best model
        if self.best_model is not None:
            model_path = output_dir / "best_model.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(self.best_model, f)
            logger.info(f"Best model saved to: {model_path}")
        
        # Save all models
        models_dir = output_dir / "all_models"
        models_dir.mkdir(exist_ok=True)
        
        for model_name, result in self.models.items():
            if "model" in result:
                model_path = models_dir / f"{model_name}.pkl"
                with open(model_path, "wb") as f:
                    pickle.dump(result["model"], f)
        
        # Save training summary
        summary = {
            "task_type": self.task_type,
            "best_model_name": getattr(self, 'best_model_name', None),
            "best_score": self.best_score,
            "model_results": {
                name: {
                    "cv_score": result.get("cv_score", 0.0),
                    "val_score": result.get("val_score"),
                    "best_params": result.get("best_params", {}),
                    "error": result.get("error")
                }
                for name, result in self.models.items()
            }
        }
        
        summary_path = output_dir / "training_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Training summary saved to: {summary_path}")
    
    def load_model(self, model_path: Path):
        """Load a trained model."""
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            raise ModelError(f"Error loading model from {model_path}: {e}")
    
    def predict(self, model, X: pd.DataFrame) -> np.ndarray:
        """Make predictions with a trained model."""
        try:
            return model.predict(X)
        except Exception as e:
            raise ModelError(f"Error making predictions: {e}")
    
    def predict_proba(self, model, X: pd.DataFrame) -> Optional[np.ndarray]:
        """Get prediction probabilities (classification only)."""
        try:
            if hasattr(model, "predict_proba"):
                return model.predict_proba(X)
            return None
        except Exception as e:
            logger.warning(f"Error getting prediction probabilities: {e}")
            return None