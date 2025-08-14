#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test file for PrecisionDoc PDF processing functionality
"""

import os
import pytest
from dotenv import load_dotenv

# Import logging utility
from precisiondoc.utils.log_utils import setup_logger

# Import core functionality
from precisiondoc import process_single_pdf

# Setup logger for this module
logger = setup_logger(__name__)

# Load environment variables from .env file
load_dotenv()

def test_process_single_pdf_basic():
    """
    Test basic functionality of process_single_pdf function
    
    This test verifies that the process_single_pdf function returns
    a non-empty result when processing a PDF file.
    """
    # Skip test if API_KEY is not available
    if not os.environ.get("API_KEY"):
        pytest.skip("API_KEY environment variable not set")
    
    # Process a test PDF file
    results = process_single_pdf(
        pdf_path="tests/test_files/test_single_page.pdf",
        doc_type="test_single_page",
        output_folder="tests/test_output",
        base_url=os.environ.get("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        api_key=os.environ.get("API_KEY"),
        model=os.environ.get("TEXT_MODEL", "qwen-vl-max")
    )
    
    # Basic assertion to verify that results are returned
    assert results is not None, "process_single_pdf should return results"
    assert isinstance(results, dict), "Results should be a dictionary"
    
    # Log success
    logger.info("Successfully processed PDF file")
    
    return results
