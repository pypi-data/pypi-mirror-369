"""
Command Line Interface for Hashub DocApp SDK

Provides a command-line interface for document conversion operations.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from .client import HashubDocClient
from .exceptions import HashubDocError


def setup_client(api_key: Optional[str] = None) -> HashubDocClient:
    """Setup and return configured client."""
    try:
        return HashubDocClient(api_key=api_key)
    except Exception as e:
        print(f"Error initializing client: {e}")
        sys.exit(1)


def convert_command(args):
    """Handle convert command."""
    client = setup_client(args.api_key)
    
    try:
        if args.mode == "smart":
            result = client.convert_smart(args.input, output=args.output)
        elif args.mode == "fast":
            result = client.convert_fast(args.input, output=args.output)
        elif args.mode == "layout":
            result = client.convert_layout(args.input, output=args.output)
        else:
            result = client.convert_file(
                path=args.input,
                output=args.output,
                mode=args.mode,
                smart=args.smart
            )
            
            if not args.no_wait:
                print(f"Job started: {result['job_id']}")
                print("Waiting for completion...")
                final_result = client.wait(result['job_id'])
                result = client.get_result(result['job_id'])
        
        # Save output
        if args.output_file:
            output_path = Path(args.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if result.get('content'):
                    f.write(result['content'])
                else:
                    json.dump(result, f, indent=2)
            
            print(f"Output saved to: {output_path}")
        else:
            if result.get('content'):
                print(result['content'])
            else:
                print(json.dumps(result, indent=2))
                
    except HashubDocError as e:
        print(f"Conversion error: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def batch_command(args):
    """Handle batch conversion command."""
    client = setup_client(args.api_key)
    
    # Get input files
    if args.input_dir:
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            print(f"Input directory not found: {input_dir}")
            sys.exit(1)
        
        pattern = args.pattern or "*"
        files = list(input_dir.glob(pattern))
        file_paths = [str(f) for f in files if f.is_file()]
    else:
        file_paths = args.files
    
    if not file_paths:
        print("No files to process")
        sys.exit(1)
    
    print(f"Processing {len(file_paths)} files...")
    
    try:
        results = client.batch_convert(
            items=file_paths,
            mode=args.mode,
            output=args.output,
            concurrency=args.concurrency
        )
        
        # Process results
        successful = 0
        failed = 0
        
        for result in results:
            if result.get('error'):
                print(f"❌ Failed: {result.get('file_path', 'unknown')} - {result['error']}")
                failed += 1
            else:
                print(f"✅ Success: {result['filename']}")
                successful += 1
                
                # Save individual output if output directory specified
                if args.output_dir:
                    output_dir = Path(args.output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    base_name = Path(result['filename']).stem
                    ext = 'md' if args.output == 'markdown' else args.output
                    output_file = output_dir / f"{base_name}.{ext}"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        if result.get('content'):
                            f.write(result['content'])
                        else:
                            json.dump(result, f, indent=2)
        
        print(f"\nSummary: {successful} successful, {failed} failed")
        
    except Exception as e:
        print(f"Batch processing error: {e}")
        sys.exit(1)


def status_command(args):
    """Handle status check command."""
    client = setup_client(args.api_key)
    
    try:
        status = client.get_status(args.job_id)
        print(json.dumps(status, indent=2))
        
        if args.wait and status['status'] not in ['completed', 'failed', 'cancelled']:
            print("Waiting for completion...")
            final_status = client.wait(args.job_id)
            print("\nFinal status:")
            print(json.dumps(final_status, indent=2))
            
    except Exception as e:
        print(f"Status check error: {e}")
        sys.exit(1)


def list_command(args):
    """Handle list jobs command."""
    client = setup_client(args.api_key)
    
    try:
        jobs = client.list_jobs(limit=args.limit, status=args.status)
        
        if args.format == 'json':
            print(json.dumps(jobs, indent=2))
        else:
            print(f"{'Job ID':<20} {'Status':<12} {'Filename':<30} {'Created'}")
            print("-" * 80)
            for job in jobs:
                print(f"{job['job_id']:<20} {job['status']:<12} {job.get('filename', 'N/A'):<30} {job.get('created_at', 'N/A')}")
                
    except Exception as e:
        print(f"List jobs error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hashub DocApp CLI - Professional Document Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert PDF to Markdown (smart mode)
  hashub-docapp convert document.pdf --mode smart --output markdown

  # Fast text extraction
  hashub-docapp convert scan.jpg --mode fast --output txt

  # Batch convert all PDFs in directory
  hashub-docapp batch --input-dir ./docs --pattern "*.pdf" --output-dir ./output

  # Check job status
  hashub-docapp status job_abc123def456

  # List recent jobs
  hashub-docapp list --limit 10
        """
    )
    
    parser.add_argument(
        '--api-key',
        help='API key (or set HASHUB_API_KEY environment variable)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert a document')
    convert_parser.add_argument('input', help='Input file path')
    convert_parser.add_argument('--output', '-o', default='markdown',
                               choices=['markdown', 'txt', 'json', 'html', 'pdf'],
                               help='Output format')
    convert_parser.add_argument('--mode', '-m', default='auto',
                               choices=['auto', 'fast', 'smart', 'layout', 'fast_ocr', 'smart_ocr', 'layout_json'],
                               help='Processing mode')
    convert_parser.add_argument('--output-file', '-f', help='Output file path')
    convert_parser.add_argument('--smart', action='store_true', default=True,
                               help='Enable smart processing')
    convert_parser.add_argument('--no-wait', action='store_true',
                               help='Don\'t wait for completion, just start job')
    convert_parser.set_defaults(func=convert_command)
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch convert multiple documents')
    batch_group = batch_parser.add_mutually_exclusive_group(required=True)
    batch_group.add_argument('--input-dir', help='Input directory path')
    batch_group.add_argument('--files', nargs='+', help='List of file paths')
    batch_parser.add_argument('--pattern', help='File pattern for directory mode (e.g., "*.pdf")')
    batch_parser.add_argument('--output', '-o', default='markdown',
                             choices=['markdown', 'txt', 'json', 'html'],
                             help='Output format')
    batch_parser.add_argument('--mode', '-m', default='auto',
                             choices=['auto', 'fast_ocr', 'smart_ocr', 'layout_json'],
                             help='Processing mode')
    batch_parser.add_argument('--output-dir', help='Output directory for results')
    batch_parser.add_argument('--concurrency', '-c', type=int, default=3,
                             help='Number of concurrent conversions')
    batch_parser.set_defaults(func=batch_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check job status')
    status_parser.add_argument('job_id', help='Job ID to check')
    status_parser.add_argument('--wait', '-w', action='store_true',
                              help='Wait for job completion')
    status_parser.set_defaults(func=status_command)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recent jobs')
    list_parser.add_argument('--limit', '-l', type=int, default=20,
                            help='Maximum number of jobs to list')
    list_parser.add_argument('--status', '-s', 
                            choices=['queued', 'processing', 'completed', 'failed', 'cancelled'],
                            help='Filter by status')
    list_parser.add_argument('--format', choices=['table', 'json'], default='table',
                            help='Output format')
    list_parser.set_defaults(func=list_command)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
