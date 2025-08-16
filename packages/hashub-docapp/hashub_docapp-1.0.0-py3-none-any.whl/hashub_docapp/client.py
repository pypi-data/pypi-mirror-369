"""
Hashub DocApp SDK Client

Main client class implementing all SDK functions as specified in the README.md.
"""

import os
import time
import json
import mimetypes
import hashlib
import hmac
from pathlib import Path
from typing import Optional, Dict, List, Any, Union, Iterator, Tuple
from urllib.parse import urljoin, urlparse

from .utils import validate_file_path, ReturnType
from .progress import render_progress_line, poll_job_with_progress
from .enhancement import ImageEnhanceOptions, get_enhancement_preset, get_available_presets
from .languages import LanguageHelper, get_language_code, get_language_display_name
from .batch import BatchHelper, BatchAnalysis, quick_analyze
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .utils import (
    validate_file_path, ensure_base_url, ReturnType, validate_return_type_args,
    save_content_to_file, generate_output_filename, map_processing_mode
)
from .progress import poll_job_with_progress
from .enhancement import (
    ImageEnhancePresets, get_enhancement_preset, 
    get_available_presets, enhancement_options_to_dict
)
from .models import (
    ConversionMode, OutputFormat, JobStatus, ProcessingPriority,
    OCROptions, ProcessingOptions, BoundingBox,
    ConversionResult, BatchResult, WebhookConfig, APIKeyInfo
)
from .exceptions import (
    HashubDocError, AuthenticationError, RateLimitError, ProcessingError,
    ValidationError, TimeoutError, FileNotFoundError, UnsupportedFormatError
)


