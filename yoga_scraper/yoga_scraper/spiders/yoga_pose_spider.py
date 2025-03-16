import scrapy
import json
import re
import time
import logging
from urllib.parse import urlencode, quote_plus
from scrapy.http import Request
from ..items import YogaPoseImage

class YogaPoseSpider(scrapy.Spider):
    name = "yoga_poses"
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
    
    def start_requests(self):
        """Generate initial requests for each yoga pose."""
        for pose_name, pose_name_hindi in self.yoga_poses.items():
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
                
                yield Request(
                    url=url,
                    callback=self.parse_results,
                    meta={
                        'pose_name': pose_name,
                        'pose_name_hindi': pose_name_hindi,
                        'search_query': query,
                        'page': 1,
                    },
                    headers={
                        'User-Agent': self.settings.get('USER_AGENT'),
                    }
                )
    
    def parse_results(self, response):
        """Parse Google Images search results page."""
        pose_name = response.meta['pose_name']
        pose_name_hindi = response.meta['pose_name_hindi']
        search_query = response.meta['search_query']
        page = response.meta['page']
        
        # Extract image data from the page
        # Look for JSON data in the page that contains image information
        script_data = response.xpath('//script[contains(text(), "AF_initDataCallback")]/text()').getall()
        
        image_urls = []
        for script in script_data:
            # Try to extract image URLs from the script data
            image_matches = re.findall(r'\"(https://[^\"]+\.(jpg|jpeg|png))\"', script)
            for url, _ in image_matches:
                if url not in image_urls and self._is_valid_image_url(url):
                    image_urls.append(url)
        
        # Process found image URLs
        for i, image_url in enumerate(image_urls):
            yield YogaPoseImage(
                image_urls=[image_url],
                pose_name=pose_name,
                pose_name_hindi=pose_name_hindi,
                image_id=f"p{page}_i{i+1}"
            )
        
        # Log progress
        self.logger.info(f"Found {len(image_urls)} images for {pose_name} (page {page})")
        
        # Check if we need to go to the next page
        # Count how many images we've already scraped for this pose
        stats = self.crawler.stats
        pose_image_count = stats.get_value(f'pose_image_count/{pose_name_hindi}', 0) + len(image_urls)
        stats.set_value(f'pose_image_count/{pose_name_hindi}', pose_image_count)
        
        # If we haven't reached the minimum number of images, try to get more
        if pose_image_count < self.min_images_per_pose and page < 20:  # Limit to 20 pages max
            # Extract the "next page" URL if available
            next_page_url = None
            next_page_links = response.css('a.frGj1b::attr(href)').getall()
            if next_page_links:
                next_page_url = response.urljoin(next_page_links[0])
            
            # If next page URL is found, follow it
            if next_page_url:
                yield Request(
                    url=next_page_url,
                    callback=self.parse_results,
                    meta={
                        'pose_name': pose_name,
                        'pose_name_hindi': pose_name_hindi,
                        'search_query': search_query,
                        'page': page + 1,
                    },
                    headers={
                        'User-Agent': self.settings.get('USER_AGENT'),
                    }
                )
            # If no next page URL is found but we still need more images, try a different query
            elif page == 1:
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
                        
                        yield Request(
                            url=alt_url,
                            callback=self.parse_results,
                            meta={
                                'pose_name': pose_name,
                                'pose_name_hindi': pose_name_hindi,
                                'search_query': alt_query,
                                'page': 1,
                            },
                            headers={
                                'User-Agent': self.settings.get('USER_AGENT'),
                            }
                        )
    
    def _is_valid_image_url(self, url):
        """Check if the URL is a valid image URL."""
        # Exclude small thumbnails and icons
        if 'favicon' in url.lower() or 'icon' in url.lower():
            return False
        
        # Check if the URL has a valid image extension
        valid_extensions = ['.jpg', '.jpeg', '.png']
        return any(url.lower().endswith(ext) for ext in valid_extensions) 
