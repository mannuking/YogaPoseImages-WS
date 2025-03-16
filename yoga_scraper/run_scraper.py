import os
import sys
import time
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from yoga_scraper.spiders.selenium_yoga_spider import SeleniumYogaPoseSpider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_scraper():
    """Run the Scrapy spider to scrape yoga pose images."""
    # Create the yoga_dataset directory if it doesn't exist
    os.makedirs("yoga_dataset", exist_ok=True)
    
    # Get the Scrapy project settings
    settings = get_project_settings()
    
    # Create a CrawlerProcess with the project settings
    process = CrawlerProcess(settings)
    
    # Start the spider
    process.crawl(SeleniumYogaPoseSpider)
    
    # Start the crawling process
    process.start()

if __name__ == "__main__":
    start_time = time.time()
    logging.info("Starting the yoga pose image scraper...")
    
    try:
        run_scraper()
        logging.info("Scraping completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Total time elapsed: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)") 
