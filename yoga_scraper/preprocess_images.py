import os
import sys
import logging
import multiprocessing
from PIL import Image, ImageOps
import numpy as np
from concurrent.futures import ProcessPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("preprocessing.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def is_valid_image(image_path):
    """Check if an image is valid and meets quality criteria."""
    try:
        with Image.open(image_path) as img:
            # Check if the image is too small
            if img.width < 100 or img.height < 100:
                return False
            
            # Check if the image is too large
            if img.width > 4000 or img.height > 4000:
                return False
            
            # Check if the aspect ratio is too extreme
            aspect_ratio = img.width / img.height
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                return False
            
            # Check if the image is mostly a single color (likely a placeholder)
            if img.mode == 'RGB':
                img_array = np.array(img)
                std_r = np.std(img_array[:, :, 0])
                std_g = np.std(img_array[:, :, 1])
                std_b = np.std(img_array[:, :, 2])
                if std_r < 10 and std_g < 10 and std_b < 10:
                    return False
            
            return True
    except Exception as e:
        logging.warning(f"Error validating image {image_path}: {e}")
        return False

def process_image(args):
    """Process a single image."""
    input_path, output_dir, target_size, quality = args
    
    # Skip if the image is not valid
    if not is_valid_image(input_path):
        logging.info(f"Skipping invalid image: {input_path}")
        return False
    
    try:
        # Get the relative path components
        rel_path = os.path.relpath(input_path, "yoga_dataset")
        pose_dir = os.path.dirname(rel_path)
        filename = os.path.basename(input_path)
        
        # Create the output directory
        output_pose_dir = os.path.join(output_dir, pose_dir)
        os.makedirs(output_pose_dir, exist_ok=True)
        
        # Create the output path
        output_path = os.path.join(output_pose_dir, os.path.splitext(filename)[0] + '.jpg')
        
        # Open and process the image
        with Image.open(input_path) as img:
            # Convert to RGB mode (in case it's RGBA or other mode)
            img = img.convert('RGB')
            
            # Resize the image while maintaining aspect ratio
            img = ImageOps.contain(img, target_size)
            
            # Create a new image with the target size and paste the resized image in the center
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            paste_x = (target_size[0] - img.width) // 2
            paste_y = (target_size[1] - img.height) // 2
            new_img.paste(img, (paste_x, paste_y))
            
            # Save the processed image
            new_img.save(output_path, 'JPEG', quality=quality)
            
            logging.info(f"Processed: {input_path} -> {output_path}")
            return True
    
    except Exception as e:
        logging.error(f"Error processing image {input_path}: {e}")
        return False

def preprocess_images(input_dir="yoga_dataset", output_dir="processed_images", 
                     target_size=(224, 224), quality=90, num_workers=None):
    """Preprocess all images in the input directory."""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the number of workers
    if num_workers is None:
        num_workers = max(1, multiprocessing.cpu_count() - 1)
    
    # Find all image files
    image_paths = []
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                image_paths.append(os.path.join(root, filename))
    
    logging.info(f"Found {len(image_paths)} images to process")
    
    # Process images in parallel
    args_list = [(path, output_dir, target_size, quality) for path in image_paths]
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_image, args_list))
    
    # Count successful and failed processing
    successful = results.count(True)
    failed = results.count(False)
    
    logging.info(f"Preprocessing completed: {successful} images processed successfully, {failed} failed")

if __name__ == "__main__":
    # Parse command-line arguments
    input_dir = "yoga_dataset"
    output_dir = "processed_images"
    
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Preprocess images
    preprocess_images(input_dir, output_dir) 