class HashubDocAppClient:
    """
    Hashub DocApp SDK Client
    
    Provides a comprehensive Python interface for the Hashub DocApp API,
    enabling intelligent OCR, document conversion, and text extraction.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://doc.hashub.dev/api/v1",
        timeout: Tuple[int, int] = (30, 120),
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        rate_limit_delay: float = 2.0  # Increased default delay to avoid rate limits
    ):
        """
        Initialize the Hashub DocApp client.
        
        Args:
            api_key: API key for authentication (can also be set via HASHUB_API_KEY env var)
            base_url: Base URL for the API
            timeout: Tuple of (connect_timeout, read_timeout) in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retry delays
            rate_limit_delay: Minimum delay between requests (seconds)
        """
        self.api_key = api_key or os.getenv("HASHUB_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key is required. Set HASHUB_API_KEY environment variable or pass api_key parameter.")
            
        self.base_url = base_url.rstrip('/') + '/'
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0
        
        # Setup session with retry strategy
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "hashub-docapp-python-sdk/1.0.0"
        })
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and rate limiting."""
        # Rate limiting - ensure minimum delay between requests
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        try:
            response = self.session.request(
                method, 
                url, 
                timeout=self.timeout,
                **kwargs
            )
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or unauthorized access")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 404:
                # Provide more helpful 404 error information
                if '/convert' in endpoint:
                    error_msg = (
                        f"API endpoint not found: {url}\n"
                        f"This might indicate:\n"
                        f"  1. Wrong base URL - try: https://doc.hashub.dev/api/v1\n"
                        f"  2. API version mismatch\n"
                        f"  3. Endpoint path changed\n"
                        f"Current base URL: {self.base_url}"
                    )
                else:
                    error_msg = f"Resource not found: {url}"
                raise HashubDocError(error_msg, status_code=404)
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get('message', f'HTTP {response.status_code} error')
                except:
                    message = f'HTTP {response.status_code} error'
                raise HashubDocError(message, status_code=response.status_code)
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise HashubDocError("Connection error occurred")
        except requests.exceptions.RequestException as e:
            raise HashubDocError(f"Request failed: {str(e)}")
        finally:
            # Update last request time for rate limiting
            self._last_request_time = time.time()
    
    # =====================================
    # 1. Çekirdek Fonksiyonlar (Core)
    # =====================================
    
    def convert_file(
        self,
        path: str,
        output: str = "markdown",
        mode: str = "auto",
        smart: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convert a local file by uploading it to the API.
        
        Args:
            path: File path to convert
            output: Output format ("markdown", "txt", "json", "pdf")
            mode: Processing mode ("auto", "fast_ocr", "smart_ocr", "layout_json", "bbox_json")
            smart: Enable smart processing
            **kwargs: Additional metadata options
            
        Returns:
            Dictionary containing job_id and other metadata
        """
        file_path = validate_file_path(path)
        
        # Prepare metadata (simplified format that works with API)
        metadata = {
            "output_format": output,
            "processing_mode": map_processing_mode(mode),
            "smart_processing": smart
        }
        
        # Add OCR options if provided
        if 'ocr_options' in kwargs:
            metadata['ocr_options'] = kwargs['ocr_options']
        
        # Add enhancement options if provided
        if 'enhance_options' in kwargs:
            metadata['enhance_options'] = kwargs['enhance_options']
        
        # Upload file
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'metadata': json.dumps(metadata)}
            
            result = self._make_request('POST', '/convert', files=files, data=data)
            
        return {
            'job_id': result['session_id'],
            'status': result['status'],
            'filename': result['filename'],
            'mime_type': result['mime_type'],
            'message': result['message'],
            'created_at': result['created_at'],
            'estimated_time': result.get('estimated_processing_time'),
            'check_status_url': result.get('check_status_url')
        }
    
    def convert_text(
        self,
        text: str,
        output: str = "markdown",
        mode: str = "auto",
        smart: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convert text input (HTML or raw text).
        
        Args:
            text: Text content to convert
            output: Output format
            mode: Processing mode
            smart: Enable smart processing
            **kwargs: Additional options
            
        Returns:
            Dictionary containing job_id and other metadata
        """
        metadata = {
            "output_format": output,
            "processing_mode": map_processing_mode(mode),
            "smart": smart
        }
        
        data = {
            'text_content': text,
            'metadata': json.dumps(metadata)
        }
        
        result = self._make_request('POST', '/convert', data=data)
        
        return {
            'job_id': result['session_id'],
            'status': result['status'],
            'message': result['message'],
            'created_at': result['created_at'],
            'estimated_time': result.get('estimated_processing_time')
        }
    
    def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Dictionary with status information
        """
        result = self._make_request('GET', f'/convert/status/{job_id}')
        
        return {
            'job_id': result.get('session_id', job_id),
            'session_id': result.get('session_id', job_id),  # Keep both for compatibility
            'status': result.get('status', 'unknown'),
            'progress': result.get('progress', 0),
            'step': result.get('step'),
            'filename': result.get('filename'),
            'output_format': result.get('output_format'),
            'updated_at': result.get('updated_at'),
            'download_url': result.get('download_url'),
            'preview_url': result.get('preview_url'),
            'processing_type': result.get('processing_type'),
            'error_details': result.get('error_details'),
            'result': result.get('result')  # Add result field for completed jobs
        }
    
    def wait(
        self, 
        job_id: str, 
        interval: float = 2.0, 
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Wait for job completion with polling.
        
        Args:
            job_id: Job identifier
            interval: Polling interval in seconds
            timeout: Maximum wait time in seconds (auto-calculated if None)
            
        Returns:
            Final job status
        """
        start_time = time.time()
        
        # Auto-calculate timeout if not provided
        if timeout is None:
            timeout = self._calculate_timeout(job_id)
        
        while time.time() - start_time < timeout:
            status = self.get_status(job_id)
            
            if status['status'] in ['completed', 'failed', 'cancelled']:
                return status
                
            time.sleep(interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
    
    def _calculate_timeout(self, job_id: str) -> int:
        """
        Calculate appropriate timeout based on job characteristics.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Calculated timeout in seconds
        """
        try:
            # Get initial job status to understand the task
            status = self.get_status(job_id)
            
            # Base timeouts by processing mode
            base_timeouts = {
                'fast_ocr': 60,           # 1 minute per page
                'smart_ocr': 120,         # 2 minutes per page  
                'extract_text': 30,       # 30 seconds per page
                'layout_json': 90,        # 1.5 minutes per page
                'bbox_json': 45,          # 45 seconds per page
                'doc_convert': 20,        # 20 seconds total (office docs)
            }
            
            processing_type = status.get('processing_type', 'smart_ocr')
            base_timeout = base_timeouts.get(processing_type, 120)
            
            # Estimate page count from file info
            estimated_pages = self._estimate_page_count(status)
            
            # Calculate timeout: base_timeout * pages + buffer
            calculated_timeout = max(
                base_timeout * estimated_pages + 60,  # Add 1 minute buffer
                300  # Minimum 5 minutes
            )
            
            # Maximum limit: 2 hours for very large documents
            max_timeout = 7200
            calculated_timeout = min(calculated_timeout, max_timeout)
            
            print(f"🕐 Auto-timeout: {calculated_timeout//60}m {calculated_timeout%60}s "
                  f"({estimated_pages} pages × {base_timeout}s + buffer)")
            
            return calculated_timeout
            
        except Exception:
            # Fallback to conservative timeout
            return 1800  # 30 minutes
    
    def _estimate_page_count(self, status: Dict[str, Any]) -> int:
        """
        Estimate page count from job status info.
        
        Args:
            status: Job status dictionary
            
        Returns:
            Estimated number of pages
        """
        # First try to get from progress_details (API response)
        progress_details = status.get('progress_details', {})
        if progress_details and 'total_pages' in progress_details:
            total_pages = progress_details['total_pages']
            if total_pages and total_pages > 0:
                return total_pages
        
        # Try to get page count from status if available (legacy)
        if 'page_count' in status:
            return max(status['page_count'], 1)
        
        # Estimate based on file size (rough heuristic)
        filename = status.get('filename', '')
        
        if filename.lower().endswith('.pdf'):
            # PDF: assume multiple pages for PDFs
            return 8  # Conservative estimate for PDFs
        elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
            # Images: usually 1 page
            return 1
        elif filename.lower().endswith(('.doc', '.docx', '.txt', '.html')):
            # Office/text documents: usually process quickly
            return 1
        else:
            # Unknown: conservative estimate
            return 5
    
    def get_result(self, job_id: str) -> Dict[str, Any]:
        """
        Get completed job result.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job result with content
        """
        # First check if job is completed
        status = self.get_status(job_id)
        
        if status['status'] != 'completed':
            raise ProcessingError(f"Job {job_id} is not completed. Status: {status['status']}")
        
        # Download the result content
        if status.get('download_url'):
            download_response = self.session.get(
                ensure_base_url(self.base_url, status['download_url']),
                timeout=self.timeout
            )
            download_response.raise_for_status()
            content = download_response.text
        else:
            content = None
        
        return {
            **status,
            'content': content
        }
    
    def cancel(self, job_id: str) -> None:
        """
        Cancel a job.
        
        Args:
            job_id: Job identifier
        """
        self._make_request('POST', f'/convert/cancel/{job_id}')
    
    def delete(self, job_id: str, with_files: bool = True) -> None:
        """
        Delete job and optionally associated files.
        
        Args:
            job_id: Job identifier
            with_files: Whether to delete associated files
        """
        params = {'with_files': with_files} if with_files else {}
        self._make_request('DELETE', f'/convert/{job_id}', params=params)
    
    # =====================================
    # 2. Gelişmiş Kestirme Fonksiyonlar (Enhanced Shortcuts)
    # =====================================
    
    def convert_smart(
        self, 
        file_or_image: Union[str, Path], 
        output: str = "markdown",
        return_type: ReturnType = "content",
        save_to: Optional[Union[str, Path]] = None,
        show_progress: bool = True,
        timeout: int = 300
    ) -> Union[str, Path]:
        """
        Convert PDF/IMG with smart OCR to high-quality output with progress tracking.
        
        Args:
            file_or_image: Path to file or image
            output: Output format (default: markdown)
            return_type: Return type - 'content', 'url', or 'file'
            save_to: Save path (required when return_type='file')
            show_progress: Show progress bar in terminal
            timeout: Maximum wait time in seconds
            
        Returns:
            Based on return_type:
            - 'content': Text content of the result
            - 'url': Full download URL
            - 'file': Path to saved file
        """
        validate_return_type_args(return_type, save_to)
        
        # Start conversion
        result = self.convert_file(
            path=str(file_or_image),
            output=output,
            mode="smart_ocr",
            smart=True
        )
        
        job_id = result['job_id']
        if show_progress:
            print(f"🚀 Smart conversion started. Job ID: {job_id[-8:]}")
        
        # Wait with progress tracking
        final_status = poll_job_with_progress(
            client=self,
            job_id=job_id,
            timeout=timeout,
            show_progress=show_progress
        )
        
        # Get result based on return_type
        return self._handle_result_return(
            final_status, return_type, save_to, 
            source_path=file_or_image, output_format=output
        )
    
    def convert_fast(
        self, 
        file_or_image: Union[str, Path], 
        output: str = "markdown",
        language: str = "en",  # Now accepts ISO codes by default
        enhancement: Optional[str] = None,
        return_type: ReturnType = "content",
        save_to: Optional[Union[str, Path]] = None,
        show_progress: bool = True,
        timeout: int = 300
    ) -> Union[str, Path]:
        """
        Convert PDF/IMG with fast OCR to plain text with progress tracking.
        
        Args:
            file_or_image: Path to file or image
            output: Output format (default: txt)
            language: Language code - supports both ISO codes ('en', 'tr', 'de') and API codes ('lang_eng_en')
            enhancement: Image enhancement preset name (optional)
            return_type: Return type - 'content', 'url', or 'file'
            save_to: Save path (required when return_type='file')
            show_progress: Show progress bar in terminal
            timeout: Maximum wait time in seconds
            
        Language Examples:
            - 'en' or 'lang_eng_en': English
            - 'tr' or 'lang_tur_tr': Turkish  
            - 'de' or 'lang_deu_de': German
            - 'zh' or 'lang_chi_sim_zh': Chinese (Simplified)
            
        Enhancement Presets:
            - document_crisp: Clean text documents, clear scans
            - scan_low_dpi: Low quality scans (100-150 DPI)
            - camera_shadow: Phone photos with shadows
            - photocopy_faded: Faded photocopies
            - inverted_scan: Inverted color documents
            - noisy_dots: Noisy scans with artifacts
            - tables_fine: Documents with tables
            - receipt_thermal: Receipts and invoices
            - newspaper_moire: Newspapers and magazines
            - fax_low_quality: Old fax documents
            - blueprint: Technical drawings
            
        Returns:
            Based on return_type:
            - 'content': Text content of the result
            - 'url': Full download URL
            - 'file': Path to saved file
        """
        validate_return_type_args(return_type, save_to)
        
        # Convert language code to API format if needed
        try:
            api_language = get_language_code(language)
            lang_info = LanguageHelper.get_language_info(language)
            lang_display = lang_info['english']
        except ValueError as e:
            raise ValidationError(f"Unsupported language: {language}. {e}")
        
        # Prepare conversion options
        conversion_options = {
            "ocr_options": {
                "language": api_language
            }
        }
        
        # Add enhancement preset if specified
        if enhancement:
            enhance_options = get_enhancement_preset(enhancement)
            if enhance_options:
                conversion_options["enhance_options"] = {
                    "preset": "medium",  # Default preset
                    "overrides": enhancement_options_to_dict(enhance_options)
                }
                if show_progress:
                    print(f"🎨 Using enhancement preset: {enhancement}")
            else:
                available = ", ".join(get_available_presets().keys())
                raise ValidationError(f"Unknown enhancement preset: {enhancement}. Available: {available}")
        
        # Start conversion
        result = self.convert_file(
            path=str(file_or_image),
            output=output,
            mode="extract_text_plain",
            smart=False,
            **conversion_options
        )
        
        job_id = result['job_id']
        if show_progress:
            print(f"⚡ Fast OCR started. Job ID: {job_id[-8:]} | Language: {lang_display}")
        
        # Wait with progress tracking
        final_status = poll_job_with_progress(
            client=self,
            job_id=job_id,
            timeout=timeout,
            show_progress=show_progress
        )
        
        # Get result based on return_type
        return self._handle_result_return(
            final_status, return_type, save_to,
            source_path=file_or_image, output_format=output
        )
    
    def convert_layout(
        self, 
        file_or_pdf: Union[str, Path], 
        output: str = "json",
        return_type: ReturnType = "content",
        save_to: Optional[Union[str, Path]] = None,
        show_progress: bool = True,
        timeout: int = 300
    ) -> Union[str, Path]:
        """
        Convert PDF/IMG to structured layout with progress tracking.
        
        Args:
            file_or_pdf: Path to file or PDF
            output: Output format (default: json)
            return_type: Return type - 'content', 'url', or 'file'
            save_to: Save path (required when return_type='file')
            show_progress: Show progress bar in terminal
            timeout: Maximum wait time in seconds
            
        Returns:
            Based on return_type:
            - 'content': Layout content
            - 'url': Full download URL
            - 'file': Path to saved file
        """
        validate_return_type_args(return_type, save_to)
        
        # Start conversion
        result = self.convert_file(
            path=str(file_or_pdf),
            output=output,
            mode="layout_json",
            smart=True
        )
        
        job_id = result['job_id']
        if show_progress:
            print(f"📋 Layout extraction started. Job ID: {job_id[-8:]}")
        
        # Wait with progress tracking
        final_status = poll_job_with_progress(
            client=self,
            job_id=job_id,
            timeout=timeout,
            show_progress=show_progress
        )
        
        # Get result based on return_type
        return self._handle_result_return(
            final_status, return_type, save_to,
            source_path=file_or_pdf, output_format=output
        )
    
    def convert_bbox(
        self, 
        file_or_image: Union[str, Path], 
        regions: List[BoundingBox],
        output: str = "json",
        return_type: ReturnType = "content",
        save_to: Optional[Union[str, Path]] = None,
        show_progress: bool = True,
        timeout: int = 300
    ) -> Union[str, Path]:
        """
        Extract text from specific regions with progress tracking.
        
        Args:
            file_or_image: Path to file or image
            regions: List of bounding box regions
            output: Output format (default: json)
            return_type: Return type - 'content', 'url', or 'file'
            save_to: Save path (required when return_type='file')
            show_progress: Show progress bar in terminal
            timeout: Maximum wait time in seconds
            
        Returns:
            Based on return_type:
            - 'content': Extracted text content
            - 'url': Full download URL
            - 'file': Path to saved file
        """
        validate_return_type_args(return_type, save_to)
        
        # Validate regions
        for region in regions:
            if not all(hasattr(region, attr) for attr in ['x', 'y', 'w', 'h']):
                raise ValidationError("Each region must have 'x', 'y', 'w', 'h' properties")
        
        # Start conversion
        result = self.convert_file(
            path=str(file_or_image),
            output=output,
            mode="bbox_json",
            smart=True,
            custom_data={'bboxRegions': [region.__dict__ for region in regions]}
        )
        
        job_id = result['job_id']
        if show_progress:
            print(f"🎯 Bbox extraction started. Job ID: {job_id[-8:]} ({len(regions)} regions)")
        
        # Wait with progress tracking
        final_status = poll_job_with_progress(
            client=self,
            job_id=job_id,
            timeout=timeout,
            show_progress=show_progress
        )
        
        # Get result based on return_type
        return self._handle_result_return(
            final_status, return_type, save_to,
            source_path=file_or_image, output_format=output
        )
    
    def _handle_result_return(
        self,
        status_data: Dict[str, Any],
        return_type: ReturnType,
        save_to: Optional[Union[str, Path]],
        source_path: Union[str, Path],
        output_format: str
    ) -> Union[str, Path]:
        """
        Handle result return based on return_type.
        
        Args:
            status_data: Job status data
            return_type: Type of return ('content', 'url', 'file')
            save_to: Save path for file return
            source_path: Original source file path
            output_format: Output format
            
        Returns:
            Content, URL, or file path based on return_type
        """
        download_url = status_data.get('download_url')
        if not download_url:
            raise ProcessingError("No download URL available in completed job")
        
        if return_type == 'url':
            # Return full download URL
            return ensure_base_url(self.base_url, download_url)
        
        elif return_type == 'content':
            # Download and return content
            result_data = self.get_result(status_data['session_id'])
            return result_data.get('content', '')
        
        elif return_type == 'file':
            # Download and save to file
            result_data = self.get_result(status_data['session_id'])
            content = result_data.get('content', '')
            
            if save_to:
                save_path = Path(save_to)
            else:
                # Generate filename from source
                filename = generate_output_filename(source_path, output_format)
                save_path = Path(source_path).parent / filename
            
            return save_content_to_file(content, save_path)
        
        else:
            raise ValidationError(f"Invalid return_type: {return_type}")

    def convert_smart_legacy(
        self, 
        file_or_image: str, 
        output: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Legacy smart conversion method (deprecated - use convert_smart instead).
        """
        result = self.convert_file(
            path=file_or_image,
            output=output,
            mode="smart_ocr",
            smart=True
        )
        
        # Wait for completion and return result
        final_status = self.wait(result['job_id'])
        return self.get_result(result['job_id'])
    
    def convert_fast_legacy(
        self, 
        file_or_image: str, 
        output: str = "txt"
    ) -> Dict[str, Any]:
        """
        Legacy fast conversion method (deprecated - use convert_fast instead).
        """
        result = self.convert_file(
            path=file_or_image,
            output=output,
            mode="fast_ocr",
            smart=False
        )
        
        final_status = self.wait(result['job_id'])
        return self.get_result(result['job_id'])
    
    def convert_layout_legacy(
        self, 
        file_or_pdf: str, 
        output: str = "json"
    ) -> Dict[str, Any]:
        """
        Convert PDF/IMG to structured layout JSON.
        
        Args:
            file_or_pdf: Path to file
            output: Output format (default: json)
            
        Returns:
            Conversion result with layout data
        """
        result = self.convert_file(
            path=file_or_pdf,
            output=output,
            mode="layout_json",
            smart=True
        )
        
        final_status = self.wait(result['job_id'])
        return self.get_result(result['job_id'])
    
    def convert_bbox(
        self, 
        file_or_image: str, 
        regions: List[Dict[str, int]], 
        output: str = "json"
    ) -> Dict[str, Any]:
        """
        Extract text from specific regions using bounding boxes.
        
        Args:
            file_or_image: Path to file or image
            regions: List of bounding box regions [{"x": int, "y": int, "w": int, "h": int}]
            output: Output format (default: json)
            
        Returns:
            Conversion result with region-specific text
        """
        # Validate regions format
        for region in regions:
            if not all(key in region for key in ['x', 'y', 'w', 'h']):
                raise ValidationError("Each region must contain 'x', 'y', 'w', 'h' keys")
        
        result = self.convert_file(
            path=file_or_image,
            output=output,
            mode="bbox_json",
            smart=True,
            bbox_regions=regions
        )
        
        final_status = self.wait(result['job_id'])
        return self.get_result(result['job_id'])
    
    def convert_url(
        self, 
        url: str, 
        output: str = "markdown", 
        mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        Convert document from URL (S3 presigned, public URLs).
        
        Args:
            url: Document URL
            output: Output format
            mode: Processing mode
            
        Returns:
            Conversion result
        """
        data = {
            'url': url,
            'metadata': json.dumps({
                'output_format': output,
                'processing_mode': map_processing_mode(mode)
            })
        }
        
        result = self._make_request('POST', '/convert', data=data)
        
        job_id = result['session_id']
        final_status = self.wait(job_id)
        return self.get_result(job_id)
    
    # =====================================
    # 3. Ofis ve HTML Dönüşümü
    # =====================================
    
    def convert_doc(
        self, 
        path: Union[str, Path], 
        output: str = "markdown",
        return_type: ReturnType = "content",
        save_to: Optional[Union[str, Path]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[str, Path]:
        """
        Convert Word/Excel/HTML documents with direct result return.
        
        Args:
            path: Path to document
            output: Output format (default: markdown)
            return_type: Return type - 'content', 'url', or 'file'
            save_to: Save path (required when return_type='file')
            options: Additional conversion options
            
        Returns:
            Based on return_type:
            - 'content': Document content
            - 'url': Full download URL
            - 'file': Path to saved file
        """
        validate_return_type_args(return_type, save_to)
        
        if options is None:
            options = {}
            
        # Start conversion
        result = self.convert_file(
            path=str(path),
            output=output,
            mode="doc_convert",
            smart=False,
            **options
        )
        
        job_id = result['job_id']
        print(f"📄 Document conversion started. Job ID: {job_id[-8:]}")
        
        # Wait for completion (no progress bar - usually fast)
        final_status = self.wait(job_id)
        
        # Get result based on return_type
        return self._handle_result_return(
            final_status, return_type, save_to,
            source_path=path, output_format=output
        )
    
    def convert_html_string(
        self, 
        html_content: str, 
        output: str = "markdown",
        return_type: ReturnType = "content",
        save_to: Optional[Union[str, Path]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[str, Path]:
        """
        Convert HTML string content with direct result return.
        
        Args:
            html_content: HTML content as string
            output: Output format (default: markdown)
            return_type: Return type - 'content', 'url', or 'file'
            save_to: Save path (required when return_type='file')
            options: Additional conversion options
            
        Returns:
            Based on return_type:
            - 'content': Converted content
            - 'url': Full download URL
            - 'file': Path to saved file
        """
        validate_return_type_args(return_type, save_to)
        
        if options is None:
            options = {}
            
        # Start conversion
        result = self.convert_text(
            text=html_content,
            output=output,
            mode="doc_convert",
            smart=True,
            **options
        )
        
        job_id = result['job_id']
        print(f"🌐 HTML conversion started. Job ID: {job_id[-8:]}")
        
        # Wait for completion (no progress bar - usually fast)
        final_status = self.wait(job_id)
        
        # Handle result return - use temp name for HTML string source
        temp_source_name = f"html_content_{job_id[-8:]}.html"
        return self._handle_result_return(
            final_status, return_type, save_to,
            source_path=temp_source_name, output_format=output
        )
    
    # =====================================
    # 4. Batch ve Async Fonksiyonlar
    # =====================================
    
    def batch_convert(
        self, 
        items: List[str], 
        mode: str = "auto", 
        output: str = "markdown", 
        concurrency: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Convert multiple files in parallel.
        
        Args:
            items: List of file paths
            mode: Processing mode
            output: Output format
            concurrency: Number of concurrent conversions
            
        Returns:
            List of conversion results
        """
        import concurrent.futures
        
        def convert_single(item_path):
            try:
                result = self.convert_file(
                    path=item_path,
                    output=output,
                    mode=mode
                )
                final_status = self.wait(result['job_id'])
                return self.get_result(result['job_id'])
            except Exception as e:
                return {
                    'error': str(e),
                    'file_path': item_path,
                    'status': 'failed'
                }
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_item = {executor.submit(convert_single, item): item for item in items}
            
            for future in concurrent.futures.as_completed(future_to_item):
                result = future.result()
                results.append(result)
        
        return results
    
    def stream_progress(self, job_id: str) -> Iterator[Dict[str, Any]]:
        """
        Stream real-time progress updates for a job.
        
        Args:
            job_id: Job identifier
            
        Yields:
            Status updates
        """
        last_progress = -1
        
        while True:
            try:
                status = self.get_status(job_id)
                current_progress = status.get('progress', 0)
                
                # Only yield if progress changed or status changed
                if current_progress != last_progress or status['status'] in ['completed', 'failed', 'cancelled']:
                    yield status
                    last_progress = current_progress
                
                if status['status'] in ['completed', 'failed', 'cancelled']:
                    break
                    
                time.sleep(1)  # 1 second polling interval
                
            except Exception as e:
                yield {'error': str(e), 'job_id': job_id}
                break
    
    # =====================================
    # 5. Yardımcı Fonksiyonlar (Utilities)
    # =====================================
    
    def ping(self) -> bool:
        """
        Check if API is accessible.
        
        Returns:
            True if API is accessible
        """
        try:
            self._make_request('GET', '/health')
            return True
        except:
            return False
    
    def validate_api_key(self) -> bool:
        """
        Validate API key.
        
        Returns:
            True if API key is valid
        """
        try:
            self._make_request('GET', '/auth/validate')
            return True
        except AuthenticationError:
            return False
        except:
            return False
    
    def set_retries(self, max_retries: int, backoff: Tuple[float, float] = (0.3, 2.0)) -> None:
        """
        Set retry strategy.
        
        Args:
            max_retries: Maximum number of retries
            backoff: Tuple of (backoff_factor, max_backoff)
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff[0]
        
        # Update session retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff[0],
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def set_timeout(self, connect: int, read: int) -> None:
        """
        Set HTTP request timeouts.
        
        Args:
            connect: Connection timeout in seconds
            read: Read timeout in seconds
        """
        self.timeout = (connect, read)
    
    def register_webhook(self, url: str, secret: str) -> Dict[str, Any]:
        """
        Register webhook URL.
        
        Args:
            url: Webhook URL
            secret: Webhook secret for signature verification
            
        Returns:
            Registration details
        """
        data = {
            'webhook_url': url,
            'secret': secret,
            'events': ['conversion.completed', 'conversion.failed']
        }
        
        return self._make_request('POST', '/webhooks', json=data)
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: Webhook payload bytes
            signature: Signature from webhook headers
            
        Returns:
            True if signature is valid
        """
        # This would need the webhook secret - implementation depends on your webhook setup
        # For now, return True as placeholder
        return True
    
    # =====================================
    # Additional Utility Methods
    # =====================================
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported input and output formats."""
        try:
            return self._make_request('GET', '/formats')
        except:
            # Fallback to known formats
            return {
                'input_formats': [
                    'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp', 'gif',
                    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'html'
                ],
                'output_formats': ['markdown', 'txt', 'json', 'pdf', 'html']
            }
    
    def get_api_usage(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return self._make_request('GET', '/usage')
    
    def list_jobs(self, limit: int = 50, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List recent jobs.
        
        Args:
            limit: Maximum number of jobs to return
            status: Filter by job status (optional)
            
        Returns:
            List of job dictionaries
        """
        params = {'limit': limit}
        if status:
            params['status'] = status
        return self._make_request('GET', '/jobs', params=params)
    
    # Language Support Methods
    
    def get_supported_languages(self, popular_only: bool = False) -> List[Dict[str, str]]:
        """
        Get list of supported OCR languages.
        
        Args:
            popular_only: Return only popular languages if True
            
        Returns:
            List of language dictionaries with iso, english, native, api_code
        """
        if popular_only:
            return LanguageHelper.get_popular_languages()
        else:
            return LanguageHelper.list_languages()
    
    def search_languages(self, query: str) -> List[Dict[str, str]]:
        """
        Search for languages by name or ISO code.
        
        Args:
            query: Search query (language name or ISO code)
            
        Returns:
            List of matching language dictionaries
        """
        return LanguageHelper.search_languages(query)
    
    def get_language_info(self, code: str) -> Dict[str, str]:
        """
        Get detailed information about a language.
        
        Args:
            code: ISO code ('en') or API code ('lang_eng_en')
            
        Returns:
            Language information dictionary
        """
        return LanguageHelper.get_language_info(code)
    
    def print_language_list(self, popular_only: bool = True):
        """
        Print a formatted list of supported languages.
        
        Args:
            popular_only: Show only popular languages if True
        """
        languages = self.get_supported_languages(popular_only)
        
        print(f"\n{'=' * 60}")
        print(f"📝 Supported OCR Languages {'(Popular)' if popular_only else '(All)'}")
        print(f"{'=' * 60}")
        print(f"{'ISO':<4} {'English Name':<20} {'Native Name':<25}")
        print(f"{'-' * 60}")
        
        for lang in languages:
            iso = lang['iso']
            english = lang['english']
            native = lang['native']
            print(f"{iso:<4} {english:<20} {native:<25}")
        
        print(f"{'-' * 60}")
        print(f"Usage: client.convert_fast('file.pdf', language='{languages[0]['iso']}')")
        if popular_only:
            print("Use client.get_supported_languages(popular_only=False) for all languages")
        print(f"{'=' * 60}\n")
    
    # Intelligent Batch Processing Methods
    
    def batch_convert_smart(
        self,
        directory: Union[str, Path],
        save_to: Union[str, Path],
        output_format: str = "txt",
        recursive: bool = True,
        show_progress: bool = True,
        max_workers: int = 3,
        timeout: int = 600
    ) -> Dict[str, Any]:
        """
        Smart batch processing for images and PDFs with OCR.
        
        Uses intelligent processing with automatic language detection and optimal enhancement.
        The AI automatically detects document language and applies best enhancement settings.
        Only processes files that require OCR (images and PDFs).
        
        Args:
            directory: Directory containing files to process
            save_to: Directory to save processed files
            output_format: Output format (txt, json, markdown)
            recursive: Include subdirectories
            show_progress: Show progress information
            max_workers: Maximum concurrent jobs
            timeout: Total timeout in seconds
            
        Returns:
            Dictionary with processing results and statistics
        """
        return self._batch_convert_internal(
            directory=directory,
            save_to=save_to,
            mode="smart",
            language=None,  # Auto-detect
            enhancement=None,  # Auto-enhance
            output_format=output_format,
            recursive=recursive,
            show_progress=show_progress,
            max_workers=max_workers,
            timeout=timeout
        )
    
    def batch_convert_fast(
        self,
        directory: Union[str, Path],
        save_to: Union[str, Path],
        language: str = "en",
        enhancement: Optional[str] = None,
        output_format: str = "txt",
        recursive: bool = True,
        show_progress: bool = True,
        max_workers: int = 5,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Fast batch OCR processing for images and PDFs.
        
        Uses fast OCR mode for quick text extraction.
        Only processes files that require OCR (images and PDFs).
        
        Args:
            directory: Directory containing files to process
            save_to: Directory to save processed files
            language: Language code (ISO or API format)
            enhancement: Image enhancement preset
            output_format: Output format (txt, json, markdown)
            recursive: Include subdirectories
            show_progress: Show progress information
            max_workers: Maximum concurrent jobs
            timeout: Total timeout in seconds
            
        Returns:
            Dictionary with processing results and statistics
        """
        return self._batch_convert_internal(
            directory=directory,
            save_to=save_to,
            mode="fast",
            language=language,
            enhancement=enhancement,
            output_format=output_format,
            recursive=recursive,
            show_progress=show_progress,
            max_workers=max_workers,
            timeout=timeout
        )
    
    def batch_convert_auto(
        self,
        directory: Union[str, Path],
        save_to: Union[str, Path],
        language: str = "en",
        enhancement: Optional[str] = None,
        output_format: str = "txt",
        recursive: bool = True,
        show_progress: bool = True,
        max_workers: int = 4,
        timeout: int = 900
    ) -> Dict[str, Any]:
        """
        Automatic batch processing for mixed file types.
        
        Intelligently detects file types and applies appropriate processing:
        - Images/PDFs: OCR processing
        - Office documents: Text extraction
        - HTML/XML: Content parsing
        - Text files: Direct processing
        
        Args:
            directory: Directory containing files to process
            save_to: Directory to save processed files
            language: Language code (ISO or API format, used for OCR files)
            enhancement: Image enhancement preset (used for OCR files)
            output_format: Output format (txt, json, markdown)
            recursive: Include subdirectories
            show_progress: Show progress information
            max_workers: Maximum concurrent jobs
            timeout: Total timeout in seconds
            
        Returns:
            Dictionary with processing results and statistics
        """
        return self._batch_convert_internal(
            directory=directory,
            save_to=save_to,
            mode="auto",
            language=language,
            enhancement=enhancement,
            output_format=output_format,
            recursive=recursive,
            show_progress=show_progress,
            max_workers=max_workers,
            timeout=timeout
        )
    
    def analyze_batch_directory(
        self, 
        directory: Union[str, Path], 
        recursive: bool = True,
        show_details: bool = True
    ) -> BatchAnalysis:
        """
        Analyze a directory for batch processing without processing files.
        
        Args:
            directory: Directory to analyze
            recursive: Include subdirectories
            show_details: Print detailed analysis
            
        Returns:
            BatchAnalysis with file categorization and recommendations
        """
        analysis = BatchHelper.analyze_directory(directory, recursive)
        
        if show_details:
            BatchHelper.print_analysis(analysis)
        
        return analysis
    
    def _batch_convert_internal(
        self,
        directory: Union[str, Path],
        save_to: Union[str, Path],
        mode: str,  # 'smart', 'fast', or 'auto'
        language: str = "en",
        enhancement: Optional[str] = None,
        output_format: str = "txt",
        recursive: bool = True,
        show_progress: bool = True,
        max_workers: int = 4,
        timeout: int = 600
    ) -> Dict[str, Any]:
        """Internal batch processing implementation."""
        import concurrent.futures
        import threading
        from datetime import datetime
        
        # Validate inputs
        directory = Path(directory)
        save_to = Path(save_to)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Create output directory
        save_to.mkdir(parents=True, exist_ok=True)
        
        # Analyze directory
        if show_progress:
            print(f"🔍 Analyzing directory: {directory}")
        
        analysis = BatchHelper.analyze_directory(directory, recursive)
        
        # Filter files based on mode
        if mode in ['smart', 'fast']:
            # Only OCR files
            valid_files = BatchHelper.filter_for_mode(analysis.valid_files, mode)
            mode_description = f"{'Smart' if mode == 'smart' else 'Fast'} OCR"
        else:
            # All supported files
            valid_files = analysis.valid_files
            mode_description = "Auto (Mixed Types)"
        
        if not valid_files:
            print("❌ No suitable files found for processing")
            return {
                'success': False,
                'message': 'No suitable files found',
                'processed': 0,
                'failed': 0,
                'results': []
            }
        
        # Show analysis
        if show_progress:
            print(f"\n📊 Batch Processing Summary:")
            print(f"   Mode: {mode_description}")
            print(f"   Files to process: {len(valid_files)}")
            print(f"   Output directory: {save_to}")
            
            if mode == 'smart':
                print(f"   Language: Auto-detect (AI will determine optimal language)")
                print(f"   Enhancement: Auto-enhance (AI will apply best settings)")
            elif language:
                print(f"   Language: {get_language_display_name(language)} ({language})")
                if enhancement:
                    print(f"   Enhancement: {enhancement}")
        
        # Convert language to API format (skip for smart mode)
        api_language = None
        if language and mode != 'smart':
            try:
                api_language = get_language_code(language)
            except ValueError as e:
                raise ValueError(f"Unsupported language: {language}. {e}")
        
        # Prepare processing
        results = []
        failed_files = []
        processed_count = 0
        
        # Progress tracking
        total_files = len(valid_files)
        completed = 0
        lock = threading.Lock()
        
        def update_progress():
            nonlocal completed
            with lock:
                completed += 1
                if show_progress:
                    progress = (completed / total_files) * 100
                    print(f"⏳ Progress: {completed}/{total_files} ({progress:.1f}%) files processed")
        
        def process_single_file(file_path: Path) -> Dict[str, Any]:
            """Process a single file."""
            try:
                # Generate output filename
                output_path = BatchHelper.generate_output_filename(
                    file_path, save_to, output_format
                )
                
                # Determine processing method based on file type and mode
                file_ext = file_path.suffix.lower()
                
                if file_ext in BatchHelper.OCR_EXTENSIONS:
                    # OCR processing
                    if mode == 'fast':
                        # Fast mode: use specified language and enhancement
                        if language:
                            result = self.convert_fast(
                                file_or_image=file_path,
                                output=output_format,
                                language=language,
                                enhancement=enhancement,
                                return_type="content",
                                show_progress=False,
                                timeout=timeout // max_workers
                            )
                        else:
                            # No language specified, use default English
                            result = self.convert_fast(
                                file_or_image=file_path,
                                output=output_format,
                                language="en",
                                enhancement=enhancement,
                                return_type="content",
                                show_progress=False,
                                timeout=timeout // max_workers
                            )
                    else:  # smart or auto
                        # Prepare OCR options based on mode
                        if mode == 'smart':
                            # Smart mode: let AI auto-detect language and enhancement
                            ocr_options = {"auto_detect_language": True}
                        else:
                            # Auto mode: use specified language if provided
                            ocr_options = {}
                            if api_language:
                                ocr_options["language"] = api_language
                        
                        result = self.convert_file(
                            path=str(file_path),
                            output=output_format,
                            mode="smart_ocr",
                            smart=True,
                            ocr_options=ocr_options
                        )
                        # Wait for result
                        job_id = result['job_id']
                        final_status = poll_job_with_progress(
                            client=self,
                            job_id=job_id,
                            timeout=timeout // max_workers,
                            show_progress=False
                        )
                        result = final_status.get('result', {}).get('content', '')
                else:
                    # Non-OCR processing (office docs, html, etc.)
                    result = self.convert_file(
                        path=str(file_path),
                        output=output_format,
                        mode="extract_text",
                        smart=False
                    )
                    job_id = result['job_id']
                    final_status = poll_job_with_progress(
                        client=self,
                        job_id=job_id,
                        timeout=timeout // max_workers,
                        show_progress=False
                    )
                    result = final_status.get('result', {}).get('content', '')
                
                # Save result
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                
                update_progress()
                
                return {
                    'input_file': str(file_path),
                    'output_file': str(output_path),
                    'success': True,
                    'size_chars': len(result),
                    'processing_mode': mode
                }
                
            except Exception as e:
                update_progress()
                return {
                    'input_file': str(file_path),
                    'output_file': None,
                    'success': False,
                    'error': str(e),
                    'processing_mode': mode
                }
        
        # Start processing
        start_time = datetime.now()
        
        if show_progress:
            print(f"\n🚀 Starting batch processing with {max_workers} workers...")
        
        # Process files with thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(process_single_file, file_path): file_path 
                for file_path in valid_files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                results.append(result)
                
                if result['success']:
                    processed_count += 1
                else:
                    failed_files.append(result['input_file'])
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Final summary
        if show_progress:
            print(f"\n✅ Batch processing completed!")
            print(f"   Total time: {duration:.1f} seconds")
            print(f"   Successfully processed: {processed_count}/{total_files}")
            print(f"   Failed: {len(failed_files)}")
            print(f"   Output directory: {save_to}")
            
            if failed_files:
                print(f"\n❌ Failed files:")
                for failed_file in failed_files[:5]:  # Show first 5
                    print(f"   • {Path(failed_file).name}")
                if len(failed_files) > 5:
                    print(f"   ... and {len(failed_files) - 5} more")
        
        return {
            'success': processed_count > 0,
            'processed': processed_count,
            'failed': len(failed_files),
            'total_files': total_files,
            'duration_seconds': duration,
            'output_directory': str(save_to),
            'processing_mode': mode,
            'results': results,
            'failed_files': failed_files
        }
