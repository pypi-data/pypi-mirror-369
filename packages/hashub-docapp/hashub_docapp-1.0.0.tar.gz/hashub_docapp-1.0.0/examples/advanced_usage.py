"""
Advanced Usage Examples for Hashub DocApp SDK

This file demonstrates advanced features and use cases.
"""

import json
import time
from pathlib import Path
from hashub_docapp import HashubDocClient, OCROptions, ProcessingOptions

# Initialize client
client = HashubDocClient()


def example_custom_ocr_options():
    """Example: Using custom OCR options"""
    print("=== Custom OCR Options Example ===")
    
    try:
        # Configure advanced OCR options
        ocr_options = OCROptions(
            language="lang_eng_en",
            chunk_size=3,
            psm_mode=6,
            confidence_threshold=85,
            enhance_options={
                "preset": "scan_high",
                "overrides": {
                    "contrast": 1.5,
                    "sharpness": 1.3,
                    "deskew": True,
                    "noise_reduction": True
                }
            }
        )
        
        # Convert with custom options
        result = client.convert_file(
            path="scanned_document.pdf",
            output="markdown",
            mode="smart_ocr",
            smart=True,
            ocr_options=ocr_options.__dict__,
            priority=8,  # High priority
            tags=["invoice", "accounting"],
            custom_data={"department": "finance", "project": "q4_processing"}
        )
        
        job_id = result['job_id']
        print(f"High-quality OCR job started: {job_id}")
        
        # Wait and get result
        final_result = client.wait(job_id)
        content = client.get_result(job_id)
        
        print("OCR completed with custom settings!")
        print(f"Content length: {len(content['content'])} characters")
        
    except Exception as e:
        print(f"Error: {e}")


def example_document_analysis():
    """Example: Comprehensive document analysis"""
    print("\n=== Document Analysis Example ===")
    
    try:
        # First, get layout information
        layout_result = client.convert_layout("report.pdf", output="json")
        layout_data = json.loads(layout_result['content'])
        
        print("Document structure analysis:")
        print(f"- Pages: {layout_data.get('page_count', 'N/A')}")
        print(f"- Detected elements: {len(layout_data.get('elements', []))}")
        
        # Analyze document elements
        tables = [e for e in layout_data.get('elements', []) if e.get('type') == 'table']
        images = [e for e in layout_data.get('elements', []) if e.get('type') == 'image']
        text_blocks = [e for e in layout_data.get('elements', []) if e.get('type') == 'text']
        
        print(f"- Tables found: {len(tables)}")
        print(f"- Images found: {len(images)}")
        print(f"- Text blocks: {len(text_blocks)}")
        
        # Extract tables if found
        if tables:
            print("\nTable content preview:")
            for i, table in enumerate(tables[:2]):  # Show first 2 tables
                print(f"Table {i+1}: {table.get('content', 'No content')[:100]}...")
        
        # Then get clean markdown version
        markdown_result = client.convert_smart("report.pdf", output="markdown")
        
        # Save both versions
        with open("report_structure.json", "w") as f:
            json.dump(layout_data, f, indent=2)
        
        with open("report_content.md", "w") as f:
            f.write(markdown_result['content'])
        
        print("Analysis completed! Files saved: report_structure.json, report_content.md")
        
    except Exception as e:
        print(f"Error: {e}")


def example_webhook_integration():
    """Example: Webhook integration for async processing"""
    print("\n=== Webhook Integration Example ===")
    
    try:
        # Register webhook (replace with your actual webhook URL)
        webhook_url = "https://your-app.com/webhooks/hashub"
        webhook_secret = "your_secure_secret_here"
        
        webhook_info = client.register_webhook(
            url=webhook_url,
            secret=webhook_secret
        )
        
        print(f"Webhook registered: {webhook_info}")
        
        # Start a job that will trigger webhook
        result = client.convert_file(
            path="async_document.pdf",
            output="markdown",
            mode="smart_ocr",
            smart=True,
            custom_data={"webhook_id": "doc_process_001"}
        )
        
        print(f"Job started: {result['job_id']}")
        print(f"Webhook will be triggered at: {webhook_url}")
        print("Your webhook handler should verify the signature and process the result.")
        
    except Exception as e:
        print(f"Error: {e}")


