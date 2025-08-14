"""
Evidence processing utilities for Word documents.
"""
import json
import pandas as pd
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from precisiondoc.utils.word.content_formatting import ContentFormatter

class EvidenceProcessor:
    """Handles evidence data processing operations"""
    
    @staticmethod
    def _prepare_evidence_text(row, exclude_columns):
        """
        Prepare evidence text from row data
        
        Args:
            row: DataFrame row
            exclude_columns: Columns to exclude from text
            
        Returns:
            dict: Dictionary containing evidence fields
        """
        evidence_dict = {}
        for col in row.index:
            if col not in exclude_columns:
                # Check if value is empty, if so display "N/A"
                if pd.isna(value := row[col]):
                    evidence_dict[col] = "N/A"
                else:
                    # Process based on value type
                    if isinstance(value, (dict, list, tuple, set)):
                        # Format complex data types using json.dumps
                        evidence_dict[col] = json.dumps(value, indent=4, ensure_ascii=False)
                    elif isinstance(value, str):
                        # Use string values directly
                        evidence_dict[col] = value
                    else:
                        # Convert other types to string
                        evidence_dict[col] = str(value)
        return evidence_dict
    
    @staticmethod
    def _rename_evidence_dict_keys(evidence_dict):
        """
        Rename keys in evidence dictionary
        
        Args:
            evidence_dict: Dictionary containing evidence data
            
        Returns:
            dict: Dictionary with renamed keys
        """
        key_mapping = {
            'text': 'resource_sentence',
            'image_path': 'resource_url'
        }
        
        renamed_dict = {}
        for key, value in evidence_dict.items():
            new_key = key_mapping.get(key, key)  # Use mapped key if exists, otherwise keep original
            renamed_dict[new_key] = value
            
        return renamed_dict
    
    @staticmethod
    def _sort_evidence_dict(evidence_dict):
        """
        Sort evidence dictionary based on predefined key sequence
        
        Args:
            evidence_dict: Dictionary containing evidence data
            
        Returns:
            dict: Sorted dictionary
        """
        # Define the desired key order
        key_order = [
            'symbol', 
            'alteration', 
            'disease_name_cn', 
            'disease_name_en', 
            'drug_name_cn', 
            'drug_name_en', 
            'drug_combination', 
            'response_type', 
            'resource', 
            'resource_url', 
            'resource_sentence'
        ]
        
        # Create a new ordered dictionary
        sorted_dict = {}
        
        # First add keys in the specified order
        for key in key_order:
            if key in evidence_dict:
                sorted_dict[key] = evidence_dict[key]
        
        # Then add any remaining keys that weren't in our predefined order
        for key, value in evidence_dict.items():
            if key not in sorted_dict:
                sorted_dict[key] = value
                
        return sorted_dict
    
    @staticmethod
    def _format_json_dict(evidence_dict):
        """
        Format evidence dictionary as a JSON-style string
        
        Args:
            evidence_dict: Dictionary containing evidence data
            
        Returns:
            str: Formatted JSON-style string
        """
        # Convert dictionary to formatted JSON string
        json_str = json.dumps(evidence_dict, ensure_ascii=False, indent=2)
        
        # Replace quotes with curly quotes for better appearance
        json_str = json_str.replace('"', '"').replace('":', '":')
        
        return json_str
    
    @staticmethod
    def _populate_multi_line_cells(table, evidence_dict, exclude_columns=None):
        """
        Populate table cells with one row per key-value pair
        
        Args:
            table: Table object
            evidence_dict: Dictionary containing evidence data
            exclude_columns: Columns to exclude from text
            
        Returns:
            tuple: (left_cells, right_cell) - List of left cells and merged right cell
        """
        if exclude_columns is None:
            exclude_columns = []
        
        # Get all keys and values
        left_cells = []
        
        # Populate left cells with text (one row per key-value pair)
        row_index = 0
        for key, value in evidence_dict.items():
            if key not in exclude_columns and value and str(value).strip():  # Only include non-empty values and non-excluded columns
                cell = table.cell(row_index, 0)
                # Convert value to string carefully to avoid escape characters
                if isinstance(value, str):
                    formatted_value = value
                else:
                    # For non-string types, convert without introducing escape characters
                    formatted_value = str(value)
                
                cell_text = f"{key}: {formatted_value}"
                ContentFormatter.add_text_to_cell(cell, cell_text, multi_line=False)
                left_cells.append(cell)
                row_index += 1
        
        # Merge right column cells vertically
        right_cell = table.cell(0, 1)
        if row_index > 1:
            right_cell.merge(table.cell(row_index - 1, 1))
        
        # Set vertical alignment for right cell
        right_cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        
        return left_cells, right_cell
    
    @staticmethod
    def _populate_json_format_cell(table, evidence_dict):
        """
        Populate left cell with formatted JSON string
        
        Args:
            table: Table object
            evidence_dict: Dictionary containing evidence data
            
        Returns:
            tuple: (left_cell, right_cell) - Left cell and right cell
        """
        # Format evidence as JSON
        json_text = EvidenceProcessor._format_json_dict(evidence_dict)
        
        # Add JSON text to left cell
        left_cell = table.cell(0, 0)
        ContentFormatter.add_text_to_cell(left_cell, json_text)
        
        # Get right cell
        right_cell = table.cell(0, 1)
        right_cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        
        return left_cell, right_cell
