# Word document font settings
WORD_FONT_SETTINGS = {
    'default_font_name': 'Microsoft YaHei',  # Default font for regular text
    'east_asia_font_name': 'Microsoft YaHei',  # Font for East Asian characters
    'default_font_size': 10,  # Default font size in points
    'heading_font_name': 'Microsoft YaHei',  # Font for headings
    'heading_font_size': 16,  # Font size for headings in points
    'subheading_font_size': 12,  # Font size for subheadings in points
    'run_font_name': 'Microsoft YaHei',  # Font for regular text runs
    'run_font_size': 10,  # Font size for regular text runs
    'page_number_font_name': 'Microsoft YaHei',  # Font for page numbers
    'separator_font_name': 'Microsoft YaHei',  # Font for separator lines
}

# Table formatting settings
TABLE_SETTINGS = {
    'show_borders_default': True,  # Default setting for showing table borders
    'multi_line_text_default': False,  # Default setting for multi-line text in cells
    
    # Table width settings (in inches)
    'portrait_table_width': 6.27,  # A4 portrait width minus margins
    'landscape_table_width': 9.69,  # A4 landscape width minus margins
    
    # Column ratio settings (percentage as decimal)
    'text_column_ratio': 0.2,  # Text column takes 20% of table width
    'image_column_ratio': 0.8,  # Image column takes 80% of table width
    
    # Image width setting (in inches)
    # If not specified, will use 90% of the image column width
    'image_width': None,  # Set to a specific value to override the automatic calculation
}

# Image formatting settings
IMAGE_SETTINGS = {
    'width_ratio': 0.9,  # Image width as a ratio of the column width (90%)
    'max_height': None,  # Maximum height in inches (None = no limit)
    'fallback_text': 'Image not available',  # Text to display when image is not found
}
