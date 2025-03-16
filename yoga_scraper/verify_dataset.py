import os
import sys
import logging
import multiprocessing
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
import numpy as np
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("verification.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def verify_image(image_path):
    """Verify that an image is valid and can be opened."""
    try:
        with Image.open(image_path) as img:
            img.verify()  # Verify that the image is valid
            return True, image_path
    except Exception as e:
        return False, image_path

def verify_dataset(dataset_dir, num_workers=None):
    """Verify all images in the dataset."""
    # Get the number of workers
    if num_workers is None:
        num_workers = max(1, multiprocessing.cpu_count() - 1)
    
    # Find all image files
    image_paths = []
    for root, _, files in os.walk(dataset_dir):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                image_paths.append(os.path.join(root, filename))
    
    logging.info(f"Found {len(image_paths)} images to verify")
    
    # Verify images in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(verify_image, image_paths))
    
    # Count valid and invalid images
    valid_images = [path for valid, path in results if valid]
    invalid_images = [path for valid, path in results if not valid]
    
    logging.info(f"Verification completed: {len(valid_images)} valid images, {len(invalid_images)} invalid images")
    
    # Log invalid images
    if invalid_images:
        logging.warning("Invalid images:")
        for path in invalid_images:
            logging.warning(f"  {path}")
    
    return valid_images, invalid_images

def count_images_by_pose(dataset_dir):
    """Count the number of images for each yoga pose."""
    pose_counts = {}
    
    for root, _, files in os.walk(dataset_dir):
        pose_dir = os.path.basename(root)
        if pose_dir not in pose_counts:
            pose_counts[pose_dir] = 0
        
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                pose_counts[pose_dir] += 1
    
    # Remove entries with zero images
    pose_counts = {pose: count for pose, count in pose_counts.items() if count > 0}
    
    return pose_counts

def visualize_dataset(dataset_dir, num_samples=3):
    """Visualize random samples from each yoga pose."""
    # Get all subdirectories (yoga poses)
    pose_dirs = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
    
    # Create a figure with subplots
    num_poses = len(pose_dirs)
    fig, axes = plt.subplots(num_poses, num_samples, figsize=(15, 3 * num_poses))
    
    # If there's only one pose, make sure axes is 2D
    if num_poses == 1:
        axes = np.array([axes])
    
    # Iterate over each pose
    for i, pose_dir in enumerate(pose_dirs):
        pose_path = os.path.join(dataset_dir, pose_dir)
        
        # Get all image files for this pose
        image_files = [f for f in os.listdir(pose_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # If there are fewer images than num_samples, use all of them
        num_to_sample = min(num_samples, len(image_files))
        
        # Sample random images
        sampled_images = random.sample(image_files, num_to_sample)
        
        # Display each sampled image
        for j, image_file in enumerate(sampled_images):
            image_path = os.path.join(pose_path, image_file)
            
            try:
                img = Image.open(image_path)
                axes[i, j].imshow(img)
                axes[i, j].set_title(f"{pose_dir}\n{j+1}/{num_to_sample}")
                axes[i, j].axis('off')
            except Exception as e:
                axes[i, j].text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center')
                axes[i, j].axis('off')
        
        # If there are fewer images than num_samples, hide the remaining axes
        for j in range(num_to_sample, num_samples):
            axes[i, j].axis('off')
    
    plt.tight_layout()
    plt.savefig('dataset_visualization.png')
    logging.info("Dataset visualization saved to dataset_visualization.png")

if __name__ == "__main__":
    # Parse command-line arguments
    dataset_dir = "processed_images"
    
    if len(sys.argv) > 1:
        dataset_dir = sys.argv[1]
    
    # Verify the dataset
    valid_images, invalid_images = verify_dataset(dataset_dir)
    
    # Count images by pose
    pose_counts = count_images_by_pose(dataset_dir)
    
    # Print the counts
    print("\nImage counts by pose:")
    for pose, count in sorted(pose_counts.items()):
        print(f"  {pose}: {count} images")
    
    # Visualize the dataset
    visualize_dataset(dataset_dir) 
