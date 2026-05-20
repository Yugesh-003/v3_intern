# PDF Financial Document Extraction & Analysis

A Python-based project for extracting and analyzing structured data from PDF financial documents using advanced text extraction and table parsing techniques.

## Overview

This project demonstrates a robust pipeline for extracting financial information from PDF documents, specifically designed to handle complex layouts with headers, footers, tables, and multi-page documents. The implementation uses PyMuPDF (fitz) and pdfplumber to intelligently parse and organize document content.

## Features

- **Intelligent Text Extraction**: Separates document content into headers, main content, and footers based on spatial positioning
- **Table Parsing**: Automatically detects and extracts tables from PDFs, converting them to structured JSON format
- **Header/Footer Detection**: Identifies and isolates page headers and footers using configurable margin thresholds
- **Image Detection**: Counts and tracks images within PDF documents
- **Structured Output**: Returns organized data including:
  - Header content with page references
  - Main body text
  - Footer information
  - Extracted tables as JSON objects
  - Image count statistics

## Project Structure

```
.
├── may_19.ipynb                    # Main Jupyter notebook with extraction pipeline
├── data/
│   └── finance_evaluation.pdf      # Sample financial document (Q1 2026 Portfolio Review)
├── .venv/                          # Python virtual environment
└── README.md                       # This file
```

## Dependencies

The project requires the following Python packages:

- **pymupdf** (1.27.2.3+) - PyMuPDF library for PDF text extraction
- **pdfplumber** (0.11.9+) - Advanced PDF parsing and table extraction
- **Pillow** (9.1+) - Image processing support
- **pdfminer.six** (20251230) - PDF mining utilities
- **pypdfium2** (4.18.0+) - PDF rendering engine

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install pymupdf pdfplumber
```

The notebook will automatically install additional dependencies when run.

## Usage

### Running the Extraction Pipeline

The main extraction function is defined in the notebook:

```python
from may_19 import extract_text

# Extract content from a PDF
header_content, main_content, footer_content, tables_json, image_count = extract_text("path/to/document.pdf")
```

### Configuration Parameters

The extraction behavior can be customized via these parameters:

- **FOOTER_MARGIN** (default: 50): Pixel distance from bottom of page to identify footer content
- **HEADER_MARGIN** (default: 70): Pixel distance from top of page to identify header content

### Output Format

The function returns a tuple of five elements:

1. **header_content** (list): List of dictionaries with page number and header text
2. **main_content** (str): Concatenated main body text from all pages
3. **footer_content** (list): List of dictionaries with page number and footer text
4. **tables_json** (list): List of extracted tables with page references and structured data
5. **image_count** (int): Total number of images found in the document

### Example Output

```python
# Headers
[{'page': 1, 'text': 'PAGE 1 OF 3'}, ...]

# Tables
[{
    'page': 2,
    'table_data': [
        {
            'Asset Classification': 'Domestic Large-Cap Equities',
            'Target Alloc %': '30.0%',
            'Current Alloc %': '32.4%',
            ...
        },
        ...
    ]
}]
```

## Sample Document

The included `finance_evaluation.pdf` is a Q1 2026 Portfolio Review from Apex Global Wealth Management containing:

- **Monetary Policy Analysis**: Discussion of capital markets and interest rate trends
- **Asset Allocation**: Detailed breakdown of portfolio composition
- **Fixed-Income Outlook**: Analysis of bond markets and yield curves
- **Equity Sector Analysis**: Performance review of various market segments
- **Risk Management**: Volatility modeling and stress-testing frameworks
- **Strategic Recommendations**: Forward-looking portfolio adjustments

The document includes a comprehensive asset allocation table with current values, target allocations, Q1 returns, and strategic actions.

## Technical Details

### Text Extraction Strategy

1. **Block Sorting**: Text blocks are sorted by vertical position (top to bottom) for logical reading order
2. **Spatial Classification**: Content is classified as header, footer, or main based on Y-coordinates
3. **Table Detection**: Tables are identified separately to avoid duplicate text extraction
4. **Text Cleaning**: Newlines within cells are normalized to spaces for readability

### Table Extraction

- Tables are detected using pdfplumber's table detection algorithm
- Headers are automatically identified from the first row
- Missing headers are labeled as `column_N`
- Cell content is cleaned and normalized
- Each table is associated with its source page number

## Limitations

- Extraction quality depends on PDF structure and formatting
- Complex nested tables may require additional processing
- Scanned PDFs (image-based) require OCR preprocessing
- Margin thresholds may need adjustment for different document layouts

## Future Enhancements

- OCR support for scanned documents
- Advanced table structure recognition for complex layouts
- Named entity recognition for financial data
- Automatic document classification
- Export to multiple formats (CSV, Excel, JSON)

## License

This project is provided as-is for educational and analytical purposes.

## Notes

The financial document included is a sample for demonstration purposes and does not represent actual investment advice or real portfolio data.
