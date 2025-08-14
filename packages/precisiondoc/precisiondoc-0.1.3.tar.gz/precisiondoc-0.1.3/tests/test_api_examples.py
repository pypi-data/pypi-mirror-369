#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PrecisionDoc API usage examples and tests
"""

import os
from dotenv import load_dotenv

# Import logging utility
from precisiondoc.utils.log_utils import setup_logger

# Import core functionality
from precisiondoc import excel_to_word, process_pdf, process_single_pdf

# Setup logger for this module
logger = setup_logger(__name__)

# Load environment variables from .env file
load_dotenv()

def test_process_pdf():
    """Example of processing PDF files"""
    results = process_pdf(
        folder_path="tests/test_files",
        output_folder="tests/test_output",  # Optional, default is "./output"
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # Optional, will use env var BASE_URL if not provided
        api_key=os.environ.get("API_KEY"),  # Use environment variable instead of hardcoded key
        model="qwen-vl-max"  # Optional (Qwen2.5-VL, Qwen3-32B), will use env var TEXT_MODEL if not provided
    )
    return results

def test_excel_to_word_default():
    """Example of converting Excel to Word with default parameters"""
    word_file = excel_to_word(
        excel_file="tests/test_files/lung_screening_Version_1.2025.xlsx",
    )
    return word_file

def test_excel_to_word_custom():
    """Example of converting Excel to Word with custom parameters"""
    word_file = excel_to_word(
        excel_file="tests/test_files/lung_screening_Version_1.2025.pdf",
        word_file="tests/test_output/lung_screening_Version_1.2025.docx",
        multi_line_text=False,  # use multi line text
        show_borders=True      # show table borders
    )
    return word_file

def test_process_single_pdf():
    """Example of processing a single PDF file"""
    results = process_single_pdf(
        pdf_path="tests/test_files/lung_screening_Version_1.2025.pdf",
        doc_type="lung_screening_Version_1.2025",  # Optional, will use filename if not provided
        output_folder="tests/test_output",  # Optional, default is "./output"
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # Optional, will use env var BASE_URL if not provided
        api_key=os.environ.get("API_KEY"),  # Use environment variable instead of hardcoded key
        model="qwen-vl-max"  # Optional, will use env var TEXT_MODEL if not provided
    )
    return results

if __name__ == "__main__":
    # Uncomment the test function you want to run
    # test_process_pdf()
    test_process_single_pdf()
    # test_excel_to_word_default()
    # test_excel_to_word_custom()
