import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Specify yoga poses (using the original Hindi names)
yoga_poses = [
    "ताड़ासन", "त्रिकोणासन", "दुर्वासन", "अर्धचंद्रासन",
    "उष्ट्रासन", "धनुरासन", "भुजंगासन",
    "हलासन", "सेतुबंधासन"
]

# Directory to save images
dataset_dir = "yoga_dataset"
os.makedirs(dataset_dir, exist_ok=True)

# Configure Selenium WebDriver (Headless)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def scrape_images(pose_name, num_images=200):
    search_query = pose_name + " yoga pose person home background -thumbnail -video"
    save_dir = os.path.join(dataset_dir, pose_name)
    os.makedirs(save_dir, exist_ok=True)

    # Open Google Images
    driver.get("https://images.google.com/")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)

    # Scroll and fetch image URLs
    image_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(image_urls) < num_images:
        # Find elements, then extract URLs. This avoids StaleElementReferenceException
        images = driver.find_elements(By.CSS_SELECTOR, "img") # Use a broader CSS selector for Google Images
        for img in images:
            src = img.get_attribute("src")
            if src and src.startswith("http") and src not in image_urls:
                image_urls.add(src)
                if len(image_urls) >= num_images:
                    break

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for more images to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Try clicking "Show more results" button if present
            try:
                show_more_button = driver.find_element(By.CSS_SELECTOR, ".mye4qd")
                if show_more_button.is_displayed():
                    show_more_button.click()
                    time.sleep(2)  # Wait for more images
                    new_height = driver.execute_script("return document.body.scrollHeight") # Update height
            except Exception:
                break  # If button not found or other error, exit loop
        last_height = new_height

    # Download images
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, stream=True, timeout=10) # Increased timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            if response.status_code == 200:
                with open(os.path.join(save_dir, f"{pose_name}_{i+1}.jpg"), "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192): # Download in chunks
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")
    print(f"Downloaded {len(image_urls)} images for {pose_name}.")

# Scrape images for each pose
for pose in yoga_poses:
    scrape_images(pose)

# Close WebDriver
driver.quit()
