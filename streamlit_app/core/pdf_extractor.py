# =============================================================================
# PDF Extraction Module
# =============================================================================

import os
from typing import Tuple, List, Dict
import fitz  # PyMuPDF
import pdfplumber
from .config import Config


class PDFExtractor:
    """Handles PDF content extraction with table preservation."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def extract_content(self, pdf_path: str) -> Tuple[str, List[Dict], Dict[str, int]]:
        """
        Extract structured content from PDF.
        
        Returns:
            main_content: Clean text content
            tables: List of table dictionaries
            stats: Extraction statistics
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        main_content = ""
        all_tables = []
        image_count = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in range(len(doc)):
                page = doc[page_num]
                plumber_page = pdf.pages[page_num]
                
                # Define header/footer regions
                page_height = page.rect.height
                footer_y_start = page_height - self.config.FOOTER_MARGIN
                header_y_end = self.config.HEADER_MARGIN
                
                # Extract tables first
                tables = plumber_page.find_tables()
                table_regions = []
                
                for table in tables:
                    table_regions.append(table.bbox)
                    extracted = table.extract()
                    
                    if extracted and len(extracted) > 1:
                        headers = [
                            h.replace("\n", " ").strip() if h else f"column_{i}"
                            for i, h in enumerate(extracted[0])
                        ]
                        
                        table_data = []
                        for row in extracted[1:]:
                            cleaned_row = [
                                cell.replace("\n", " ").strip() if cell else ""
                                for cell in row
                            ]
                            row_dict = dict(zip(headers, cleaned_row))
                            table_data.append(row_dict)
                        
                        all_tables.append({
                            "page": page_num + 1,
                            "data": table_data
                        })
                
                # Extract text blocks, excluding headers/footers/tables
                blocks = page.get_text("blocks")
                blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
                
                for block in blocks:
                    x0, y0, x1, y1, text = block[:5]
                    text = text.strip()
                    
                    if not text:
                        continue
                    
                    # Skip headers and footers
                    if y1 <= header_y_end or y0 >= footer_y_start:
                        continue
                    
                    # Skip text inside table regions
                    inside_table = any(
                        y0 >= ty0 and y1 <= ty1
                        for tx0, ty0, tx1, ty1 in table_regions
                    )
                    
                    if not inside_table:
                        main_content += text + "\n\n"
                
                image_count += len(page.get_images())
        
        # Get page count before closing document
        page_count = len(doc)
        doc.close()
        
        stats = {
            "pages": page_count,
            "tables": len(all_tables),
            "images": image_count,
            "text_length": len(main_content.split())
        }
        
        return main_content, all_tables, stats