"""
Word document processing utilities.
This module is deprecated and will be removed in a future version.
Please use precisiondoc.utils.word.WordUtils instead.
"""
import warnings
from precisiondoc.utils.word.document_formatting import DocumentFormatter
from precisiondoc.utils.word.table_utils import TableUtils
from precisiondoc.utils.word.content_formatting import ContentFormatter
from precisiondoc.utils.word.evidence_processing import EvidenceProcessor
from precisiondoc.utils.word.image_utils import ImageUtils
from precisiondoc.utils.word.export_utils import ExportUtils
from precisiondoc.utils.word import WordUtils

# Issue deprecation warning
warnings.warn(
    "The WordUtils class in word_utils.py is deprecated. "
    "Please use precisiondoc.utils.word.WordUtils instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, re-export WordUtils class
__all__ = ['WordUtils']
