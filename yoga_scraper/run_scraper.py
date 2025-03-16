import os
import sys
import time
import logging
import platform
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

def check_chromedriver():
    """Check if ChromeDriver is available."""
    system = platform.system()
    chromedriver_name = "chromedriver.exe" if system == "Windows" else "chromedriver"
    
    # Check common locations
    chromedriver_paths = [
        os.path.join(".", chromedriver_name),  # Current directory
        os.path.join("..", chromedriver_name),  # Parent directory
        chromedriver_name,  # System PATH
    ]
    
    # Check if CHROMEDRIVER_PATH environment variable is set
    if "CHROMEDRIVER_PATH" in os.environ:
        chromedriver_paths.insert(0, os.environ["CHROMEDRIVER_PATH"])
    
    # Check each path
    for path in chromedriver_paths:
        if os.path.exists(path):
            logging.info(f"Found ChromeDriver at: {path}")
            return True
    
    logging.warning("ChromeDriver not found in common locations.")
    logging.info("Please run download_chromedriver.py to download ChromeDriver.")
    return False

def run_scraper():
    """Run the Scrapy spider to scrape yoga pose images."""
    # Check if ChromeDriver is available
    if not check_chromedriver():
        try:
            # Try to import webdriver_manager to see if it's available
            from webdriver_manager.chrome import ChromeDriverManager
            logging.info("webdriver_manager is available. Will try to use it.")
        except ImportError:
            logging.error("ChromeDriver not found and webdriver_manager is not available.")
            logging.info("Please run download_chromedriver.py to download ChromeDriver.")
            return False
    
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
    
    return True

if __name__ == "__main__":
    start_time = time.time()
    logging.info("Starting the yoga pose image scraper...")
    
    try:
        success = run_scraper()
        if success:
            logging.info("Scraping completed successfully.")
        else:
            logging.error("Scraping failed. Please check the error messages above.")
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Total time elapsed: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)") 
