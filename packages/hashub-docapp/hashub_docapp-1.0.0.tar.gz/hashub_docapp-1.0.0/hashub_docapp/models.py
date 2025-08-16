"""
Hashub DocApp SDK Models

Data classes and enums for the Hashub DocApp SDK.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Union
from datetime import datetime


class ConversionMode(Enum):
    """Document conversion modes."""
    AUTO = "auto"
    FAST_OCR = "fast_ocr" 
    SMART_OCR = "smart_ocr"
    LAYOUT_JSON = "layout_json"
    BBOX_JSON = "bbox_json"
    DOC_CONVERT = "doc_convert"


class OutputFormat(Enum):
    """Output format options."""
    MARKDOWN = "markdown"
    TXT = "txt"
    JSON = "json"
    PDF = "pdf"
    HTML = "html"


class JobStatus(Enum):
    """Job processing status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingPriority(Enum):
    """Processing priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10


@dataclass
class OCROptions:
    """OCR configuration options."""
    language: str = "lang_eng_en"
    chunk_size: int = 5
    psm_mode: int = 6
    confidence_threshold: int = 80
    enhance_options: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.enhance_options is None:
            self.enhance_options = {
                "preset": "scan_medium",
                "overrides": {
                    "contrast": 1.3,
                    "sharpness": 1.2,
                    "deskew": True
                }
            }


@dataclass
class ProcessingOptions:
    """Document processing configuration."""
    smart_processing: bool = True
    processing_mode: str = "extract_structured_full"
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    tags: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    source: str = "python_sdk"
    client_version: str = "1.0.0"


@dataclass
class ConversionMetadata:
    """Metadata for conversion requests."""
    convert_type: str = "file"
    output_format: str = "markdown"
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    smart_processing: bool = True
    processing_mode: str = "extract_structured_full"
    ocr_options: Optional[OCROptions] = None
    psm_mode: int = 6
    confidence_threshold: int = 80
    source: str = "python_sdk"
    client_version: str = "1.0.0"
    priority: int = 5
    tags: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BoundingBox:
    """Bounding box coordinates for region-based OCR."""
    x: int
    y: int
    w: int
    h: int


@dataclass
class ConversionResult:
    """Result of a document conversion."""
    session_id: str
    status: JobStatus
    filename: str
    mime_type: str
    output_format: str
    content: Optional[str] = None
    download_url: Optional[str] = None
    preview_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    progress: int = 0
    step: Optional[str] = None
    message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class BatchResult:
    """Result of a batch conversion operation."""
    total_files: int
    successful: int
    failed: int
    results: List[ConversionResult]
    errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    url: str
    secret: str
    events: List[str] = field(default_factory=lambda: ["conversion.completed", "conversion.failed"])


@dataclass
class APIKeyInfo:
    """API key information."""
    key_id: str
    name: str
    permissions: List[str]
    rate_limit: Dict[str, int]
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
