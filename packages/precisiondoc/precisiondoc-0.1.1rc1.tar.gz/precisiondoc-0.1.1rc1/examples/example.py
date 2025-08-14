#!/usr/bin/env python3
import os
import argparse
import shutil
from dotenv import load_dotenv

# Import from PrecisionDoc package using absolute imports
from precisiondoc import process_pdf, excel_to_word
from precisiondoc.pdf.pdf_processor import PDFProcessor
from precisiondoc.ai.ai_client import AIClient
from precisiondoc.ai.qwen_api import QwenClient

def create_sample_env_if_missing():
    """Create .env file from .env.example if .env doesn't exist"""
    if not os.path.exists('.env') and os.path.exists('.env.example'):
        print("No .env file found. Creating from .env.example...")
        shutil.copy('.env.example', '.env')
        print("Created .env file. Please edit it with your API keys.")
        return True
    return False

def validate_api_keys(use_qwen):
    """Validate that API keys are set and not using placeholder values"""
    if use_qwen:
        key_name = "API_KEY"  # Both APIs use the same env var name now
        api_key = os.getenv(key_name)
        placeholder = "your_api_key_here"
    else:
        key_name = "API_KEY"
        api_key = os.getenv(key_name)
        placeholder = "your_api_key_here"
    
    if not api_key:
        print(f"Error: {key_name} environment variable is not set.")
        print(f"Please set it in your .env file or export it in your shell.")
        return False
    
    if api_key == placeholder:
        print(f"Error: {key_name} is still set to the placeholder value.")
        print(f"Please update it with your actual API key in the .env file.")
        return False
    
    return True

def create_sample_folder_if_missing(folder_path):
    """Create sample folder if it doesn't exist"""
    if not os.path.exists(folder_path):
        print(f"Creating sample folder: {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        print(f"Sample folder created. Please add PDF files to {folder_path}")
        return True
    return False

def main():
    """Main entry point for the example script"""
    parser = argparse.ArgumentParser(description="Example script for PDF processing")
    parser.add_argument("--folder", default="./pdf_files", help="Folder containing PDF files")
    parser.add_argument("--api-key", help="API key for OpenAI or Qwen")
    parser.add_argument("--use-qwen", action="store_true", help="Use Qwen API instead of OpenAI")
    parser.add_argument("--env-file", default=".env", help="Path to .env file")
    parser.add_argument("--output-folder", default="./output", help="Output folder for results")
    parser.add_argument("--model", help="Model to use for API calls")
    parser.add_argument("--base-url", help="Base URL for API calls")
    parser.add_argument("--excel-to-word", action="store_true", help="Convert Excel evidence to Word")
    parser.add_argument("--excel-file", help="Excel file to convert to Word (required if --excel-to-word is used)")
    parser.add_argument("--word-file", help="Output Word file path (optional)")
    parser.add_argument("--multi-line-text", action="store_true", default=True, 
                        help="Use multi-line text format in Word export (default: True)")
    parser.add_argument("--show-borders", action="store_true", default=True,
                        help="Show borders in Word export tables (default: True)")
    parser.add_argument("--exclude-columns", help="Comma-separated list of columns to exclude from Word export")
    
    args = parser.parse_args()
    
    # Load environment variables from specified .env file
    if os.path.exists(args.env_file):
        load_dotenv(args.env_file)
        print(f"Loaded environment variables from {args.env_file}")
    else:
        # Try to create .env from .env.example if it doesn't exist
        if args.env_file == ".env":
            created = create_sample_env_if_missing()
            if created:
                load_dotenv()
            else:
                print(f"Warning: {args.env_file} not found and couldn't create from .env.example")
    
    # Handle Excel to Word conversion if requested
    if args.excel_to_word:
        if not args.excel_file:
            print("Error: --excel-file is required when using --excel-to-word")
            return
        
        print(f"Converting Excel file to Word: {args.excel_file}")
        try:
            # Parse exclude_columns if provided
            exclude_cols = None
            if args.exclude_columns:
                exclude_cols = [col.strip() for col in args.exclude_columns.split(',')]
            
            word_file = excel_to_word(
                excel_file=args.excel_file,
                word_file=args.word_file,
                output_folder=args.output_folder,
                multi_line_text=args.multi_line_text,
                show_borders=args.show_borders,
                exclude_columns=exclude_cols
            )
            print(f"Word file created: {word_file}")
            return
        except Exception as e:
            print(f"Error converting Excel to Word: {str(e)}")
            return
    
    # Create sample folder if it doesn't exist
    create_sample_folder_if_missing(args.folder)
    
    # Validate API keys
    if not args.api_key and not validate_api_keys(args.use_qwen):
        print("Please set the API key and try again.")
        return
    
    # Process PDFs
    print(f"Processing PDFs in folder: {args.folder}")
    print(f"Using {'Qwen' if args.use_qwen else 'OpenAI'} API")
    
    try:
        # Use the PDFProcessor class directly to demonstrate its features
        processor = PDFProcessor(
            folder_path=args.folder,
            api_key=args.api_key,
            output_folder=args.output_folder,
            base_url=args.base_url,
            model=args.model
        )
        
        # Process all PDFs with 1:1 mapping between original PDFs and output files
        results = processor.process_all()
        
        # Print summary
        print("\nProcessing Summary:")
        for doc_type, page_results in results.items():
            success_count = sum(1 for result in page_results if result.get("success", False))
            print(f"- {doc_type}: Processed {len(page_results)} pages, {success_count} successful")
            
            # Show page metadata example from the first successful page
            for result in page_results:
                if result.get("success", False):
                    print(f"  - Page metadata example: Page {result.get('page_number')}/{result.get('total_pages')} from {result.get('raw_pdf_name')}")
                    break
    
    except Exception as e:
        print(f"Error processing PDFs: {str(e)}")
        return

if __name__ == "__main__":
    main()
