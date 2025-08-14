"""Data processing and preprocessing module."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    LabelEncoder,
    OneHotEncoder,
    RobustScaler,
    StandardScaler,
    MinMaxScaler,
)

from mlcli.core.config import DataConfig
from mlcli.core.exceptions import DataError
from mlcli.utils.logging import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """Advanced data preprocessing pipeline."""
    
    def __init__(self, config: DataConfig):
        self.config = config
        self.preprocessor: Optional[ColumnTransformer] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.feature_names: List[str] = []
        self.target_name: Optional[str] = None
        
    def load_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """Load data from various file formats."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DataError(f"Data file not found: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_path.suffix.lower() == '.json':
                df = pd.read_json(file_path)
            elif file_path.suffix.lower() == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                raise DataError(f"Unsupported file format: {file_path.suffix}")
            
            logger.info(f"Loaded data: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            raise DataError(f"Error loading data from {file_path}: {e}")
    
    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive data analysis."""
        analysis = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
            "duplicates": df.duplicated().sum(),
            "memory_usage": df.memory_usage(deep=True).sum(),
        }
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            analysis["numeric_stats"] = df[numeric_cols].describe().to_dict()
            analysis["numeric_columns"] = numeric_cols
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            analysis["categorical_columns"] = categorical_cols
            analysis["categorical_stats"] = {}
            for col in categorical_cols:
                analysis["categorical_stats"][col] = {
                    "unique_values": df[col].nunique(),
                    "top_values": df[col].value_counts().head(10).to_dict()
                }
        
        # Data quality issues
        analysis["quality_issues"] = self._detect_quality_issues(df)
        
        return analysis
    
    def _detect_quality_issues(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect common data quality issues."""
        issues = {
            "high_missing_columns": [],
            "high_cardinality_columns": [],
            "constant_columns": [],
            "duplicate_columns": [],
            "outlier_columns": [],
        }
        
        # High missing values (>50%)
        missing_pct = df.isnull().sum() / len(df)
        issues["high_missing_columns"] = missing_pct[missing_pct > 0.5].index.tolist()
        
        # High cardinality categorical columns (>50% unique values)
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) > 0.5:
                issues["high_cardinality_columns"].append(col)
        
        # Constant columns
        for col in df.columns:
            if df[col].nunique() <= 1:
                issues["constant_columns"].append(col)
        
        # Duplicate columns
        for i, col1 in enumerate(df.columns):
            for col2 in df.columns[i+1:]:
                if df[col1].equals(df[col2]):
                    issues["duplicate_columns"].append((col1, col2))
        
        # Potential outliers in numeric columns (using IQR method)
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            if len(outliers) > len(df) * 0.05:  # More than 5% outliers
                issues["outlier_columns"].append(col)
        
        return issues
    
    def preprocess_data(
        self, 
        df: pd.DataFrame, 
        target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Optional[pd.Series], Dict[str, Any]]:
        """Preprocess data with intelligent feature engineering."""
        
        target_column = target_column or self.config.target_column
        if not target_column or target_column not in df.columns:
            raise DataError(f"Target column '{target_column}' not found in data")
        
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Auto-detect column types if not specified
        numeric_cols = self._get_numeric_columns(X)
        categorical_cols = self._get_categorical_columns(X)
        
        # Create preprocessing pipeline
        self.preprocessor = self._create_preprocessor(numeric_cols, categorical_cols)
        
        # Fit and transform features
        X_processed = self.preprocessor.fit_transform(X)
        
        # Get feature names after preprocessing
        self.feature_names = self._get_feature_names(numeric_cols, categorical_cols)
        
        # Convert to DataFrame
        X_processed = pd.DataFrame(X_processed, columns=self.feature_names, index=X.index)
        
        # Process target variable
        y_processed, target_info = self._process_target(y)
        
        # Create preprocessing report
        preprocessing_report = {
            "original_shape": df.shape,
            "processed_shape": (X_processed.shape[0], X_processed.shape[1]),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "feature_names": self.feature_names,
            "target_info": target_info,
            "preprocessing_steps": self._get_preprocessing_steps(),
        }
        
        logger.info(f"Preprocessing complete: {X_processed.shape[1]} features")
        
        return X_processed, y_processed, preprocessing_report
    
    def _get_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """Get numeric columns, respecting config if provided."""
        if self.config.numerical_columns:
            return [col for col in self.config.numerical_columns if col in df.columns]
        return df.select_dtypes(include=['number']).columns.tolist()
    
    def _get_categorical_columns(self, df: pd.DataFrame) -> List[str]:
        """Get categorical columns, respecting config if provided."""
        if self.config.categorical_columns:
            return [col for col in self.config.categorical_columns if col in df.columns]
        return df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def _create_preprocessor(
        self, 
        numeric_cols: List[str], 
        categorical_cols: List[str]
    ) -> ColumnTransformer:
        """Create preprocessing pipeline."""
        
        transformers = []
        
        # Numeric preprocessing
        if numeric_cols:
            numeric_steps = []
            
            # Imputation
            if self.config.missing_value_strategy == "mean":
                numeric_steps.append(("imputer", SimpleImputer(strategy="mean")))
            elif self.config.missing_value_strategy == "median":
                numeric_steps.append(("imputer", SimpleImputer(strategy="median")))
            elif self.config.missing_value_strategy == "constant":
                numeric_steps.append(("imputer", SimpleImputer(strategy="constant", fill_value=0)))
            
            # Scaling
            if self.config.scaling_strategy == "standard":
                numeric_steps.append(("scaler", StandardScaler()))
            elif self.config.scaling_strategy == "minmax":
                numeric_steps.append(("scaler", MinMaxScaler()))
            elif self.config.scaling_strategy == "robust":
                numeric_steps.append(("scaler", RobustScaler()))
            
            if numeric_steps:
                from sklearn.pipeline import Pipeline
                transformers.append(("numeric", Pipeline(numeric_steps), numeric_cols))
        
        # Categorical preprocessing
        if categorical_cols:
            categorical_steps = []
            
            # Imputation
            categorical_steps.append(("imputer", SimpleImputer(strategy="most_frequent")))
            
            # Encoding
            if self.config.encoding_strategy in ["auto", "onehot"]:
                categorical_steps.append(("encoder", OneHotEncoder(drop="first", sparse_output=False)))
            
            if categorical_steps:
                from sklearn.pipeline import Pipeline
                transformers.append(("categorical", Pipeline(categorical_steps), categorical_cols))
        
        return ColumnTransformer(transformers, remainder="passthrough")
    
    def _get_feature_names(
        self, 
        numeric_cols: List[str], 
        categorical_cols: List[str]
    ) -> List[str]:
        """Get feature names after preprocessing."""
        feature_names = []
        
        # Numeric features keep their names
        feature_names.extend(numeric_cols)
        
        # Categorical features get expanded names
        if categorical_cols and hasattr(self.preprocessor, "named_transformers_"):
            cat_transformer = self.preprocessor.named_transformers_.get("categorical")
            if cat_transformer and hasattr(cat_transformer, "named_steps"):
                encoder = cat_transformer.named_steps.get("encoder")
                if hasattr(encoder, "get_feature_names_out"):
                    cat_feature_names = encoder.get_feature_names_out(categorical_cols)
                    feature_names.extend(cat_feature_names)
                else:
                    # Fallback for older sklearn versions
                    feature_names.extend(categorical_cols)
        
        return feature_names
    
    def _process_target(self, y: pd.Series) -> Tuple[pd.Series, Dict[str, Any]]:
        """Process target variable."""
        target_info = {
            "name": y.name,
            "dtype": str(y.dtype),
            "unique_values": y.nunique(),
            "missing_values": y.isnull().sum(),
        }
        
        # For classification tasks with string labels
        if y.dtype == 'object' or y.dtype.name == 'category':
            self.label_encoder = LabelEncoder()
            y_processed = pd.Series(
                self.label_encoder.fit_transform(y), 
                index=y.index, 
                name=y.name
            )
            target_info["label_mapping"] = dict(
                zip(self.label_encoder.classes_, self.label_encoder.transform(self.label_encoder.classes_))
            )
            target_info["task_type"] = "classification"
        else:
            y_processed = y.copy()
            if y.nunique() <= 10:  # Likely classification
                target_info["task_type"] = "classification"
            else:
                target_info["task_type"] = "regression"
        
        return y_processed, target_info
    
    def _get_preprocessing_steps(self) -> List[str]:
        """Get list of preprocessing steps applied."""
        steps = []
        
        if self.config.missing_value_strategy != "none":
            steps.append(f"Missing value imputation: {self.config.missing_value_strategy}")
        
        if self.config.scaling_strategy != "none":
            steps.append(f"Feature scaling: {self.config.scaling_strategy}")
        
        if self.config.encoding_strategy != "none":
            steps.append(f"Categorical encoding: {self.config.encoding_strategy}")
        
        return steps
    
    def split_data(
        self, 
        X: pd.DataFrame, 
        y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split data into train and test sets."""
        
        return train_test_split(
            X, y,
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=y if y.nunique() <= 10 else None  # Stratify for classification
        )
    
    def save_preprocessing_artifacts(self, output_dir: Path, report: Dict[str, Any]) -> None:
        """Save preprocessing artifacts and reports."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save data profile
        profile_path = output_dir / "data_profile.json"
        with open(profile_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Data profile saved to: {profile_path}")
    
    def transform_new_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using fitted preprocessor."""
        if self.preprocessor is None:
            raise DataError("Preprocessor not fitted. Run preprocess_data first.")
        
        # Remove target column if present
        if self.target_name and self.target_name in df.columns:
            df = df.drop(columns=[self.target_name])
        
        # Transform data
        X_transformed = self.preprocessor.transform(df)
        
        # Convert to DataFrame
        return pd.DataFrame(X_transformed, columns=self.feature_names, index=df.index)