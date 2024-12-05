# Larodan Product Scraper

A Python-based web scraper for extracting product information from Larodan's website. This tool asynchronously scrapes product details, including images, PDFs, and safety information.

## Features

- Asynchronous web scraping with configurable concurrency
- Product information extraction including:
  - Basic product details (ID, name, CAS number)
  - Chemical structure and SMILES notation
  - Molecular weight
  - Product images (with automatic processing)
  - Safety data sheets (PDF)
  - UN numbers extraction from PDFs
  - Packaging and pricing information
  - Product synonyms
- Automatic image processing and thumbnail generation
- PDF parsing for safety information
- JSON output for scraped data
- Comprehensive logging

## Requirements

- Python 3.10+
- See `requirements.txt` for package dependencies

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/larodan-scraper.git
cd larodan-scraper
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

Basic usage:
```bash
python3 -m larodan_scraper --url "https://www.larodan.com/products/category/monounsaturated-fa/" -c 3
```

Arguments:
- `--url`: Base URL for scraping (default: https://www.larodan.com/products/category/monounsaturated-fa/)
- `-c`: Number of concurrent crawlers (default: 3)

## Output

The scraper creates the following directory structure:
```
products/
├── images/      # Product images and structures
├── products.json # Scraped product data
└── tmp/         # Temporary files (cleaned up after processing)
```

## Data Format

The scraped data is saved in JSON format with the following structure:
```json
{
  "id": "string",
  "name": "string",
  "CAS": "string",
  "structure": "string",
  "smiles": "string",
  "description": "string",
  "molecular_weight": "string",
  "url": "string",
  "image_path": "string",
  "img": "string",
  "pdf_msds": "string",
  "synonyms": ["string"],
  "packaging": {
    "size": "price"
  },
  "un_number": "string"
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.