"""
Utility functions for Hashub DocApp SDK

File operations, validation, and helper functions.
"""

import os
import mimetypes
from pathlib import Path
from typing import Union, Optional, Literal
from urllib.parse import urljoin


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validate and return Path object for file.
    
    Args:
        file_path: File path to validate
        
    Returns:
        Validated Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValidationError: If path is not a file
    """
    from .exceptions import ValidationError
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(str(file_path))
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")
    return path


def get_mime_type(file_path: Union[str, Path]) -> str:
    """
    Get MIME type for file.
    
    Args:
        file_path: Path to file
        
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def map_processing_mode(mode: str) -> str:
    """
    Map SDK processing modes to API processing modes.
    
    Args:
        mode: SDK processing mode
        
    Returns:
        API processing mode
    """
    mode_mapping = {
        "auto": "extract_structured_full",
        "fast_ocr": "extract_text_plain",
        "smart_ocr": "extract_structured_full", 
        "layout_json": "extract_layout_structure",
        "bbox_json": "extract_text_from_bbox",
        "doc_convert": "extract_structured_full"
    }
    return mode_mapping.get(mode, mode)


def ensure_base_url(base_url: str, download_url: str) -> str:
    """
    Ensure download URL has base URL prefix.
    
    Args:
        base_url: API base URL
        download_url: Download URL (may be relative)
        
    Returns:
        Full download URL
    """
    if download_url.startswith('http'):
        return download_url
    elif download_url.startswith('/'):
        # Extract domain from base_url
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        return domain + download_url
    else:
        return urljoin(base_url, download_url)


def get_output_extension(output_format: str) -> str:
    """
    Get file extension for output format.
    
    Args:
        output_format: Output format name
        
    Returns:
        File extension including dot
    """
    extension_map = {
        "markdown": ".md",
        "txt": ".txt",
        "json": ".json", 
        "pdf": ".pdf",
        "html": ".html",
        "docx": ".docx"
    }
    return extension_map.get(output_format, ".out")


def generate_output_filename(
    source_path: Union[str, Path],
    output_format: str,
    suffix: str = "_converted"
) -> str:
    """
    Generate output filename based on source file and format.
    
    Args:
        source_path: Source file path
        output_format: Output format
        suffix: Suffix to add to filename
        
    Returns:
        Generated output filename
    """
    source = Path(source_path)
    stem = source.stem
    ext = get_output_extension(output_format)
    return f"{stem}{suffix}{ext}"


def save_content_to_file(
    content: str,
    file_path: Union[str, Path],
    encoding: str = 'utf-8'
) -> Path:
    """
    Save content to file with proper encoding.
    
    Args:
        content: Content to save
        file_path: Target file path
        encoding: File encoding
        
    Returns:
        Path object of saved file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)
    
    return path


ReturnType = Literal['content', 'url', 'file']


def validate_return_type_args(
    return_type: ReturnType,
    save_to: Optional[Union[str, Path]] = None
) -> None:
    """
    Validate return_type and save_to arguments.
    
    Args:
        return_type: Type of return ('content', 'url', 'file')
        save_to: Save path (required for 'file' return_type)
        
    Raises:
        ValidationError: If arguments are invalid
    """
    from .exceptions import ValidationError
    
    if return_type not in ('content', 'url', 'file'):
        raise ValidationError(f"return_type must be 'content', 'url', or 'file', got: {return_type}")
    
    if return_type == 'file' and not save_to:
        raise ValidationError("save_to is required when return_type='file'")


def redact_api_key(api_key: str) -> str:
    """
    Redact API key for logging purposes.
    
    Args:
        api_key: API key to redact
        
    Returns:
        Redacted API key
    """
    if not api_key:
        return api_key
    if len(api_key) <= 8:
        return "****"
    return api_key[:4] + "…" + api_key[-4:]
