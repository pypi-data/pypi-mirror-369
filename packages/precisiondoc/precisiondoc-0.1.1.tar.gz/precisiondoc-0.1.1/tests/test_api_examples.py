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
        folder_path="/Users/jiaoyk/Downloads/TestData/CSCO_test",
        output_folder="/Users/jiaoyk/Downloads/test_output/result_0812",  # Optional, default is "./output"
        base_url="https://bio-qwen25-vl-api.brbiotech.tech/v1",  # Optional, will use env var BASE_URL if not provided
        api_key="no-key-required",  # Optional, will use env var if not provided
        model="Qwen2.5-VL"  # Optional (Qwen2.5-VL, Qwen3-32B), will use env var TEXT_MODEL if not provided
    )
    return results

def test_excel_to_word_default():
    """Example of converting Excel to Word with default parameters"""
    word_file = excel_to_word(
        excel_file="/Users/jiaoyk/Downloads/test_output/excel/CSCO非小细胞肺癌诊疗指南_results.xlsx",
    )
    return word_file

def test_excel_to_word_custom():
    """Example of converting Excel to Word with custom parameters"""
    word_file = excel_to_word(
        excel_file="/Users/jiaoyk/Downloads/test_output/excel/CSCO非小细胞肺癌诊疗指南_results.xlsx",
        word_file="/Users/jiaoyk/Downloads/test_output/word/CSCO非小细胞肺癌诊疗指南_results.docx",
        multi_line_text=False,  # use multi line text
        show_borders=True      # show table borders
    )
    return word_file

def test_process_single_pdf():
    """Example of processing a single PDF file"""
    results = process_single_pdf(
        pdf_path="/Users/jiaoyk/Downloads/TestData/CSCO_test/CSCO非小细胞肺癌诊疗指南2024_20240813110010.pdf",
        doc_type="CSCO非小细胞肺癌诊疗指南",  # Optional, will use filename if not provided
        output_folder="/Users/jiaoyk/Downloads/test_output/single_pdf_result",  # Optional, default is "./output"
        base_url="https://bio-qwen25-vl-api.brbiotech.tech/v1",  # Optional, will use env var BASE_URL if not provided
        api_key="no-key-required",  # Optional, will use env var if not provided
        model="Qwen2.5-VL"  # Optional, will use env var TEXT_MODEL if not provided
    )
    return results

if __name__ == "__main__":
    # Uncomment the test function you want to run
    # test_process_pdf()
    test_process_single_pdf()
    # test_excel_to_word_default()
    # test_excel_to_word_custom()
