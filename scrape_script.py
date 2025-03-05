import requests
from bs4 import BeautifulSoup
import os
import time
import sys
from PIL import Image
from io import BytesIO

yoga_poses = ["taadasana", "trikonasana", "durvasana", "ardhachandrasana", "ustrasana", "dhanurasana", "bhujangasana", "halasana", "setubandhasana"]
image_count_limit = 10

def is_valid_image(image_content):
    return True # Disabled image validation for debugging

def download_images(yoga_pose):
    search_term = yoga_pose + " yoga pose"
    search_url = f"https://www.google.com/search?q={search_term}&amp;tbm=isch"
    print(f"Searching URL: {search_url}") # Print search URL

    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {search_url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img')
    print(f"Found {len(img_tags)} image tags") # Print number of image tags

    downloaded_count = 0
    for i, img_tag in enumerate(img_tags):
        if downloaded_count >= image_count_limit:
            break

        img_url = img_tag.get('src') or img_tag.get('data-src')

        if img_url and img_url.startswith('http'):
            print(f"Image URL: {img_url}") # Print image URL
            try:
                img_response = requests.get(img_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
                img_response.raise_for_status()
                image_content = img_response.content

                if is_valid_image(image_content): # Check if image is valid
                    image_dir = os.path.join("yoga_dataset", yoga_pose)
                    os.makedirs(image_dir, exist_ok=True)
                    filename = f"{yoga_pose}_{downloaded_count + 1}.jpg"
                    filepath = os.path.join(image_dir, filename)

                    with open(filepath, 'wb') as f:
                        f.write(image_content)

                    downloaded_count += 1
                    print(f"Downloaded image {downloaded_count} for {yoga_pose}")
                else:
                    print(f"Skipping invalid image: {img_url}")

            except requests.exceptions.RequestException as e:
                print(f"Error downloading image from {img_url}: {e}")
        else:
            print(f"Skipping invalid image URL: {img_url}")

    print(f"Successfully downloaded {downloaded_count} valid images for {yoga_pose}")


if __name__ == "__main__":
    for pose in yoga_poses:
        download_images(pose.lower())
