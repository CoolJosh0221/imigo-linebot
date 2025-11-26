"""Custom exceptions for the IMIGO application"""


class ImigoException(Exception):
    """Base exception for all IMIGO errors"""

    pass


class ConfigurationError(ImigoException):
    """Raised when configuration is invalid or missing"""

    pass


class DatabaseError(ImigoException):
    """Raised when database operations fail"""

    pass


class LINEAPIError(ImigoException):
    """Raised when LINE API operations fail"""

    pass


class AIServiceError(ImigoException):
    """Raised when AI service operations fail"""

    pass


class TranslationError(ImigoException):
    """Raised when translation operations fail"""

    pass


class RichMenuError(ImigoException):
    """Raised when rich menu operations fail"""

    pass


class ValidationError(ImigoException):
    """Raised when input validation fails"""

    pass
