"""
Table utilities for Word documents.
"""
from docx.shared import Inches
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from precisiondoc.config.document_format_settings import TABLE_SETTINGS

class TableUtils:
    """Handles table-related operations"""
    
    @staticmethod
    def _create_basic_table(doc, row_count, cols=2):
        """
        Create a basic table with specified rows and columns
        
        Args:
            doc: Word document
            row_count: Number of rows
            cols: Number of columns (default: 2)
            
        Returns:
            table: Created table
        """
        # 使用样式1创建表格，这是一个有边框的表格样式
        table = doc.add_table(rows=row_count, cols=cols, style='Table Grid')
        table.autofit = False
        table.allow_autofit = False
        return table
    
    @staticmethod
    def _set_table_column_widths(table, is_landscape):
        """
        Set table and column widths based on orientation
        
        Args:
            table: Table object
            is_landscape: Whether the page is in landscape orientation
            
        Returns:
            tuple: (table_width, text_col_width, image_col_width)
        """
        # Set table width based on orientation (accounting for margins) using config settings
        if is_landscape:
            table_width = Inches(TABLE_SETTINGS['landscape_table_width'])
        else:
            table_width = Inches(TABLE_SETTINGS['portrait_table_width'])
            
        # Calculate column widths based on ratio settings from config
        text_col_width = Inches(table_width.inches * TABLE_SETTINGS['text_column_ratio'])
        image_col_width = Inches(table_width.inches * TABLE_SETTINGS['image_column_ratio'])
            
        table.width = table_width
        
        # Set column widths using direct XML manipulation for more reliable width control
        tbl_grid = table._element.find(".//w:tblGrid", table._element.nsmap)
        
        # Clear existing grid columns if any
        for grid_col in tbl_grid.findall(".//w:gridCol", table._element.nsmap):
            tbl_grid.remove(grid_col)
        
        # Create new grid columns with desired widths
        col1 = OxmlElement('w:gridCol')
        col1.set(qn('w:w'), str(int(text_col_width.twips)))  # Text column
        tbl_grid.append(col1)
        
        col2 = OxmlElement('w:gridCol')
        col2.set(qn('w:w'), str(int(image_col_width.twips)))  # Image column
        tbl_grid.append(col2)
        
        # Set column widths at the cell level too
        for row in table.rows:
            row.cells[0].width = text_col_width
            row.cells[1].width = image_col_width
            
        return table_width, text_col_width, image_col_width
    
    @staticmethod
    def _set_table_pagination_properties(table):
        """
        Set table properties for pagination (allowing table to break across pages)
        
        Args:
            table: Table object
        """
        # Set table properties for continuation across pages
        table_pr = table._element.xpath('w:tblPr')[0]
        table_layout = OxmlElement('w:tblLayout')
        table_layout.set(qn('w:type'), 'fixed')
        table_pr.append(table_layout)
        
        # Allow row to break across pages
        for row in table.rows:
            tr = row._tr
            trPr = tr.get_or_add_trPr()
            cantSplit = OxmlElement('w:cantSplit')
            cantSplit.set(qn('w:val'), '0')  # 0 means can split
            trPr.append(cantSplit)
    
    @staticmethod
    def _remove_table_borders(table):
        """
        Remove all borders from a table
        
        Args:
            table: Table object to remove borders from
        """
        for row in table.rows:
            for cell in row.cells:
                # Set border width to 0 using XML directly
                tcPr = cell._element.tcPr
                if tcPr is None:
                    tcPr = OxmlElement('w:tcPr')
                    cell._element.append(tcPr)
                
                # Create border element for each side
                for side in ['top', 'left', 'bottom', 'right']:
                    # Create border element if it doesn't exist
                    tc_borders = tcPr.find('.//w:tcBorders', namespaces=tcPr.nsmap)
                    if tc_borders is None:
                        tc_borders = OxmlElement('w:tcBorders')
                        tcPr.append(tc_borders)
                    
                    # Create or find the specific border
                    border_elem_tag = f'w:{side}'
                    border = tc_borders.find(border_elem_tag, namespaces=tcPr.nsmap)
                    if border is None:
                        border = OxmlElement(border_elem_tag)
                        tc_borders.append(border)
                    
                    # Set border to none
                    border.set(qn('w:val'), 'nil')
