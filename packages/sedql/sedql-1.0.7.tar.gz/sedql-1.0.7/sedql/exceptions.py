"""
SEDQL Exceptions
"""


class SEDError(Exception):
    """Base exception for SEDQL errors"""
    pass


class SEDConnectionError(SEDError):
    """Exception raised for database connection errors"""
    pass


class SEDValidationError(SEDError):
    """Exception raised for validation errors"""
    pass


class SEDCommandError(SEDError):
    """Exception raised for CLI command execution errors"""
    pass


class SEDConfigError(SEDError):
    """Exception raised for configuration errors"""
    pass
