"""
PrecisionDoc - Document processing and evidence extraction package

This package provides tools for processing PDF documents, extracting evidence,
and generating structured outputs in various formats (JSON, Excel, Word).

Main Features:
-------------
1. PDF Processing: Split PDFs into pages, convert to images, and process with AI
2. Evidence Extraction: Extract structured evidence from document images
3. Export Utilities: Export evidence to JSON, Excel, and Word formats
4. Word Document Generation: Create formatted Word documents with evidence tables

Usage Examples:
--------------
Process a PDF folder:
    >>> from precisiondoc import process_pdf
    >>> results = process_pdf(
    ...     folder_path="path/to/pdfs",
    ...     output_folder="./output",
    ...     api_key="your-api-key",  # Optional, will use env var if not provided
    ...     base_url="https://api.example.com/v1",  # Optional
    ...     model="gpt-4"  # Optional
    ... )

Convert Excel evidence to Word:
    >>> from precisiondoc import excel_to_word
    >>> word_file = excel_to_word(
    ...     excel_file="path/to/evidence.xlsx",
    ...     word_file="path/to/output.docx",  # Optional
    ...     multi_line_text=True,  # Optional
    ...     show_borders=True  # Optional
    ... )
"""

__version__ = '0.1.0'

# Import core components for API exposure
from .pdf.pdf_processor import PDFProcessor
from .utils.word import WordUtils, ExportUtils
from .utils.data_utils import DataUtils
from .utils.word.image_utils import ImageUtils

# Convenience functions for common operations
def process_pdf(folder_path, api_key=None, output_folder="./output", base_url=None, model=None):
    """
    Process PDF files in a folder and generate evidence extraction results.
    
    Args:
        folder_path (str): Path to folder containing PDF files
        api_key (str, optional): API key for AI service. If None, will try to load from environment variable API_KEY.
        output_folder (str, optional): Output folder for results. Defaults to "./output".
        base_url (str, optional): Base URL for API. If None, will try to load from environment variable BASE_URL.
        model (str, optional): Model to use for API calls. If None, will try to load from environment variable TEXT_MODEL.
        
    Returns:
        dict: Dictionary with processing results
    """
    processor = PDFProcessor(
        folder_path=folder_path,
        api_key=api_key,
        output_folder=output_folder,
        base_url=base_url,
        model=model
    )
    results = processor.process_all()
    processor.save_consolidated_results(results)
    return results

def excel_to_word(excel_file, word_file=None, output_folder=None, 
                 multi_line_text=True, show_borders=True, exclude_columns=None):
    """
    Convert Excel file with evidence data to formatted Word document
    
    Args:
        excel_file (str or DataFrame): Path to Excel file or pandas DataFrame
        word_file (str, optional): Path to output Word file (if None, will be generated from excel_file)
        output_folder (str, optional): Output folder path, used to find images
        multi_line_text (bool, optional): If True, split text by newlines in the left cell. Defaults to True.
        show_borders (bool, optional): If True, show table borders. Defaults to True.
        exclude_columns (list, optional): Columns to exclude from evidence text
        
    Returns:
        str: Path to the generated Word file
    """
    return WordUtils.export_evidence_to_word(
        excel_file=excel_file,
        word_file=word_file,
        output_folder=output_folder,
        multi_line_text=multi_line_text,
        show_borders=show_borders,
        exclude_columns=exclude_columns
    )

# Export main classes and functions
__all__ = [
    'PDFProcessor',
    'WordUtils',
    'ExportUtils',
    'DataUtils',
    'ImageUtils',
    'process_pdf',
    'excel_to_word',
]
