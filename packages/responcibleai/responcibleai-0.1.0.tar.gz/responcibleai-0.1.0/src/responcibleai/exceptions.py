"""
Custom exception classes for the ResponcibleAI Python SDK.
These allow callers to catch SDK-specific errors instead of generic exceptions.
"""

class ResponcibleAIError(Exception):
    """Base exception for all ResponcibleAI SDK errors."""
    pass


class AuthenticationError(ResponcibleAIError):
    """Raised when authentication with the ResponcibleAI API fails."""
    pass


class AuthorizationError(ResponcibleAIError):
    """Raised when the API key is valid but lacks permissions for the request."""
    pass


class BadRequestError(ResponcibleAIError):
    """Raised when the request to the API is invalid (HTTP 400)."""
    pass


class NotFoundError(ResponcibleAIError):
    """Raised when the requested resource is not found (HTTP 404)."""
    pass


class RateLimitError(ResponcibleAIError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""
    pass


class ServerError(ResponcibleAIError):
    """Raised when the API encounters an internal error (HTTP 5xx)."""
    pass


class NetworkError(ResponcibleAIError):
    """Raised when a network-related error occurs before reaching the API."""
    pass
