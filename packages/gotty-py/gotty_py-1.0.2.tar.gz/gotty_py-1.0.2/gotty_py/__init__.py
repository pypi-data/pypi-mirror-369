"""
Gotty Python Client

A generic Python client for interacting with gotty terminal interfaces.
"""

from .gotty_client import GottyWebSocketClient, ServerResponse

__version__ = "1.0.2"
__author__ = "Thomas Wentworth"

__all__ = [
    'GottyWebSocketClient',
    'ServerResponse',
]
