import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import face_recognition  # Add this to requirements.txt

def is_valid_image(img_data):
    """Check if image meets our criteria"""
    try:
        # Convert bytes to PIL Image
        img = Image.open(BytesIO(img_data))
        
        # Check image dimensions (minimum 400x400, maximum 4000x4000)
        width, height = img.size
        if width < 400 or height < 400 or width > 4000 or height > 4000:
            return False
            
        # Convert to numpy array for processing
        img_np = np.array(img)
        
        # Check if image is not black and white or grayscale
        if len(img_np.shape) < 3 or img_np.shape[2] < 3:
            return False
            
        # Detect faces to ensure it's a real person
        face_locations = face_recognition.face_locations(img_np)
        if len(face_locations) == 0:
            return False
            
        # Check if image is not a cartoon/illustration
        # Calculate edge density
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (width * height)
        if edge_density > 0.1:  # Threshold for cartoon detection
            return False
            
        return True
    except Exception:
        return False

def scrape_images(pose_name, num_images=200):
    search_query = f"{pose_name} yoga pose real person -illustration -cartoon"
    save_dir = os.path.join(dataset_dir, pose_name)
    os.makedirs(save_dir, exist_ok=True)

    # Open Google Images
    driver.get("https://images.google.com/")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)

    # Add tools menu interaction to filter for large images
    try:
        tools_button = driver.find_element(By.XPATH, "//div[text()='Tools']")
        tools_button.click()
        time.sleep(1)
        
        size_button = driver.find_element(By.XPATH, "//div[text()='Size']")
        size_button.click()
        time.sleep(1)
        
        large_option = driver.find_element(By.XPATH, "//div[text()='Large']")
        large_option.click()
        time.sleep(2)
    except Exception as e:
        print(f"Failed to set image size filter: {e}")

    image_urls = set()
    valid_images = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while valid_images < num_images:
        images = driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
        for img in images:
            try:
                # Click image to get full resolution version
                img.click()
                time.sleep(1)
                
                # Get the full resolution image URL
                full_img = driver.find_element(By.CSS_SELECTOR, "img.n3VNCb")
                src = full_img.get_attribute("src")
                
                if src and src.startswith("http") and src not in image_urls:
                    # Download and validate image
                    response = requests.get(src, timeout=10)
                    if response.status_code == 200 and is_valid_image(response.content):
                        image_urls.add(src)
                        # Save the image
                        save_path = os.path.join(save_dir, f"{pose_name}_{valid_images+1}.jpg")
                        with open(save_path, "wb") as f:
                            f.write(response.content)
                        valid_images += 1
                        print(f"Downloaded valid image {valid_images}/{num_images} for {pose_name}")
                        
                        if valid_images >= num_images:
                            return
            except Exception as e:
                print(f"Error processing image: {e}")
                continue

        # Scroll and try to load more images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            try:
                show_more_button = driver.find_element(By.CSS_SELECTOR, ".mye4qd")
                if show_more_button.is_displayed():
                    show_more_button.click()
                    time.sleep(2)
                else:
                    break
            except Exception:
                break
        last_height = new_height

# Main execution
if __name__ == "__main__":
    # Directory to save images
    dataset_dir = "yoga_dataset"
    os.makedirs(dataset_dir, exist_ok=True)

    # Configure Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    # Yoga poses list
    yoga_poses = [
        "ताड़ासन", "त्रिकोणासन", "दुर्वासन", "अर्धचंद्रासन",
        "उष्ट्रासन", "धनुरासन", "भुजंगासन", "मौलासन",
        "हलासन", "सेतुबंधासन"
    ]

    try:
        for pose in yoga_poses:
            scrape_images(pose)
    finally:
driver.quit()
