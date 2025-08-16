"""VigiEau - Fetch data"""

from .api import VigiEau
from .auth import HttpRequestError, RequestException, TimeoutExceededError
from .exceptions import VigiEauException

__all__ = [
    "VigiEau",
    "VigiEauException",
    "HttpRequestError",
    "TimeoutExceededError",
    "RequestException",
]
