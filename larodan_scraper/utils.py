import logging
import os
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
import re

def setup_logging():
    """Configure logging settings"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def setup_directories(dirs: List[str]):
    """Create necessary directories for storing files"""
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)

def extract_packaging_info(soup: BeautifulSoup) -> dict:
    """Extract packaging and pricing information"""
    packaging = {}
    variations_table = soup.find("table", {"class": "product-variations-table"})
    if variations_table:
        for row in variations_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 5:
                package_info = cells[1].text.strip()
                if ' - ' in package_info:
                    package_size = package_info.split(' - ')[-1]
                else:
                    package_size = package_info
                    
                price_info = cells[3].text.strip()
                if price_info:
                    price = float(re.sub(r"[^\d.]", "", price_info))
                else:
                    price = None
                packaging[package_size] = price
    return packaging

def extract_image_url(soup: BeautifulSoup) -> str:
    """Extract product image URL"""
    structure_img = soup.select_one('.prod-structure img')
    if structure_img and 'src' in structure_img.attrs:
        return structure_img['src']
    return ""

def extract_pdf_url(soup: BeautifulSoup) -> str:
    """Extract safety PDF URL"""
    pdf_link = soup.select_one('a[href*=".pdf"]')
    if pdf_link and 'href' in pdf_link.attrs:
        return pdf_link['href']
    return ""