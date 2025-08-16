"""AddressesFrPy - Python client for the French address API."""

from .api import AddressFr
from .auth import HttpRequestError, RequestException, TimeoutExceededError
from .exceptions import AddressFrException

__all__ = [
    "AddressFr",
    "AddressFrException",
    "HttpRequestError",
    "TimeoutExceededError",
    "RequestException",
]
