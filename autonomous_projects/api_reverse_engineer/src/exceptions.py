"""
Exception classes for the API reverse engineering tool.
"""

from typing import Optional, Any


class APIReverseEngineerError(Exception):
    """Base exception for all API reverse engineering errors."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details
        
    def __str__(self):
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class TrafficCaptureError(APIReverseEngineerError):
    """Raised when traffic capture fails."""
    pass


class ProxyServerError(TrafficCaptureError):
    """Raised when proxy server cannot be started."""
    pass


class TrafficAnalysisError(APIReverseEngineerError):
    """Raised when traffic analysis fails."""
    pass


class InvalidTrafficDataError(TrafficAnalysisError):
    """Raised when traffic data is invalid or corrupted."""
    pass


class InsufficientDataError(TrafficAnalysisError):
    """Raised when there's insufficient data for analysis."""
    pass


class SDKGenerationError(APIReverseEngineerError):
    """Raised when SDK generation fails."""
    pass


class UnsupportedLanguageError(SDKGenerationError):
    """Raised when trying to generate SDK for unsupported language."""
    pass


class TemplateError(SDKGenerationError):
    """Raised when template processing fails."""
    pass


class DocumentationError(APIReverseEngineerError):
    """Raised when documentation generation fails."""
    pass


class FileOperationError(APIReverseEngineerError):
    """Raised when file operations fail."""
    pass


class ConfigurationError(APIReverseEngineerError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(APIReverseEngineerError):
    """Raised when data validation fails."""
    pass


class NetworkError(APIReverseEngineerError):
    """Raised when network operations fail."""
    pass