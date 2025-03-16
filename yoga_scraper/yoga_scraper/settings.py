BOT_NAME = "yoga_scraper"

SPIDER_MODULES = ["yoga_scraper.spiders"]
NEWSPIDER_MODULE = "yoga_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True

# Disable cookies
COOKIES_ENABLED = False

# Configure item pipelines
ITEM_PIPELINES = {
    "yoga_scraper.pipelines.YogaImagesPipeline": 1,
}

# Set settings for images pipeline
IMAGES_STORE = "yoga_dataset"
IMAGES_EXPIRES = 90  # 90 days of delay for image expiration

# Configure the size and quality of downloaded images
IMAGES_THUMBS = {
    "small": (50, 50),
    "medium": (224, 224),
}

# Configure the minimum width and height for downloaded images
IMAGES_MIN_WIDTH = 100
IMAGES_MIN_HEIGHT = 100

# Configure the maximum width and height for downloaded images
IMAGES_MAX_WIDTH = 4000
IMAGES_MAX_HEIGHT = 4000

# Configure user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 1 day
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [503, 504, 505, 500, 400, 401, 402, 403, 404]

# Configure logging
LOG_LEVEL = "INFO"

# Configure download timeout
DOWNLOAD_TIMEOUT = 180  # 3 minutes

# Configure retry settings
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Configure download handlers
DOWNLOAD_HANDLERS = {
    "http": "scrapy.core.downloader.handlers.http.HTTPDownloadHandler",
    "https": "scrapy.core.downloader.handlers.http.HTTPDownloadHandler",
}

# Configure request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
} 
