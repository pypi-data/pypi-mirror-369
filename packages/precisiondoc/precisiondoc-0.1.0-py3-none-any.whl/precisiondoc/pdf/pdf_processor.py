import os
import json
import re
import pandas as pd
from typing import Dict, List
from dotenv import load_dotenv
from datetime import datetime

# Import utility modules
from precisiondoc.pdf.pdf_utils import find_latest_pdfs, split_pdf, extract_text_from_pdf, convert_pdf_to_image
from precisiondoc.ai.ai_client import AIClient
from precisiondoc.utils.word_utils import WordUtils
from precisiondoc.utils.data_utils import DataUtils
from precisiondoc.utils.log_utils import setup_logger

# Setup logger for this module
logger = setup_logger(__name__)

class PDFProcessor:
    """Main class for processing PDF documents"""
    
    def __init__(self, folder_path: str, api_key: str = None, output_folder: str = "./output", base_url: str = None, model: str = None):
        """
        Initialize the PDF processor.
        
        Args:
            folder_path: Path to the folder containing PDF files
            api_key: API key for OpenAI. If None, will try to load from environment variables.
            output_folder: Path to the output folder for results. Default is "./output"
            base_url: Base URL for API. If None, will try to load from environment variables.
            model: Model to use for API calls. If None, will try to load from environment variables.
        """
        self.folder_path = folder_path
        
        # Set output directories
        self.output_folder = output_folder
        self.pages_folder = os.path.join(self.output_folder, "pages")
        self.images_folder = os.path.join(self.output_folder, "images")
        
        # Add dedicated folders for different output file types
        self.json_folder = os.path.join(self.output_folder, "json")
        self.excel_folder = os.path.join(self.output_folder, "excel")
        self.word_folder = os.path.join(self.output_folder, "word")
        
        # Create output directories if they don't exist
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.pages_folder, exist_ok=True)
        os.makedirs(self.images_folder, exist_ok=True)
        os.makedirs(self.json_folder, exist_ok=True)
        os.makedirs(self.excel_folder, exist_ok=True)
        os.makedirs(self.word_folder, exist_ok=True)
        
        # Initialize AI client
        self.ai_client = AIClient(api_key=api_key, base_url=base_url, model=model)
    
    def process_page_with_ai(self, page_path: str) -> Dict:
        """
        Process a single PDF page with AI.
        Skip processing for table of contents or reference pages.
        
        Args:
            page_path: Path to the PDF page
            
        Returns:
            Dictionary containing the AI's response or a skip message
        """
        # Extract text from PDF page
        page_text = extract_text_from_pdf(page_path)
        
        # Convert PDF to image
        image_path = convert_pdf_to_image(page_path, self.images_folder)
        logger.info(f"Converted PDF to image: {image_path}")
        
        # Use AI to identify page type
        page_type_result = self.ai_client.identify_page_type(page_text)
        page_type = page_type_result.get("page_type", "content")
        
        logger.info(f"Identified page type: {page_type} for {os.path.basename(page_path)}")
        # Skip processing for non-content pages
        if page_type != "content":
            return {
                "success": True,
                "content": f"This page appears to be a {page_type} page and was skipped for detailed AI processing.",
                "page_type": page_type
            }
        
        # Process content with AI
        logger.info(f"Processing page with AI: {os.path.basename(page_path)}")
        
        # Check if the AI client has a process_image method
        if hasattr(self.ai_client, 'process_image'):
            # Check if image exists
            if image_path and os.path.exists(image_path):
                # Use image-based processing with PNG
                logger.info(f"Using image-based processing with PNG: {image_path}")
                result = self.ai_client.process_image(image_path)
            elif hasattr(self.ai_client, 'process_pdf') and os.path.exists(page_path):
                # Fallback to using PDF directly if PNG doesn't exist
                logger.info(f"PNG not found. Using PDF directly: {page_path}")
                result = self.ai_client.process_pdf(page_path)
            else:
                # Fallback to text-based processing if neither option works
                logger.info(f"Using text-based processing as fallback")
                result = self.ai_client.process_text(page_text)
        else:
            # Use text-based processing if image processing is not available
            logger.info(f"Using text-based processing (image processing not available)")
            result = self.ai_client.process_text(page_text)
        
        # Add page type to result
        if "page_type" not in result:
            result["page_type"] = page_type
            
        # Add image path to result for later use
        if image_path:
            result["image_path"] = image_path
            
        return result
    
    def _initialize_output_files(self, doc_type: str) -> tuple:
        """
        Initialize output files for a document.
        
        Args:
            doc_type: Document type/name
            
        Returns:
            Tuple of (json_file, excel_file, word_file) paths
        """
        # Normalize PDF name for file naming
        normalized_pdf_name = re.sub(r'[^\w\-\.]', '_', doc_type)
        
        # Initialize output files at the beginning to avoid redundant data
        json_file = os.path.join(self.json_folder, f"{normalized_pdf_name}_results.json")
        excel_file = os.path.join(self.excel_folder, f"{normalized_pdf_name}_results.xlsx")
        word_file = os.path.join(self.word_folder, f"{normalized_pdf_name}_results.docx")
        
        # Create empty files to clear any previous content
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
            
        # Initialize Excel file with empty content
        if os.path.exists(excel_file):
            try:
                # Create an empty DataFrame and save it to clear the Excel file
                empty_df = pd.DataFrame()
                empty_df.to_excel(excel_file, index=False)
                logger.info(f"Initialized Excel file: {excel_file}")
            except Exception as e:
                logger.warning(f"Could not initialize Excel file {excel_file}: {str(e)}")
        
        # Initialize Word file with empty content if it exists
        if os.path.exists(word_file):
            try:
                # Import here to avoid circular imports
                from docx import Document
                # Create an empty document and save it to clear the Word file
                doc = Document()
                doc.save(word_file)
                logger.info(f"Initialized Word file: {word_file}")
            except Exception as e:
                logger.warning(f"Could not initialize Word file {word_file}: {str(e)}")
                
        logger.info(f"Initialized output files for {doc_type}")
        return json_file, excel_file, word_file
    
    def _process_pdf_pages(self, doc_type: str, pdf_path: str, json_file: str) -> List[Dict]:
        """
        Process all pages of a PDF.
        
        Args:
            doc_type: Document type/name
            pdf_path: Path to the PDF file
            json_file: Path to the JSON output file for saving intermediate results
            
        Returns:
            List of page results
        """
        # Split PDF into pages
        page_paths = split_pdf(pdf_path, self.pages_folder)
        
        # Process each page with AI
        page_results = []
        for i, page_path in enumerate(page_paths):
            logger.info(f"Processing page {i+1}/{len(page_paths)} of {doc_type}")
            try:
                result = self.process_page_with_ai(page_path)
                
                # Add page number information to result
                result["page_number"] = i + 1
                result["total_pages"] = len(page_paths)
                # Add raw pdf file name
                result["raw_pdf_name"] = os.path.basename(pdf_path)
                
                page_results.append(result)
                
                # Save intermediate results after each page (optional, may be too frequent)
                if (i+1) % 5 == 0:  # Save every 5 pages
                    # Save intermediate results to the initialized files
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(page_results, f, ensure_ascii=False, indent=2)
                    logger.info(f"Saved intermediate results for {doc_type} to {json_file}")
            except Exception as e:
                logger.error(f"Error processing page {i+1} of {doc_type}: {str(e)}")
                # Continue with next page despite errors
        
        return page_results
    
    def _save_final_results(self, doc_type: str, page_results: List[Dict], 
                           json_file: str, excel_file: str, word_file: str) -> None:
        """
        Save final results to JSON, Excel, and Word files.
        
        Args:
            doc_type: Document type/name
            page_results: List of page results
            json_file: Path to the JSON output file
            excel_file: Path to the Excel output file
            word_file: Path to the Word output file
        """
        # Save final results to JSON file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(page_results, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved final JSON results for {doc_type} to {json_file}")
        
        # Convert to Excel and Word
        pdf_results = {doc_type: page_results}
        
        # Convert nested results to flat structure for Excel
        all_rows = DataUtils.convert_to_flat_structure(pdf_results)
        
        # Save to Excel
        DataUtils.save_to_excel(all_rows, excel_file)
        logger.info(f"Saved Excel results for {doc_type} to {excel_file}")
        
        # Export to Word
        WordUtils.export_evidence_to_word(excel_file, word_file, self.output_folder, multi_line_text=True)
        logger.info(f"Saved Word results for {doc_type} to {word_file}")
        
        # Save consolidated results after each document is processed
        self.save_consolidated_results({doc_type: page_results})

    def process_all(self) -> Dict[str, List[Dict]]:
        """
        Process all PDFs in the folder.
        
        Returns:
            Dictionary mapping document type to list of page results
        """
        # Find latest PDFs
        latest_pdfs = find_latest_pdfs(self.folder_path)
        
        if not latest_pdfs:
            logger.warning(f"No PDF files found in {self.folder_path}")
            return {}
        
        results = {}

        # Process each PDF
        for doc_type, pdf_path in latest_pdfs.items():
            logger.info(f"Processing {doc_type}: {os.path.basename(pdf_path)}")
            
            # Initialize output files
            json_file, excel_file, word_file = self._initialize_output_files(doc_type)
            
            # Process PDF pages
            page_results = self._process_pdf_pages(doc_type, pdf_path, json_file)
            
            # Store results
            results[doc_type] = page_results
            
            # Save final results
            self._save_final_results(doc_type, page_results, json_file, excel_file, word_file)
        
        return results
    
    def save_consolidated_results(self, results: Dict[str, List[Dict]]) -> str:
        """
        Save consolidated results to a JSON file and an Excel file.
        
        Args:
            results: Dictionary mapping document type to list of page results
        
        Returns:
            Path to the output file
        """
        # This method is now simplified as most file operations are handled in process_all
        # It's kept for backward compatibility and potential future consolidated output
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        consolidated_file = os.path.join(self.output_folder, f"consolidated_results_{timestamp}.json")
        
        # Save consolidated JSON results
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved consolidated results to {consolidated_file}")
        return consolidated_file
