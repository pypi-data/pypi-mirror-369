"""
Hashub DocApp SDK Exceptions

Custom exception classes for the Hashub DocApp SDK.
"""

from typing import Optional, Dict, Any


class HashubDocError(Exception):
    """Base exception for all Hashub DocApp SDK errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(HashubDocError):
    """Raised when API authentication fails."""
    
    def __init__(self, message: str = "Authentication failed. Please check your API key."):
        super().__init__(message, status_code=401)


class RateLimitError(HashubDocError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded. Please wait before making more requests."):
        super().__init__(message, status_code=429)


class ProcessingError(HashubDocError):
    """Raised when document processing fails."""
    
    def __init__(self, message: str, job_id: Optional[str] = None):
        super().__init__(message, status_code=500)
        self.job_id = job_id


class ValidationError(HashubDocError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, status_code=400)
        self.field = field


class TimeoutError(HashubDocError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str = "Operation timed out"):
        super().__init__(message, status_code=408)


class FileNotFoundError(HashubDocError):
    """Raised when specified file is not found."""
    
    def __init__(self, file_path: str):
        message = f"File not found: {file_path}"
        super().__init__(message, status_code=404)
        self.file_path = file_path


class UnsupportedFormatError(HashubDocError):
    """Raised when file format is not supported."""
    
    def __init__(self, format_type: str):
        message = f"Unsupported file format: {format_type}"
        super().__init__(message, status_code=415)
        self.format_type = format_type
