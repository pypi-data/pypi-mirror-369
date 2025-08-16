"""
Basic Usage Examples for Hashub DocApp SDK

This file demonstrates the core functionality of the SDK with simple examples.
"""

import os
from hashub_docapp import HashubDocClient, HashubDocError

# Initialize client (API key from environment variable)
client = HashubDocClient()

def example_convert_smart():
    """Example: Convert PDF with smart processing to Markdown"""
    print("=== Smart Conversion Example ===")
    
    try:
        # Convert with high-quality smart processing
        result = client.convert_smart("sample.pdf", output="markdown")
        
        print(f"Conversion successful!")
        print(f"Job ID: {result['job_id']}")
        print(f"Status: {result['status']}")
        print(f"Content preview (first 200 chars):")
        print(result['content'][:200] + "..." if len(result['content']) > 200 else result['content'])
        
    except FileNotFoundError:
        print("Error: sample.pdf not found. Please provide a valid PDF file.")
    except HashubDocError as e:
        print(f"API Error: {e.message}")


def example_convert_fast():
    """Example: Fast text extraction"""
    print("\n=== Fast Conversion Example ===")
    
    try:
        # Quick text extraction
        result = client.convert_fast("document.jpg", output="txt")
        
        print(f"Fast conversion successful!")
        print(f"Extracted text:")
        print(result['content'])
        
    except FileNotFoundError:
        print("Error: document.jpg not found. Please provide a valid image file.")
    except HashubDocError as e:
        print(f"API Error: {e.message}")


def example_async_conversion():
    """Example: Asynchronous conversion with status monitoring"""
    print("\n=== Async Conversion Example ===")
    
    try:
        # Start conversion
        result = client.convert_file(
            path="large_document.pdf",
            output="json",
            mode="layout_json",
            smart=True
        )
        
        job_id = result['job_id']
        print(f"Conversion started. Job ID: {job_id}")
        
        # Monitor progress
        print("Monitoring progress...")
        for status in client.stream_progress(job_id):
            print(f"Progress: {status['progress']}% - {status['step']}")
            
            if status['status'] == 'completed':
                final_result = client.get_result(job_id)
                print("Conversion completed successfully!")
                break
            elif status['status'] == 'failed':
                print(f"Conversion failed: {status.get('error_details', 'Unknown error')}")
                break
        
    except FileNotFoundError:
        print("Error: large_document.pdf not found.")
    except HashubDocError as e:
        print(f"API Error: {e.message}")


def example_batch_conversion():
    """Example: Batch processing multiple files"""
    print("\n=== Batch Conversion Example ===")
    
    files = ["doc1.pdf", "doc2.jpg", "doc3.png"]
    
    try:
        # Process multiple files
        results = client.batch_convert(
            items=files,
            mode="smart_ocr",
            output="markdown",
            concurrency=2
        )
        
        print(f"Batch processing completed for {len(files)} files:")
        
        for result in results:
            if result.get('error'):
                print(f"❌ Failed: {result.get('file_path', 'unknown')} - {result['error']}")
            else:
                print(f"✅ Success: {result['filename']}")
                
    except HashubDocError as e:
        print(f"Batch processing error: {e.message}")


def example_region_ocr():
    """Example: Extract text from specific regions"""
    print("\n=== Region OCR Example ===")
    
    try:
        # Define regions to extract
        regions = [
            {"x": 100, "y": 50, "w": 400, "h": 100},   # Header region
            {"x": 50, "y": 200, "w": 500, "h": 300},   # Main content
            {"x": 400, "y": 550, "w": 150, "h": 50},   # Footer/signature
        ]
        
        result = client.convert_bbox(
            "form.pdf",
            regions=regions,
            output="json"
        )
        
        print("Region-based OCR completed!")
        
        # Parse JSON result
        import json
        data = json.loads(result['content'])
        
        for i, region_data in enumerate(data.get('regions', [])):
            print(f"Region {i+1}: {region_data.get('text', 'No text found')}")
            
    except FileNotFoundError:
        print("Error: form.pdf not found.")
    except HashubDocError as e:
        print(f"API Error: {e.message}")


def example_utility_functions():
    """Example: Using utility functions"""
    print("\n=== Utility Functions Example ===")
    
    try:
        # Check API health
        if client.ping():
            print("✅ API is accessible")
        else:
            print("❌ API is not accessible")
        
        # Validate API key
        if client.validate_api_key():
            print("✅ API key is valid")
        else:
            print("❌ API key is invalid")
        
        # Get supported formats
        formats = client.get_supported_formats()
        print(f"Supported input formats: {', '.join(formats['input_formats'])}")
        print(f"Supported output formats: {', '.join(formats['output_formats'])}")
        
        # List recent jobs
        jobs = client.list_jobs(limit=5)
        print(f"Recent jobs ({len(jobs)}):")
        for job in jobs:
            print(f"  - {job['job_id']}: {job['status']} ({job.get('filename', 'N/A')})")
            
    except HashubDocError as e:
        print(f"API Error: {e.message}")


def main():
    """Run all examples"""
    print("Hashub DocApp SDK - Basic Usage Examples")
    print("=" * 50)
    
    # Check if API key is set
    if not client.api_key:
        print("Please set HASHUB_API_KEY environment variable or provide API key.")
        return
    
    # Run examples
    example_utility_functions()
    example_convert_smart()
    example_convert_fast()
    example_async_conversion()
    example_batch_conversion()
    example_region_ocr()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
