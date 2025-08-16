"""
Unit tests for Hashub DocApp SDK

Run with: python -m pytest tests/
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from hashub_docapp import HashubDocClient, HashubDocError, AuthenticationError, RateLimitError
from hashub_docapp.models import ConversionMode, OutputFormat, OCROptions


class TestHashubDocClient:
    """Test cases for HashubDocClient class."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = HashubDocClient(api_key="test_api_key")
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.api_key == "test_api_key"
        assert self.client.base_url == "https://api.hashub.com/api/v1"
        assert "Authorization" in self.client.session.headers
        assert self.client.session.headers["Authorization"] == "Bearer test_api_key"
    
    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            HashubDocClient()
    
    @patch.dict('os.environ', {'HASHUB_API_KEY': 'env_api_key'})
    def test_client_initialization_from_env(self):
        """Test client initialization from environment variable."""
        client = HashubDocClient()
        assert client.api_key == "env_api_key"
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_ping_success(self, mock_request):
        """Test successful ping."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_request.return_value = mock_response
        
        result = self.client.ping()
        assert result is True
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_ping_failure(self, mock_request):
        """Test ping failure."""
        mock_request.side_effect = Exception("Connection error")
        
        result = self.client.ping()
        assert result is False
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_validate_api_key_success(self, mock_request):
        """Test successful API key validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"valid": True}
        mock_request.return_value = mock_response
        
        result = self.client.validate_api_key()
        assert result is True
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_validate_api_key_invalid(self, mock_request):
        """Test invalid API key validation."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        result = self.client.validate_api_key()
        assert result is False
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_convert_file_success(self, mock_request):
        """Test successful file conversion."""
        # Mock file exists
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', create=True) as mock_open:
            
            mock_open.return_value.__enter__.return_value = Mock()
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "queued",
                "session_id": "test_session_123",
                "filename": "test.pdf",
                "mime_type": "application/pdf",
                "message": "Upload successful",
                "created_at": "2025-01-01T10:00:00Z",
                "estimated_processing_time": 30.0
            }
            mock_request.return_value = mock_response
            
            result = self.client.convert_file("test.pdf")
            
            assert result["job_id"] == "test_session_123"
            assert result["status"] == "queued"
            assert result["filename"] == "test.pdf"
    
    def test_convert_file_not_found(self):
        """Test file not found error."""
        with pytest.raises(Exception):  # FileNotFoundError from _validate_file_path
            self.client.convert_file("nonexistent_file.pdf")
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_get_status_success(self, mock_request):
        """Test successful status check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "session_id": "test_session_123",
            "status": "processing",
            "progress": 50,
            "step": "Processing document",
            "filename": "test.pdf",
            "output_format": "markdown",
            "updated_at": "2025-01-01T10:01:00Z"
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_status("test_session_123")
        
        assert result["job_id"] == "test_session_123"
        assert result["status"] == "processing"
        assert result["progress"] == 50
    
    @patch('hashub_docapp.client.HashubDocClient.get_status')
    def test_wait_success(self, mock_get_status):
        """Test successful wait for completion."""
        # Mock progression: processing -> completed
        mock_get_status.side_effect = [
            {"status": "processing", "progress": 25},
            {"status": "processing", "progress": 75},
            {"status": "completed", "progress": 100}
        ]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = self.client.wait("test_session_123", interval=0.1, timeout=10)
            
        assert result["status"] == "completed"
        assert mock_get_status.call_count == 3
    
    @patch('hashub_docapp.client.HashubDocClient.get_status')
    def test_wait_timeout(self, mock_get_status):
        """Test wait timeout."""
        mock_get_status.return_value = {"status": "processing", "progress": 25}
        
        with patch('time.sleep'), \
             patch('time.time', side_effect=[0, 1, 2, 3, 11]):  # Mock time progression
            
            with pytest.raises(Exception):  # TimeoutError
                self.client.wait("test_session_123", interval=0.1, timeout=10)
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_convert_smart_integration(self, mock_request):
        """Test convert_smart integration."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', create=True), \
             patch('hashub_docapp.client.HashubDocClient.wait') as mock_wait, \
             patch('hashub_docapp.client.HashubDocClient.get_result') as mock_get_result:
            
            # Mock convert_file response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "queued",
                "session_id": "test_session_123",
                "filename": "test.pdf",
                "mime_type": "application/pdf",
                "message": "Upload successful",
                "created_at": "2025-01-01T10:00:00Z"
            }
            mock_request.return_value = mock_response
            
            mock_wait.return_value = {"status": "completed"}
            mock_get_result.return_value = {
                "job_id": "test_session_123",
                "status": "completed",
                "content": "# Test Document\n\nThis is test content."
            }
            
            result = self.client.convert_smart("test.pdf")
            
            assert result["status"] == "completed"
            assert "content" in result
            mock_wait.assert_called_once()
            mock_get_result.assert_called_once()
    
    def test_batch_convert_empty_list(self):
        """Test batch convert with empty list."""
        result = self.client.batch_convert([])
        assert result == []
    
    @patch('hashub_docapp.client.HashubDocClient.convert_file')
    @patch('hashub_docapp.client.HashubDocClient.wait')
    @patch('hashub_docapp.client.HashubDocClient.get_result')
    def test_batch_convert_success(self, mock_get_result, mock_wait, mock_convert_file):
        """Test successful batch conversion."""
        files = ["file1.pdf", "file2.pdf"]
        
        mock_convert_file.side_effect = [
            {"job_id": "job1", "status": "queued"},
            {"job_id": "job2", "status": "queued"}
        ]
        
        mock_wait.return_value = {"status": "completed"}
        
        mock_get_result.side_effect = [
            {"job_id": "job1", "status": "completed", "content": "Content 1"},
            {"job_id": "job2", "status": "completed", "content": "Content 2"}
        ]
        
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            # Mock the executor context manager
            mock_executor.return_value.__enter__.return_value = mock_executor
            mock_executor.return_value.__exit__.return_value = None
            
            # Mock futures
            mock_future1 = Mock()
            mock_future1.result.return_value = {"status": "completed", "content": "Content 1"}
            mock_future2 = Mock()
            mock_future2.result.return_value = {"status": "completed", "content": "Content 2"}
            
            mock_executor.submit.side_effect = [mock_future1, mock_future2]
            mock_executor.as_completed.return_value = [mock_future1, mock_future2]
            
            results = self.client.batch_convert(files, concurrency=2)
            
        assert len(results) == 2
        assert all("content" in result for result in results)


class TestModels:
    """Test cases for model classes."""
    
    def test_ocr_options_creation(self):
        """Test OCR options creation."""
        options = OCROptions(
            language="lang_eng_en",
            chunk_size=5,
            confidence_threshold=85
        )
        
        assert options.language == "lang_eng_en"
        assert options.chunk_size == 5
        assert options.confidence_threshold == 85
        assert options.enhance_options is not None
    
    def test_ocr_options_defaults(self):
        """Test OCR options with defaults."""
        options = OCROptions()
        
        assert options.language == "lang_eng_en"
        assert options.chunk_size == 5
        assert options.psm_mode == 6
        assert options.confidence_threshold == 80
        assert "preset" in options.enhance_options
    
    def test_conversion_mode_enum(self):
        """Test ConversionMode enum."""
        assert ConversionMode.AUTO.value == "auto"
        assert ConversionMode.SMART_OCR.value == "smart_ocr"
        assert ConversionMode.FAST_OCR.value == "fast_ocr"
    
    def test_output_format_enum(self):
        """Test OutputFormat enum."""
        assert OutputFormat.MARKDOWN.value == "markdown"
        assert OutputFormat.TXT.value == "txt"
        assert OutputFormat.JSON.value == "json"


class TestErrorHandling:
    """Test cases for error handling."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = HashubDocClient(api_key="test_api_key")
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        with pytest.raises(AuthenticationError):
            self.client._make_request('GET', '/test')
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_rate_limit_error(self, mock_request):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            self.client._make_request('GET', '/test')
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_generic_http_error(self, mock_request):
        """Test generic HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        mock_request.return_value = mock_response
        
        with pytest.raises(HashubDocError) as exc_info:
            self.client._make_request('GET', '/test')
        
        assert exc_info.value.status_code == 500
    
    @patch('hashub_docapp.client.requests.Session.request')
    def test_connection_timeout(self, mock_request):
        """Test connection timeout handling."""
        import requests
        mock_request.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(Exception):  # TimeoutError
            self.client._make_request('GET', '/test')


if __name__ == "__main__":
    pytest.main([__file__])
