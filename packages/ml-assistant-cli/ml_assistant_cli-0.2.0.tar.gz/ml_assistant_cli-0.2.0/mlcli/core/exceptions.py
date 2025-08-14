"""Custom exceptions for ML Assistant CLI."""

from typing import Optional


class MLCLIError(Exception):
    """Base exception for all ML CLI errors."""
    
    def __init__(self, message: str, details: Optional[str] = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class ConfigurationError(MLCLIError):
    """Raised when there's a configuration issue."""
    pass


class DataError(MLCLIError):
    """Raised when there's a data processing issue."""
    pass


class ModelError(MLCLIError):
    """Raised when there's a model training/evaluation issue."""
    pass


class DeploymentError(MLCLIError):
    """Raised when there's a deployment issue."""
    pass


class ValidationError(MLCLIError):
    """Raised when validation fails."""
    pass


class ProviderError(MLCLIError):
    """Raised when there's a cloud provider issue."""
    pass