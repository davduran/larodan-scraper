import argparse
import asyncio
from larodan_scraper.scraper import LarodanScraper

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Larodan Product Scraper')
    parser.add_argument(
        '-c', 
        type=int, 
        default=3, 
        help='Number of concurrent crawlers'
    )
    parser.add_argument(
        '--url', 
        type=str, 
        default='https://www.larodan.com/products/category/monounsaturated-fa/',
        help='Base URL for scraping'
    )
    args = parser.parse_args()
    
    scraper = LarodanScraper(args.url, args.c)
    asyncio.run(scraper.run())

if __name__ == "__main__":
    main()