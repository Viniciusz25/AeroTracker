"""
AeroTracker Core — Pacote API
================================
Exporta os clientes de API e exceções base.
"""

from api.base_client import (
    APIAuthError,
    APIError,
    APINotFoundError,
    APIRateLimitError,
    APIServerError,
    APITimeoutError,
    BaseAPIClient,
    RetryConfig,
)

__all__ = [
    "BaseAPIClient",
    "RetryConfig",
    "APIError",
    "APITimeoutError",
    "APIRateLimitError",
    "APIAuthError",
    "APINotFoundError",
    "APIServerError",
]
