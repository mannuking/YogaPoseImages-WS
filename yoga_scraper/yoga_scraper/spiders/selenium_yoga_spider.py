import scrapy
import json
import re
import time
import logging
import os
from urllib.parse import urlencode, quote_plus
from scrapy.http import Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except Exception:
    WEBDRIVER_MANAGER_AVAILABLE = False
from ..items import YogaPoseImage

class SeleniumYogaPoseSpider(scrapy.Spider):
    name = "selenium_yoga_poses"
    allowed_domains = ["google.com", "gstatic.com", "googleapis.com"]
    
    # Define yoga poses with English and Hindi names
    yoga_poses = {
        "Tadasana (Mountain Pose)": "ताड़ासन",
        "Trikonasana (Triangle Pose)": "त्रिकोणासन",
        "Durvasana (Durva Grass Pose)": "दुर्वासन",
        "Ardha Chandrasana (Half Moon Pose)": "अर्धचंद्रासन",
        "Ustrasana (Camel Pose)": "उष्ट्रासन",
        "Dhanurasana (Bow Pose)": "धनुरासन",
        "Bhujangasana (Cobra Pose)": "भुजंगासन",
        "Vrksasana (Tree Pose)": "वृक्षासन",
        "Halasana (Plow Pose)": "हलासन",
        "Setu Bandhasana (Bridge Pose)": "सेतुबंधासन",
        "Akarna Dhanurasana (Shooting Bow Pose)": "आकर्ण धनुरासन",
        "Gomukhasana (Cow Face Pose)": "गोमुखासन"
    }
    
    # Maximum number of images to download per pose
    max_images_per_pose = 500
    
    # Minimum number of images to download per pose
    min_images_per_pose = 200
    
    def __init__(self, *args, **kwargs):
        super(SeleniumYogaPoseSpider, self).__init__(*args, **kwargs)
        # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Set user agent
        chrome_options.add_argument(f"user-agent={self.settings.get('USER_AGENT')}")
        
        # Initialize Chrome driver
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                # Try using webdriver_manager with explicit version
                self.driver = webdriver.Chrome(
                    ChromeDriverManager(version="114.0.5735.90").install(),
                    options=chrome_options
                )
            else:
                # Fallback to direct ChromeDriver path
                # Try to find ChromeDriver in common locations
                chromedriver_paths = [
                    "./chromedriver.exe",  # Current directory
                    "./chromedriver",
                    "chromedriver.exe",
                    "chromedriver",
                ]
                
                # Check if CHROMEDRIVER_PATH environment variable is set
                if "CHROMEDRIVER_PATH" in os.environ:
                    chromedriver_paths.insert(0, os.environ["CHROMEDRIVER_PATH"])
                
                # Try each path
                for path in chromedriver_paths:
                    if os.path.exists(path):
                        self.logger.info(f"Using ChromeDriver at: {path}")
                        service = Service(executable_path=path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        break
                else:
                    # If no ChromeDriver found, try without specifying path (system PATH)
                    self.logger.warning("ChromeDriver not found in common locations. Trying system PATH.")
                    self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            self.logger.error(f"Error initializing Chrome driver: {e}")
            self.logger.info("Please download ChromeDriver manually from https://chromedriver.chromium.org/downloads")
            self.logger.info("and place it in the project directory or add it to your system PATH.")
            raise
        
        # Create a directory to store pose counts
        self.counts_dir = os.path.join(self.settings.get('IMAGES_STORE', 'yoga_dataset'), 'counts')
        os.makedirs(self.counts_dir, exist_ok=True)
    
    def closed(self, reason):
        """Close the Selenium driver when the spider is closed."""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def start_requests(self):
        """Generate initial requests for each yoga pose."""
        for pose_name, pose_name_hindi in self.yoga_poses.items():
            # Check if we already have enough images for this pose
            if self._get_pose_image_count(pose_name_hindi) >= self.min_images_per_pose:
                self.logger.info(f"Already have enough images for {pose_name}. Skipping.")
                continue
                
            # Create search queries with variations to get diverse images
            search_queries = [
                f"{pose_name} yoga pose person",
                f"{pose_name} yoga asana",
                f"{pose_name_hindi} yoga pose",
                f"{pose_name} yoga position person",
                f"{pose_name} yoga practice",
            ]
            
            for query in search_queries:
                # Encode the search query
                params = {
                    'q': query,
                    'tbm': 'isch',  # Google Images search
                    'hl': 'en',     # Language: English
                    'gl': 'us',     # Country: US
                    'tbs': 'isz:m', # Medium sized images
                }
                
                url = f"https://www.google.com/search?{urlencode(params)}"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_results,
                    meta={
                        'pose_name': pose_name,
                        'pose_name_hindi': pose_name_hindi,
                        'search_query': query,
                        'page': 1,
                    },
                    dont_filter=True  # Don't filter duplicate requests
                )
    
    def parse_results(self, response):
        """Parse Google Images search results page using Selenium."""
        pose_name = response.meta['pose_name']
        pose_name_hindi = response.meta['pose_name_hindi']
        search_query = response.meta['search_query']
        page = response.meta['page']
        
        # Check if we already have enough images for this pose
        current_count = self._get_pose_image_count(pose_name_hindi)
        if current_count >= self.max_images_per_pose:
            self.logger.info(f"Reached maximum image count for {pose_name}. Skipping.")
            return
        
        # Load the page with Selenium
        try:
            self.driver.get(response.url)
            
            # Wait for the images to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.rg_i"))
            )
            
            # Scroll down to load more images
            self._scroll_to_load_more_images()
            
            # Extract image URLs
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
            image_urls = []
            
            for img in image_elements:
                # Try to get the full-size image URL
                try:
                    # Click on the image to open the full-size view
                    img.click()
                    
                    # Wait for the full-size image to load
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "img.r48jcc"))
                    )
                    
                    # Get the full-size image URL
                    full_img = self.driver.find_element(By.CSS_SELECTOR, "img.r48jcc")
                    src = full_img.get_attribute("src")
                    
                    if src and src.startswith("http") and self._is_valid_image_url(src):
                        image_urls.append(src)
                        
                        # Yield the image item
                        yield YogaPoseImage(
                            image_urls=[src],
                            pose_name=pose_name,
                            pose_name_hindi=pose_name_hindi,
                            image_id=f"p{page}_i{len(image_urls)}"
                        )
                        
                        # Update the pose image count
                        self._increment_pose_image_count(pose_name_hindi)
                        
                        # Check if we've reached the maximum number of images
                        if len(image_urls) >= self.max_images_per_pose - current_count:
                            break
                
                except (TimeoutException, WebDriverException) as e:
                    self.logger.warning(f"Error clicking image: {e}")
                    continue
            
            # Log progress
            self.logger.info(f"Found {len(image_urls)} images for {pose_name} (page {page})")
            
            # Check if we need to go to the next page
            current_count = self._get_pose_image_count(pose_name_hindi)
            if current_count < self.min_images_per_pose and page < 10:  # Limit to 10 pages max
                # Try to find and click the "Show more results" button
                try:
                    show_more_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".mye4qd"))
                    )
                    show_more_button.click()
                    time.sleep(2)  # Wait for more images to load
                    
                    # Get the updated URL
                    next_page_url = self.driver.current_url
                    
                    yield scrapy.Request(
                        url=next_page_url,
                        callback=self.parse_results,
                        meta={
                            'pose_name': pose_name,
                            'pose_name_hindi': pose_name_hindi,
                            'search_query': search_query,
                            'page': page + 1,
                        },
                        dont_filter=True  # Don't filter duplicate requests
                    )
                except (TimeoutException, WebDriverException) as e:
                    self.logger.warning(f"Error clicking 'Show more results' button: {e}")
                    
                    # If we can't find the "Show more results" button, try a different query
                    if page == 1:
                        # Try a different search query
                        alternative_queries = [
                            f"{pose_name} yoga demonstration",
                            f"{pose_name} yoga tutorial",
                            f"{pose_name_hindi} yoga",
                            f"{pose_name} yoga home practice",
                        ]
                        
                        for alt_query in alternative_queries:
                            if alt_query != search_query:  # Avoid duplicate queries
                                params = {
                                    'q': alt_query,
                                    'tbm': 'isch',
                                    'hl': 'en',
                                    'gl': 'us',
                                    'tbs': 'isz:m',
                                }
                                
                                alt_url = f"https://www.google.com/search?{urlencode(params)}"
                                
                                yield scrapy.Request(
                                    url=alt_url,
                                    callback=self.parse_results,
                                    meta={
                                        'pose_name': pose_name,
                                        'pose_name_hindi': pose_name_hindi,
                                        'search_query': alt_query,
                                        'page': 1,
                                    },
                                    dont_filter=True  # Don't filter duplicate requests
                                )
        
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")
    
    def _scroll_to_load_more_images(self, max_scrolls=10):
        """Scroll down to load more images."""
        for _ in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Wait for images to load
    
    def _is_valid_image_url(self, url):
        """Check if the URL is a valid image URL."""
        # Exclude small thumbnails and icons
        if 'favicon' in url.lower() or 'icon' in url.lower():
            return False
        
        # Check if the URL has a valid image extension or is a valid image URL
        valid_extensions = ['.jpg', '.jpeg', '.png']
        has_valid_extension = any(url.lower().endswith(ext) for ext in valid_extensions)
        
        # Also check for image URLs that don't have a file extension
        is_image_url = 'image' in url.lower() or 'img' in url.lower() or 'photo' in url.lower()
        
        return has_valid_extension or is_image_url
    
    def _get_pose_image_count(self, pose_name_hindi):
        """Get the current count of images for a pose."""
        count_file = os.path.join(self.counts_dir, f"{pose_name_hindi}.count")
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                return int(f.read().strip())
        return 0
    
    def _increment_pose_image_count(self, pose_name_hindi):
        """Increment the count of images for a pose."""
        count_file = os.path.join(self.counts_dir, f"{pose_name_hindi}.count")
        current_count = self._get_pose_image_count(pose_name_hindi)
        with open(count_file, 'w') as f:
            f.write(str(current_count + 1)) 
