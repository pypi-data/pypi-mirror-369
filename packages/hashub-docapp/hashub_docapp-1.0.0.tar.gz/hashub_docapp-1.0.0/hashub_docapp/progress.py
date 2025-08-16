"""
Progress tracking utilities for Hashub DocApp SDK

Based on convert_progress.py implementation with interactive progress bars.
"""

import sys
import time
from typing import Optional, Dict, Any, Callable


def render_progress_line(
    progress_percent: int,
    step: str,
    current_page: Optional[int] = None,
    total_pages: Optional[int] = None,
    eta: Optional[float] = None,
    elapsed: float = 0,
    width: int = 80
) -> str:
    """
    Render a single-line progress bar for terminal display.
    
    Args:
        progress_percent: Progress percentage (0-100)
        step: Current processing step description
        current_page: Current page being processed
        total_pages: Total number of pages
        eta: Estimated time remaining in seconds
        elapsed: Elapsed time in seconds
        width: Terminal width for the progress bar
        
    Returns:
        Formatted progress line string
    """
    bar_len = 24
    p = max(0, min(100, int(progress_percent or 0)))
    filled = int(bar_len * p / 100)
    bar = "█" * filled + "░" * (bar_len - filled)

    page_info = f"[{current_page:02d}/{total_pages:02d}]" if (current_page and total_pages) else "[--/--]"
    eta_info = f" ETA:{eta:.1f}s" if eta is not None else ""
    
    # Shorten step description
    step = step or ""
    step_low = step.lower()
    if "ocr" in step_low:
        step_tag = "📄 OCR"
    elif "convert" in step_low or "markdown" in step_low:
        step_tag = "🔄 Convert"
    elif "valid" in step_low:
        step_tag = "✓ Valid"
    elif "initial" in step_low or "start" in step_low:
        step_tag = "🚀 Init"
    elif "complete" in step_low:
        step_tag = "✅ Done"
    elif "pdf" in step_low:
        step_tag = "📋 PDF"
    else:
        step_tag = f"📋 {step[:16]}{'…' if len(step) > 16 else ''}"

    line = f"[{bar}] {p:3d}% {page_info} {elapsed:5.1f}s{eta_info} {step_tag}"
    if len(line) > width:
        return line[:width-3] + "..."
    return line


def poll_job_with_progress(
    client,
    job_id: str,
    interval: float = 3.0,  # Increased default interval to avoid rate limiting
    timeout: Optional[int] = None,  # Auto-calculate if None
    show_progress: bool = True,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Poll job status with interactive progress tracking.
    
    Args:
        client: HashubDocClient instance
        job_id: Job identifier to poll
        interval: Polling interval in seconds (minimum 2.0s to avoid rate limits)
        timeout: Maximum wait time in seconds (auto-calculated if None)
        show_progress: Whether to show progress bar in terminal
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Final job status data
        
    Raises:
        TimeoutError: If job doesn't complete within timeout
        ProcessingError: If job fails
    """
    from .exceptions import TimeoutError as SDKTimeoutError, ProcessingError
    
    # Auto-calculate timeout if not provided
    if timeout is None:
        if hasattr(client, '_calculate_timeout'):
            timeout = client._calculate_timeout(job_id)
        else:
            timeout = 300  # Fallback
    
    start_time = time.time()
    last_snapshot = None
    
    # Ensure minimum interval to avoid rate limiting (increased to 2.0s)
    interval = max(2.0, interval)
    
    # Progress state preservation
    last_known_progress = 0
    last_known_page = None
    last_known_step = "Processing"
    
    try:
        while True:
            elapsed = time.time() - start_time
            
            # Check timeout
            if elapsed > timeout:
                if show_progress:
                    print(f"\n⏰ Timeout after {timeout}s", flush=True)
                raise SDKTimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
            
            # Get job status
            status_data = client.get_status(job_id)
            
            status = (status_data.get('status') or '').lower()
            progress = int(status_data.get('progress', 0) or 0)
            step = status_data.get('step') or 'Processing'
            
            # Progress details
            progress_details = status_data.get('progress_details') or {}
            current_page = progress_details.get('current_page')
            total_pages = progress_details.get('total_pages') 
            eta = progress_details.get('estimated_time_remaining')
            
            # State preservation - don't let progress go backwards
            if progress > 0:
                last_known_progress = max(last_known_progress, progress)
            else:
                progress = last_known_progress
                
            if current_page:
                last_known_page = current_page
            elif last_known_page:
                current_page = last_known_page
                
            if step and step != "Processing":
                last_known_step = step
            else:
                step = last_known_step
            
            # Show progress if requested
            if show_progress:
                snapshot = (status, progress, current_page, step)
                if snapshot != last_snapshot:
                    line = render_progress_line(
                        progress, step, current_page, total_pages, eta, elapsed
                    )
                    print(f"\r{line}", end="", flush=True)
                    last_snapshot = snapshot
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback({
                    'job_id': job_id,
                    'status': status,
                    'progress': progress,
                    'step': step,
                    'current_page': current_page,
                    'total_pages': total_pages,
                    'eta': eta,
                    'elapsed': elapsed
                })
            
            # Check if job is terminal
            if status in ['completed', 'failed', 'cancelled', 'error']:
                if show_progress:
                    print()  # New line after progress bar
                
                if status == 'completed':
                    return status_data
                else:
                    error_msg = status_data.get('error', f"Job failed with status: {status}")
                    raise ProcessingError(f"Job {job_id} failed: {error_msg}")
            
            # Wait before next poll (adaptive interval with rate limit protection)
            adaptive_interval = interval
            if progress < 10:
                adaptive_interval = max(2.5, interval * 1.5)  # Slower when starting - avoid hitting rate limits
            elif progress > 80:
                adaptive_interval = max(2.0, interval * 0.8)  # Faster when nearly done but still safe
            else:
                adaptive_interval = max(2.0, interval)  # Safe default interval
                
            time.sleep(adaptive_interval)
            
    except KeyboardInterrupt:
        if show_progress:
            print(f"\n⛔ Interrupted by user")
        raise
    except (SDKTimeoutError, ProcessingError):
        raise
    except Exception as e:
        if show_progress:
            print(f"\n❌ Polling error: {e}")
        raise ProcessingError(f"Unexpected error while polling job {job_id}: {e}")


def human_size(n: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TB"


def now_hms() -> str:
    """Get current time in HH:MM:SS format."""
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")
