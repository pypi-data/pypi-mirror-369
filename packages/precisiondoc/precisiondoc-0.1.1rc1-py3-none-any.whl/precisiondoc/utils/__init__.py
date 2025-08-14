"""
Utility modules for PrecisionDoc.

This package contains various utility classes for data processing, 
word document generation, logging, and other operations.
"""

# Import and re-export utility classes
from precisiondoc.utils.word import WordUtils, ExportUtils
from precisiondoc.utils.data_utils import DataUtils
from precisiondoc.utils.log_utils import setup_logger
from precisiondoc.utils.word.image_utils import ImageUtils
from precisiondoc.utils.word.table_utils import TableUtils
from precisiondoc.utils.word.document_formatting import DocumentFormatter
from precisiondoc.utils.word.content_formatting import ContentFormatter
from precisiondoc.utils.word.evidence_processing import EvidenceProcessor

__all__ = [
    'WordUtils',
    'ExportUtils',
    'DataUtils',
    'ImageUtils',
    'TableUtils',
    'DocumentFormatter',
    'ContentFormatter',
    'EvidenceProcessor',
    'setup_logger',
]
