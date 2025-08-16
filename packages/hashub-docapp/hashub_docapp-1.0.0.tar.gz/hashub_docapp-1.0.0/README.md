# HashubDocApp Python SDK

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production-brightgreen.svg)](https://github.com)

Professional Python SDK for the HashubDocApp API - Advanced OCR, document conversion, and text extraction service.

## ✨ Features

- 🚀 **Fast OCR**: Quick text extraction with 76+ language support
- 🧠 **Smart OCR**: High-quality OCR with layout preservation
- 📄 **Document Conversion**: Office documents (Word, Excel) and HTML to Markdown/Text
- 🔄 **Batch Processing**: Process multiple files with intelligent categorization
- 🌍 **Multi-language**: Support for 76+ languages with ISO 639-1 codes
- 🎨 **Image Enhancement**: 11 pre-configured enhancement presets
- 📊 **Progress Tracking**: Real-time progress bars and status monitoring
- ⚡ **Rate Limiting**: Built-in API throttling protection

## 🚀 Quick Start

### Installation

```bash
pip install hashub-docapp
```

### Basic Usage

```python
from hashub_docapp import DocAppClient

# Initialize client
client = DocAppClient("your_api_key_here")

# Fast OCR - Quick text extraction
text = client.convert_fast("document.pdf", language="en")
print(text)

# Smart OCR - High-quality with layout preservation  
markdown = client.convert_smart("document.pdf")
print(markdown)
```

## 📖 Core Methods

### `convert_fast()`
Fast OCR for quick text extraction with language support.

```python
def convert_fast(
    file_or_image: Union[str, Path], 
    output: str = "markdown",
    language: str = "en",
    enhancement: Optional[str] = None,
    return_type: ReturnType = "content",
    save_to: Optional[Union[str, Path]] = None,
    show_progress: bool = True,
    timeout: int = 300
) -> Union[str, Path]
```

**Parameters:**
- `file_or_image`: Path to PDF or image file
- `output`: Output format ("markdown", "txt", "json")
- `language`: Language code (ISO 639-1 like "en", "tr", "de")
- `enhancement`: Image enhancement preset (optional)
- `return_type`: "content" (default), "url", or "file"
- `save_to`: File path when return_type="file"
- `show_progress`: Show progress bar (default: True)
- `timeout`: Maximum wait time in seconds (default: 300)

**Examples:**
```python
# Basic fast OCR
text = client.convert_fast("scan.pdf")

# With Turkish language
text = client.convert_fast("document.pdf", language="tr")

# With enhancement for low-quality scans
text = client.convert_fast("scan.pdf", enhancement="scan_low_dpi")

# Save to file
client.convert_fast("document.pdf", return_type="file", save_to="output.txt")
```

### `convert_smart()`
High-quality OCR with layout preservation and structure detection.

```python
def convert_smart(
    file_or_image: Union[str, Path], 
    output: str = "markdown",
    return_type: ReturnType = "content",
    save_to: Optional[Union[str, Path]] = None,
    show_progress: bool = True,
    timeout: int = 300
) -> Union[str, Path]
```

**Parameters:**
- `file_or_image`: Path to PDF or image file
- `output`: Output format ("markdown", "txt", "json")
- `return_type`: "content" (default), "url", or "file"
- `save_to`: File path when return_type="file"
- `show_progress`: Show progress bar (default: True)
- `timeout`: Maximum wait time in seconds (default: 300)

**Examples:**
```python
# Smart OCR with layout preservation
markdown = client.convert_smart("complex_document.pdf")

# Save as file
client.convert_smart("document.pdf", return_type="file", save_to="output.md")

# Different output format
json_data = client.convert_smart("document.pdf", output="json")
```

## 🌍 Language Support

The SDK supports 76+ languages with ISO 639-1 codes:

```python
from hashub_docapp.languages import LanguageHelper

# List all supported languages
languages = LanguageHelper.list_languages()
print(f"Supported languages: {len(languages)}")

# Get language info
turkish_info = LanguageHelper.get_language_info("tr")
print(turkish_info)  # {'english': 'Turkish', 'native': 'Türkçe', 'iso': 'tr', 'api_code': 'lang_tur_tr'}

# Use with convert_fast
text = client.convert_fast("document.pdf", language="tr")  # Turkish
text = client.convert_fast("document.pdf", language="de")  # German
text = client.convert_fast("document.pdf", language="zh")  # Chinese
```

**Popular Language Codes:**
- `en` - English
- `tr` - Turkish  
- `de` - German
- `fr` - French
- `es` - Spanish
- `zh` - Chinese (Simplified)
- `ar` - Arabic
- `ru` - Russian
- `ja` - Japanese
- `ko` - Korean

## 🎨 Image Enhancement Presets

The SDK includes 11 pre-configured enhancement presets for different document types:

```python
# Enhancement presets (use with convert_fast)
client.convert_fast("scan.pdf", enhancement="document_crisp")     # Clean documents
client.convert_fast("scan.pdf", enhancement="scan_low_dpi")       # Low quality scans
client.convert_fast("scan.pdf", enhancement="camera_shadow")      # Phone photos
client.convert_fast("scan.pdf", enhancement="photocopy_faded")    # Faded copies
client.convert_fast("scan.pdf", enhancement="inverted_scan")      # Inverted colors
client.convert_fast("scan.pdf", enhancement="noisy_dots")         # Noisy artifacts
client.convert_fast("scan.pdf", enhancement="tables_fine")        # Tables and grids
client.convert_fast("scan.pdf", enhancement="receipt_thermal")    # Receipts
client.convert_fast("scan.pdf", enhancement="newspaper_moire")    # Newspapers
client.convert_fast("scan.pdf", enhancement="fax_low_quality")    # Fax documents
client.convert_fast("scan.pdf", enhancement="blueprint")          # Technical drawings
```

## 📄 Document Conversion

### `convert_doc()`
Convert Word, Excel, and other office documents.

```python
def convert_doc(
    path: Union[str, Path], 
    output: str = "markdown",
    return_type: ReturnType = "content",
    save_to: Optional[Union[str, Path]] = None,
    options: Optional[Dict[str, Any]] = None
) -> Union[str, Path]
```

**Examples:**
```python
# Convert Word document to Markdown
markdown = client.convert_doc("document.docx")

# Convert Excel to text
text = client.convert_doc("spreadsheet.xlsx", output="txt")

# Save to file
client.convert_doc("presentation.pptx", return_type="file", save_to="output.md")
```

### `convert_html_string()`
Convert HTML string content to other formats.

```python
def convert_html_string(
    html_content: str, 
    output: str = "markdown",
    return_type: ReturnType = "content",
    save_to: Optional[Union[str, Path]] = None,
    options: Optional[Dict[str, Any]] = None
) -> Union[str, Path]
```

**Examples:**
```python
html = "<h1>Title</h1><p>Content</p>"
markdown = client.convert_html_string(html)
```

## 🔄 Batch Processing

### `batch_convert_smart()`
Smart batch processing with automatic file categorization.

```python
def batch_convert_smart(
    directory: Union[str, Path],
    save_to: Union[str, Path],
    output_format: str = "txt",
    recursive: bool = True,
    show_progress: bool = True,
    max_workers: int = 3,
    timeout: int = 600
) -> Dict[str, Any]
```

**Example:**
```python
# Process all files in directory intelligently
results = client.batch_convert_smart(
    directory="./documents",
    save_to="./output",
    output_format="markdown"
)

print(f"Processed {results['processed_count']} files")
print(f"Success: {results['success_count']}, Failed: {results['failed_count']}")
```

### `batch_convert_fast()`
Fast batch OCR for images and PDFs.

```python
def batch_convert_fast(
    directory: Union[str, Path],
    save_to: Union[str, Path],
    language: str = "en",
    enhancement: Optional[str] = None,
    output_format: str = "txt",
    recursive: bool = True,
    show_progress: bool = True,
    max_workers: int = 5,
    timeout: int = 300
) -> Dict[str, Any]
```

### `batch_convert_auto()`
Automatic processing mode selection based on file types.

```python
def batch_convert_auto(
    directory: Union[str, Path],
    save_to: Union[str, Path],
    language: str = "en",
    enhancement: Optional[str] = None,
    output_format: str = "txt",
    recursive: bool = True,
    show_progress: bool = True,
    max_workers: int = 4,
    timeout: int = 900
) -> Dict[str, Any]
```

## 📊 Return Types

The SDK supports three return types for conversion methods:

### 1. Content (Default)
```python
text = client.convert_fast("doc.pdf", return_type="content")
print(text)  # Direct text content
```

### 2. URL
```python
url = client.convert_fast("doc.pdf", return_type="url") 
print(url)   # Download URL for the result
```

### 3. File
```python
path = client.convert_fast(
    "doc.pdf", 
    return_type="file", 
    save_to="output.txt"
)
print(path)  # Path to saved file
```

## 🛠️ Job Management

### `get_status()`
Check job status.

```python
status = client.get_status(job_id)
print(f"Status: {status['status']}")
print(f"Progress: {status.get('progress', 0)}%")
```

### `wait()`
Wait for job completion with polling.

```python
final_status = client.wait(job_id, interval=2.0, timeout=300)
```

### `get_result()`
Get completed job result.

```python
result = client.get_result(job_id)
print(result['content'])  # The extracted/converted text
```

### `cancel()`
Cancel a running job.

```python
client.cancel(job_id)
```

## 🔧 Configuration

### Environment Variables

```bash
export HASHUB_API_KEY="your_api_key_here"
```

### Client Configuration

```python
client = DocAppClient(
    api_key="your_api_key",
    base_url="https://doc.hashub.dev/api/v1",  # Default
    timeout=(30, 120),                         # (connect, read) timeout
    max_retries=3,                            # Max retry attempts
    rate_limit_delay=2.0                      # Min delay between requests
)
```

## 🎯 Usage Examples

### Basic OCR

```python
from hashub_docapp import DocAppClient

client = DocAppClient("your_api_key")

# Extract text from PDF
text = client.convert_fast("invoice.pdf", language="en")
print(text)

# High-quality OCR with layout
markdown = client.convert_smart("complex_document.pdf")
print(markdown)
```

### Multi-language Processing

```python
# Process documents in different languages
documents = [
    ("english_doc.pdf", "en"),
    ("turkish_doc.pdf", "tr"), 
    ("german_doc.pdf", "de"),
    ("chinese_doc.pdf", "zh")
]

for doc_path, lang in documents:
    text = client.convert_fast(doc_path, language=lang)
    print(f"{lang}: {text[:100]}...")
```

### Enhanced Image Processing

```python
# Process different types of scanned documents
scan_types = {
    "old_book.pdf": "scan_low_dpi",
    "phone_photo.jpg": "camera_shadow", 
    "faded_copy.pdf": "photocopy_faded",
    "receipt.jpg": "receipt_thermal",
    "technical_drawing.pdf": "blueprint"
}

for file_path, enhancement in scan_types.items():
    text = client.convert_fast(
        file_path, 
        enhancement=enhancement,
        language="en"
    )
    print(f"Processed {file_path} with {enhancement}")
```

### Batch Processing Example

```python
# Process entire directory
results = client.batch_convert_auto(
    directory="./input_docs",
    save_to="./output",
    output_format="markdown",
    show_progress=True
)

print(f"✅ Processed {results['success_count']} files successfully")
for file_result in results['results']:
    if file_result['status'] == 'success':
        print(f"  📄 {file_result['source_file']} -> {file_result['output_file']}")
```

## 🛡️ Error Handling

```python
from hashub_docapp import DocAppClient
from hashub_docapp.exceptions import (
    AuthenticationError, 
    RateLimitError, 
    ProcessingError,
    ValidationError
)

client = DocAppClient("your_api_key")

try:
    result = client.convert_fast("document.pdf")
    print(result)
    
except AuthenticationError:
    print("❌ Invalid API key")
    
except RateLimitError:
    print("⏳ Rate limit exceeded, wait and retry")
    
except ProcessingError as e:
    print(f"💥 Processing failed: {e}")
    
except ValidationError as e:
    print(f"📝 Validation error: {e}")
    
except FileNotFoundError:
    print("📁 File not found")
```

## 🔄 Rate Limiting

The SDK includes built-in rate limiting to prevent API throttling:

- **Default delay**: 2 seconds between requests
- **Automatic retry**: Failed requests are retried with exponential backoff
- **Progress tracking**: Polls job status with appropriate intervals

```python
# Configure rate limiting
client = DocAppClient(
    api_key="your_key",
    rate_limit_delay=3.0,  # 3 second delay between requests
    max_retries=5          # Retry failed requests up to 5 times
)
```

## 📈 Performance Tips

1. **Use appropriate modes**:
   - `convert_fast()` for simple text extraction with language support
   - `convert_smart()` for complex layouts and formatting

2. **Batch processing**:
   - Use batch methods for multiple files
   - Adjust `max_workers` based on your API limits

3. **Language specification**:
   - Always specify the correct language for better accuracy
   - Use ISO codes for convenience (`"en"`, `"tr"`, `"de"`)

4. **Enhancement presets**:
   - Choose the right preset for your document type
   - Experiment with different presets for optimal results

## 🐛 Troubleshooting

### Common Issues

**1. 404 Errors**
```python
# Ensure correct base URL
client = DocAppClient(
    api_key="your_key",
    base_url="https://doc.hashub.dev/api/v1"
)
```

**2. Rate Limiting**
```python
# Increase delay between requests
client = DocAppClient(
    api_key="your_key", 
    rate_limit_delay=3.0
)
```

**3. Timeout Issues**
```python
# Increase timeout for large files
result = client.convert_smart("large_file.pdf", timeout=600)
```

**4. Language Errors**
```python
# Check supported languages
from hashub_docapp.languages import LanguageHelper
languages = LanguageHelper.list_languages()
print([lang['iso'] for lang in languages])
```

## 📊 API Method Summary

| Method | Purpose | Key Parameters | Returns |
|--------|---------|----------------|---------|
| `convert_fast()` | Fast OCR | file_path, language, enhancement | str/Path |
| `convert_smart()` | Smart OCR | file_path, output | str/Path |
| `convert_doc()` | Office docs | file_path, output | str/Path |
| `convert_html_string()` | HTML conversion | html_content, output | str/Path |
| `batch_convert_smart()` | Smart batch | directory, save_to | Dict |
| `batch_convert_fast()` | Fast batch | directory, save_to, language | Dict |
| `batch_convert_auto()` | Auto batch | directory, save_to | Dict |

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: [HashubDocApp Docs](https://doc.hashub.dev)
- **API Reference**: [API Documentation](https://doc.hashub.dev/api)
- **Support**: [Contact Support](mailto:support@hashub.dev)

---

**Made with ❤️ by the Hashub Team**
