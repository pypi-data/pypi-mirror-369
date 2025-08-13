"""
SpiderFoot API Client

A Python client library for interacting with SpiderFoot API v4.0.
"""

from .client import SpiderFootClient, SpiderFootAPIError

__version__ = "1.0.0"
__all__ = ["SpiderFootClient", "SpiderFootAPIError"]