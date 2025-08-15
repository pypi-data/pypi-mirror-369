"""
Essential custom models for NAV Online Számla API.

This module contains only the essential custom classes that are not part of the 
official XSD-generated models but are required for the client implementation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NavCredentials:
    """NAV API credentials - not part of official API models."""

    login: str
    password: str
    signer_key: str
    tax_number: str