def example_batch_processing_with_filtering():
    """Example: Advanced batch processing with filtering and organization"""
    print("\n=== Advanced Batch Processing Example ===")
    
    try:
        # Setup directories
        input_dir = Path("input_documents")
        output_dir = Path("processed_documents")
        output_dir.mkdir(exist_ok=True)
        
        # Get all files and categorize
        pdf_files = list(input_dir.glob("*.pdf"))
        image_files = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))
        office_files = list(input_dir.glob("*.docx")) + list(input_dir.glob("*.xlsx"))
        
        print(f"Found {len(pdf_files)} PDFs, {len(image_files)} images, {len(office_files)} office docs")
        
        # Process different types with different settings
        all_results = []
        
        # Process PDFs with smart OCR
        if pdf_files:
            print("Processing PDFs with smart OCR...")
            pdf_results = client.batch_convert(
                items=[str(f) for f in pdf_files],
                mode="smart_ocr",
                output="markdown",
                concurrency=3
            )
            all_results.extend(pdf_results)
        
        # Process images with fast OCR
        if image_files:
            print("Processing images with fast OCR...")
            image_results = client.batch_convert(
                items=[str(f) for f in image_files],
                mode="fast_ocr",
                output="txt",
                concurrency=2
            )
            all_results.extend(image_results)
        
        # Process office documents
        if office_files:
            print("Processing office documents...")
            for office_file in office_files:
                try:
                    office_result = client.convert_doc(
                        str(office_file),
                        output="markdown",
                        options={"sanitize_level": "medium", "readability": True}
                    )
                    all_results.append(office_result)
                except Exception as e:
                    print(f"Failed to process {office_file}: {e}")
        
        # Organize results
        successful_results = []
        failed_results = []
        
        for result in all_results:
            if result.get('error'):
                failed_results.append(result)
            else:
                successful_results.append(result)
                
                # Save to organized folders
                file_type = Path(result['filename']).suffix.lower()
                type_dir = output_dir / file_type[1:]  # Remove the dot
                type_dir.mkdir(exist_ok=True)
                
                # Determine output extension
                if result.get('output_format') == 'markdown':
                    ext = '.md'
                elif result.get('output_format') == 'txt':
                    ext = '.txt'
                else:
                    ext = '.json'
                
                output_file = type_dir / f"{Path(result['filename']).stem}{ext}"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('content', ''))
                
                print(f"✅ Saved: {output_file}")
        
        # Summary report
        print(f"\nBatch processing summary:")
        print(f"✅ Successful: {len(successful_results)}")
        print(f"❌ Failed: {len(failed_results)}")
        
        if failed_results:
            print("\nFailed files:")
            for failed in failed_results:
                print(f"  - {failed.get('file_path', 'unknown')}: {failed.get('error', 'unknown error')}")
        
        # Generate summary report
        summary = {
            "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_files": len(all_results),
            "successful": len(successful_results),
            "failed": len(failed_results),
            "successful_files": [r['filename'] for r in successful_results],
            "failed_files": [{"file": r.get('file_path'), "error": r.get('error')} for r in failed_results]
        }
        
        with open(output_dir / "processing_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"Summary saved to: {output_dir}/processing_summary.json")
        
    except Exception as e:
        print(f"Error: {e}")


def example_error_handling_and_retry():
    """Example: Comprehensive error handling and retry logic"""
    print("\n=== Error Handling and Retry Example ===")
    
    try:
        # Configure client with custom retry settings
        client.set_retries(max_retries=5, backoff=(0.5, 3.0))
        client.set_timeout(connect=30, read=180)
        
        # List of files to process (some might not exist)
        files_to_process = [
            "existing_document.pdf",
            "nonexistent_file.pdf",
            "corrupted_document.pdf",
            "large_document.pdf"
        ]
        
        results = []
        
        for file_path in files_to_process:
            try:
                print(f"Processing: {file_path}")
                
                # Try conversion with error handling
                result = client.convert_smart(file_path)
                results.append({
                    "file": file_path,
                    "status": "success",
                    "job_id": result['job_id']
                })
                
                print(f"✅ Success: {file_path}")
                
            except FileNotFoundError:
                print(f"❌ File not found: {file_path}")
                results.append({
                    "file": file_path,
                    "status": "file_not_found",
                    "error": "File does not exist"
                })
                
            except Exception as e:
                print(f"❌ Processing failed: {file_path} - {e}")
                results.append({
                    "file": file_path,
                    "status": "processing_failed",
                    "error": str(e)
                })
                
                # Wait before next attempt
                time.sleep(2)
        
        # Summary
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] != 'success']
        
        print(f"\nProcessing completed:")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run advanced examples"""
    print("Hashub DocApp SDK - Advanced Usage Examples")
    print("=" * 50)
    
    # Check API key
    if not client.api_key:
        print("Please set HASHUB_API_KEY environment variable.")
        return
    
    # Run advanced examples
    example_custom_ocr_options()
    example_document_analysis()
    example_webhook_integration()
    example_batch_processing_with_filtering()
    example_error_handling_and_retry()
    
    print("\n" + "=" * 50)
    print("Advanced examples completed!")


if __name__ == "__main__":
    main()
