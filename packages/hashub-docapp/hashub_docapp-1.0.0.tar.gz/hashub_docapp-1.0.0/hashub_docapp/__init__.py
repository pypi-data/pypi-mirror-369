"""
Hashub DocApp SDK - Professional Document Processing API Client

This SDK provides a comprehensive Python interface for the Hashub DocApp API,
enabling intelligent OCR, document conversion, and text extraction capabilities.

Author: Hashub Team
License: MIT
Version: 1.0.0
"""

from .client import HashubDocAppClient

# Alias for convenience
DocAppClient = HashubDocAppClient
from .models import (
    ConversionMode,
    OutputFormat,
    OCROptions,
    ProcessingOptions,
    BatchResult,
    ConversionResult,
    JobStatus
)
from .exceptions import (
    HashubDocError,
    AuthenticationError,
    RateLimitError,
    ProcessingError,
    ValidationError
)

__version__ = "1.0.0"
__author__ = "Hashub Team"
__email__ = "support@hashub.com"

__all__ = [
    "HashubDocAppClient",
    "DocAppClient",
    "ConversionMode",
    "OutputFormat", 
    "OCROptions",
    "ProcessingOptions",
    "BatchResult",
    "ConversionResult",
    "JobStatus",
    "HashubDocError",
    "AuthenticationError",
    "RateLimitError",
    "ProcessingError",
    "ValidationError"
]
