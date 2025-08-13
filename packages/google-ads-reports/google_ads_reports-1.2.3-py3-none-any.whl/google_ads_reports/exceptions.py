"""
Custom exceptions for the Google Ads driver module.
"""


class GAdsReportError(Exception):
    """Base exception for all Google Ads report errors."""

    def __init__(self, message: str, original_error=None, **context):
        self.message = message
        self.original_error = original_error
        self.context = context

        if original_error:
            super().__init__(f"{message} (caused by: {str(original_error)})")
        else:
            super().__init__(message)


class AuthenticationError(GAdsReportError):
    """Raised when authentication with Google Ads API fails."""
    pass


class ValidationError(GAdsReportError):
    """Raised when input validation fails."""
    pass


class APIError(GAdsReportError):
    """Raised when Google Ads API returns an error."""
    pass


class DataProcessingError(GAdsReportError):
    """Raised when data processing/transformation fails."""
    pass


class ConfigurationError(GAdsReportError):
    """Raised when configuration is invalid."""
    pass
