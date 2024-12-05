import asyncio
import aiohttp
import logging
import json
import os
import ssl
from bs4 import BeautifulSoup
from PIL import Image
import io
from PyPDF2 import PdfReader
from dataclasses import asdict
import re

from larodan_scraper.models import Product
from larodan_scraper.utils import (
    setup_logging,
    setup_directories,
    extract_packaging_info,
    extract_image_url,
    extract_pdf_url
)

logger = setup_logging()

class LarodanScraper:
    """Main class for Larodan product scraping"""
    
    def __init__(self, base_url: str, concurrent_crawlers: int = 3):
        self.base_url = base_url
        self.concurrent_crawlers = concurrent_crawlers
        self.session = None
        self.products_queue = asyncio.Queue()
        self.products_data = []
        
        setup_directories(['products/images', 'tmp', 'products'])

    async def init_session(self):
        """Initialize HTTP session with SSL disabled for development"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)

    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def get_page_content(self, url: str) -> str:
        """Get HTML content from a URL"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"Error {response.status} getting {url}")
                    return ""
        except Exception as e:
            logger.error(f"Error getting content from {url}: {e}")
            return ""

    async def get_product_urls(self) -> list:
        """Get URLs of all products, including pagination"""
        urls = set()
        current_page = 1
        
        while True:
            page_url = self.base_url
            if current_page > 1:
                page_url = f"{self.base_url}page/{current_page}/"
            
            logger.info(f"Processing page {page_url}")    
            html = await self.get_page_content(page_url)
            if not html:
                break
                
            soup = BeautifulSoup(html, 'html.parser')
            products = soup.select('tr.product')
            
            if not products:
                break
                
            for product in products:
                link = product.select_one('td.loop-product-title a')
                if link and link.get('href'):
                    urls.add(link['href'])
                    logger.info(f"Found product: {link['href']}")
            
            next_page = soup.select_one('a.next.page-numbers')
            if not next_page:
                break
                
            current_page += 1
            
        return list(urls)

    def extract_product_info(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract detailed product information"""
        properties = {}
        product_props = soup.select('div.product-prop')
        for prop in product_props:
            label = prop.select_one('span.prop-label')
            if label:
                label_text = label.text.strip()
                value = prop.get_text(strip=True).replace(label_text, '').strip(':').strip()
                properties[label_text] = value

        synonyms = []
        synonyms_section = soup.find('div', class_='product-prop product-prop-synonyms')
        if synonyms_section:
            synonyms_text = synonyms_section.get_text(strip=True).replace('Synonyms:', '').strip()
            if synonyms_text:
                synonyms = [syn.strip() for syn in synonyms_text.split(',')]

        structure_img = soup.select_one('.prod-structure img')
        structure = ""
        if structure_img and 'alt' in structure_img.attrs:
            structure = structure_img['alt'].replace('Structural formula of ', '')

        info = {
            'id': soup.select_one('span.sku').text.strip() if soup.select_one('span.sku') else "",
            'name': soup.select_one('h1.product-title').text.strip() if soup.select_one('h1.product-title') else "",
            'CAS': properties.get('CAS number:', ''),
            'structure': structure,
            'smiles': properties.get('Smiles:', ''),
            'description': properties.get('Description:', ''),
            'molecular_weight': properties.get('Molecular weight:', ''),
            'url': url,
            'image_path': '',
            'img': extract_image_url(soup),
            'pdf_msds': extract_pdf_url(soup),
            'synonyms': synonyms,
            'packaging': extract_packaging_info(soup)
        }
        return info

    async def save_image(self, img_url: str, product_id: str) -> str:
        """Save and process product image"""
        try:
            async with self.session.get(img_url) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type", "")
                    
                    if "image/svg+xml" in content_type:
                        svg_path = f"products/images/{product_id}.svg"
                        with open(svg_path, "wb") as f:
                            f.write(await response.read())
                        return svg_path
                    
                    data = await response.read()
                    img = Image.open(io.BytesIO(data))
                    
                    img.thumbnail((200, 200))
                    output_path = f"products/images/{product_id}.png"
                    img.save(output_path, "PNG", optimize=True)
                    return output_path
        except Exception as e:
            logger.error(f"Error saving image {img_url}: {e}")
        return ""

    async def extract_un_number(self, pdf_url: str) -> str:
        """Extract UN Number from PDF"""
        try:
            async with self.session.get(pdf_url) as response:
                if response.status == 200:
                    data = await response.read()
                    pdf_path = f"tmp/temp_{hash(pdf_url)}.pdf"
                    
                    with open(pdf_path, 'wb') as f:
                        f.write(data)
                    
                    with open(pdf_path, 'rb') as f:
                        pdf = PdfReader(f)
                        un_number = None
                        
                        for page in pdf.pages:
                            text = page.extract_text()
                            if "14.1" in text:
                                match = re.search(r'UN\s*(\d+)', text)
                                if match:
                                    un_number = match.group(1)
                                    break
                    
                    os.remove(pdf_path)
                    return un_number
                    
        except Exception as e:
            logger.error(f"Error extracting UN Number from {pdf_url}: {e}")
        return None

    async def process_product(self, url: str) -> Product:
        """Process individual product"""
        try:
            logger.info(f"Processing product: {url}")
            html = await self.get_page_content(url)
            if not html:
                return None
                
            soup = BeautifulSoup(html, 'html.parser')
            info = self.extract_product_info(soup, url)
            
            if info['img']:
                info['image_path'] = await self.save_image(info['img'], info['id'])
            
            if info['pdf_msds']:
                info['un_number'] = await self.extract_un_number(info['pdf_msds'])
            
            logger.info(f"Product processed successfully: {info['id']}")
            return Product(**info)
            
        except Exception as e:
            logger.error(f"Error processing product {url}: {e}")
            return None

    async def run(self):
        """Run complete scraping process"""
        try:
            await self.init_session()
            
            logger.info("Starting product listing...")
            product_urls = await self.get_product_urls()
            logger.info(f"Found {len(product_urls)} products")
            
            logger.info(f"Starting crawling with {self.concurrent_crawlers} crawlers...")
            tasks = []
            semaphore = asyncio.Semaphore(self.concurrent_crawlers)
            
            async def process_with_semaphore(url):
                async with semaphore:
                    return await self.process_product(url)
            
            tasks = [process_with_semaphore(url) for url in product_urls]
            products = await asyncio.gather(*tasks)
            products = [p for p in products if p is not None]
            
            logger.info(f"Saving {len(products)} products...")
            output_path = 'products/products.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(p) for p in products], f, indent=2)
            
            logger.info(f"Process completed. Results saved in {output_path}")
            
        except Exception as e:
            logger.error(f"Error in main process: {e}")
        finally:
            await self.close_session()