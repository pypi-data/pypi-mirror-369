#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main program entry file for PrecisionDoc package
"""

import os
import argparse
from dotenv import load_dotenv

# Import logging utility
from precisiondoc.utils.log_utils import setup_logger

# Import core functionality
from precisiondoc import process_pdf, excel_to_word

# Setup logger for this module
logger = setup_logger(__name__)


def main():
    """Main program entry point"""
    parser = argparse.ArgumentParser(description="PrecisionDoc - Document processing and evidence extraction")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # PDF processing command
    pdf_parser = subparsers.add_parser("process-pdf", help="Process PDF files with AI")
    pdf_parser.add_argument("--folder", required=True, help="Folder containing PDF files")
    pdf_parser.add_argument("--api-key", help="API key for AI service")
    pdf_parser.add_argument("--base-url", help="Base URL for API endpoint")
    pdf_parser.add_argument("--model", help="Model name to use for API calls")
    pdf_parser.add_argument("--output-folder", default="./output", help="Output folder for results")
    
    # Excel to Word command
    excel_parser = subparsers.add_parser("excel-to-word", help="Convert Excel evidence file to Word document")
    excel_parser.add_argument("--excel-file", required=True, help="Path to Excel file")
    excel_parser.add_argument("--word-file", help="Output Word file path (optional)")
    excel_parser.add_argument("--multi-line", action="store_true", help="Use multi-line text format")
    excel_parser.add_argument("--show-borders", action="store_true", help="Show table borders")
    excel_parser.add_argument("--exclude-columns", help="Comma-separated list of columns to exclude")
    
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    if args.command == "process-pdf":
        results = process_pdf(
            folder_path=args.folder,
            api_key=args.api_key,
            output_folder=args.output_folder,
            base_url=args.base_url,
            model=args.model
        )
        logger.info(f"PDF processing complete. Results saved to {args.output_folder}")
        
    elif args.command == "excel-to-word":
        exclude_columns = args.exclude_columns.split(",") if args.exclude_columns else None
        excel_to_word(
            excel_file=args.excel_file,
            word_file=args.word_file,
            multi_line_text=args.multi_line,
            show_borders=args.show_borders,
            exclude_columns=exclude_columns
        )
        logger.info(f"Excel to Word conversion complete")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
