"""
ZKAuth Python SDK

Zero-knowledge proof authentication SDK for Python applications.
"""

from .client import ZKAuthSDK
from .models import User, AuthResult, DeviceInfo, SessionInfo, SignUpData, SignInData
from .exceptions import (
    ZKAuthError,
    ValidationError,
    AuthenticationError,
    NetworkError,
    CircuitError,
    APIError,
)

__version__ = "1.3.0"
__author__ = "ZKAuth Team"
__email__ = "support@zkauth.com"

__all__ = [
    "ZKAuthSDK",
    "User",
    "AuthResult",
    "DeviceInfo",
    "SessionInfo",
    "SignUpData",
    "SignInData",
    "ZKAuthError",
    "ValidationError",
    "AuthenticationError",
    "NetworkError",
    "CircuitError",
    "APIError",
]
