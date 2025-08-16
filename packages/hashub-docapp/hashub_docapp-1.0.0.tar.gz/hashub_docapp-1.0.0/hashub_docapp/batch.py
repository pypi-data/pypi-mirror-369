"""
Batch Processing Helper for Hashub DocApp SDK

Provides intelligent file discovery, categorization, and batch processing capabilities.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional, Union
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class FileCategory:
    """File category with supported extensions and processing mode."""
    name: str
    extensions: Set[str]
    processing_mode: str
    description: str

@dataclass
class BatchAnalysis:
    """Analysis result of a directory for batch processing."""
    total_files: int
    valid_files: List[Path]
    invalid_files: List[Path]
    categories: Dict[str, List[Path]]
    size_mb: float
    recommendations: List[str]

class BatchHelper:
    """
    Helper class for intelligent batch file processing.
    
    Categorizes files, provides recommendations, and manages batch operations.
    """
    
    # File categories with their supported extensions and optimal processing modes
    CATEGORIES = {
        'image_pdf': FileCategory(
            name='Images & PDFs',
            extensions={'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp'},
            processing_mode='ocr',
            description='Scanned documents and images requiring OCR'
        ),
        'office_docs': FileCategory(
            name='Office Documents',
            extensions={'.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp'},
            processing_mode='extract',
            description='Office documents with embedded text'
        ),
        'web_formats': FileCategory(
            name='Web Formats',
            extensions={'.html', '.htm', '.xml', '.mhtml'},
            processing_mode='parse',
            description='Web and markup documents'
        ),
        'text_formats': FileCategory(
            name='Text Files',
            extensions={'.txt', '.rtf', '.csv', '.tsv'},
            processing_mode='simple',
            description='Plain text and structured text files'
        )
    }
    
    # Extensions that require OCR processing (images and PDFs)
    OCR_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp'}
    
    # All supported extensions
    ALL_EXTENSIONS = set()
    for category in CATEGORIES.values():
        ALL_EXTENSIONS.update(category.extensions)
    
    @classmethod
    def discover_files(
        cls, 
        directory: Union[str, Path], 
        recursive: bool = True,
        include_hidden: bool = False
    ) -> List[Path]:
        """
        Discover all files in a directory.
        
        Args:
            directory: Directory path to scan
            recursive: Include subdirectories
            include_hidden: Include hidden files (starting with .)
            
        Returns:
            List of discovered file paths
        """
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        files = []
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                # Skip hidden files if not requested
                if not include_hidden and file_path.name.startswith('.'):
                    continue
                files.append(file_path)
        
        return sorted(files)
    
    @classmethod
    def categorize_files(cls, files: List[Path]) -> Tuple[Dict[str, List[Path]], List[Path]]:
        """
        Categorize files based on their extensions.
        
        Args:
            files: List of file paths
            
        Returns:
            Tuple of (categorized_files, invalid_files)
        """
        categorized = defaultdict(list)
        invalid = []
        
        for file_path in files:
            extension = file_path.suffix.lower()
            
            # Find matching category
            category_found = False
            for category_name, category in cls.CATEGORIES.items():
                if extension in category.extensions:
                    categorized[category_name].append(file_path)
                    category_found = True
                    break
            
            if not category_found:
                invalid.append(file_path)
        
        return dict(categorized), invalid
    
    @classmethod
    def calculate_total_size(cls, files: List[Path]) -> float:
        """Calculate total size of files in MB."""
        total_bytes = sum(f.stat().st_size for f in files if f.exists())
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    @classmethod
    def analyze_directory(
        cls, 
        directory: Union[str, Path], 
        recursive: bool = True,
        include_hidden: bool = False
    ) -> BatchAnalysis:
        """
        Analyze a directory for batch processing.
        
        Args:
            directory: Directory to analyze
            recursive: Include subdirectories
            include_hidden: Include hidden files
            
        Returns:
            BatchAnalysis with categorized files and recommendations
        """
        # Discover files
        all_files = cls.discover_files(directory, recursive, include_hidden)
        
        # Categorize files
        categories, invalid_files = cls.categorize_files(all_files)
        
        # Get valid files
        valid_files = []
        for file_list in categories.values():
            valid_files.extend(file_list)
        
        # Calculate size
        size_mb = cls.calculate_total_size(valid_files)
        
        # Generate recommendations
        recommendations = cls._generate_recommendations(categories, invalid_files, size_mb)
        
        return BatchAnalysis(
            total_files=len(all_files),
            valid_files=valid_files,
            invalid_files=invalid_files,
            categories=categories,
            size_mb=size_mb,
            recommendations=recommendations
        )
    
    @classmethod
    def _generate_recommendations(
        cls, 
        categories: Dict[str, List[Path]], 
        invalid_files: List[Path],
        size_mb: float
    ) -> List[str]:
        """Generate processing recommendations based on analysis."""
        recommendations = []
        
        # File count recommendations
        total_valid = sum(len(files) for files in categories.values())
        
        if total_valid == 0:
            recommendations.append("❌ No supported files found")
            return recommendations
        
        # Processing method recommendations
        image_pdf_count = len(categories.get('image_pdf', []))
        office_count = len(categories.get('office_docs', []))
        web_count = len(categories.get('web_formats', []))
        
        if image_pdf_count > 0 and office_count == 0 and web_count == 0:
            recommendations.append(f"🚀 Use batch_convert_fast() - {image_pdf_count} OCR files only")
        elif image_pdf_count > 0 and (office_count > 0 or web_count > 0):
            recommendations.append(f"🎯 Use batch_convert_auto() - Mixed file types detected")
        elif image_pdf_count == 0:
            recommendations.append(f"📄 Use batch_convert_auto() - No OCR files, {office_count + web_count} text files")
        
        # Size recommendations
        if size_mb > 100:
            recommendations.append(f"⚠️  Large batch: {size_mb:.1f}MB - Consider processing in smaller chunks")
        elif size_mb > 500:
            recommendations.append(f"🔥 Very large batch: {size_mb:.1f}MB - Strongly recommend splitting")
        
        # Performance recommendations
        if total_valid > 50:
            recommendations.append(f"⏱️  {total_valid} files detected - Use show_progress=True to monitor")
        
        if len(invalid_files) > 0:
            recommendations.append(f"🗑️  {len(invalid_files)} unsupported files will be skipped")
        
        return recommendations
    
    @classmethod
    def filter_for_mode(cls, files: List[Path], mode: str) -> List[Path]:
        """
        Filter files based on processing mode.
        
        Args:
            files: List of file paths
            mode: 'fast' (OCR only), 'smart' (OCR only), 'auto' (all supported)
            
        Returns:
            Filtered list of files
        """
        if mode in ['fast', 'smart']:
            # Only OCR-capable files
            return [f for f in files if f.suffix.lower() in cls.OCR_EXTENSIONS]
        elif mode == 'auto':
            # All supported files
            return [f for f in files if f.suffix.lower() in cls.ALL_EXTENSIONS]
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    @classmethod
    def print_analysis(cls, analysis: BatchAnalysis, show_details: bool = True):
        """
        Print a formatted analysis report.
        
        Args:
            analysis: BatchAnalysis result
            show_details: Show detailed file breakdown
        """
        print(f"\n{'='*70}")
        print(f"📁 Batch Processing Analysis")
        print(f"{'='*70}")
        
        # Summary
        print(f"📊 Summary:")
        print(f"   Total files found: {analysis.total_files}")
        print(f"   Supported files: {len(analysis.valid_files)}")
        print(f"   Unsupported files: {len(analysis.invalid_files)}")
        print(f"   Total size: {analysis.size_mb:.1f} MB")
        
        # Categories breakdown
        if show_details and analysis.categories:
            print(f"\n📂 File Categories:")
            for category_name, files in analysis.categories.items():
                if files:
                    category = cls.CATEGORIES[category_name]
                    print(f"   {category.description}: {len(files)} files")
                    if len(files) <= 5:
                        for file in files:
                            print(f"      • {file.name}")
                    else:
                        for file in files[:3]:
                            print(f"      • {file.name}")
                        print(f"      ... and {len(files) - 3} more")
        
        # Recommendations
        if analysis.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in analysis.recommendations:
                print(f"   {rec}")
        
        print(f"{'='*70}\n")
    
    @classmethod
    def generate_output_filename(
        cls, 
        input_path: Path, 
        output_dir: Path, 
        output_format: str = "txt",
        add_timestamp: bool = False
    ) -> Path:
        """
        Generate output filename for processed file.
        
        Args:
            input_path: Original file path
            output_dir: Output directory
            output_format: Output format extension
            add_timestamp: Add timestamp to filename
            
        Returns:
            Generated output file path
        """
        base_name = input_path.stem
        
        if add_timestamp:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{base_name}_{timestamp}"
        
        output_filename = f"{base_name}.{output_format}"
        return output_dir / output_filename


def quick_analyze(directory: str, show_details: bool = True) -> BatchAnalysis:
    """
    Quick analysis function for directory scanning.
    
    Args:
        directory: Directory path to analyze
        show_details: Print detailed analysis
        
    Returns:
        BatchAnalysis result
    """
    analysis = BatchHelper.analyze_directory(directory)
    
    if show_details:
        BatchHelper.print_analysis(analysis)
    
    return analysis
