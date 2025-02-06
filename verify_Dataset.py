import os
from PIL import Image
import sys
import multiprocessing

def verify_image(filepath):
    """Verifies a single image and returns its validity."""
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True, filepath  # Valid image
    except (IOError, OSError, ValueError) as e:
        return False, filepath  # Corrupted image


def verify_images(directory, num_processes=multiprocessing.cpu_count()):
    """
    Verifies the integrity of images in a directory using multiprocessing.

    Args:
        directory: The path to the directory containing images.
        num_processes: Number of parallel processes to use (defaults to CPU count).

    Returns:
        A tuple: (total_images, valid_images, corrupted_images, corrupted_image_paths)
    """
    image_paths = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                image_paths.append(os.path.join(root, filename))

    total_images = len(image_paths)
    valid_images = 0
    corrupted_images = 0
    corrupted_image_paths = []

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(verify_image, image_paths)

    for is_valid, filepath in results:
        if is_valid:
            valid_images += 1
        else:
            corrupted_images += 1
            corrupted_image_paths.append(filepath)
            print(f"Corrupted image: {filepath}") # print immediately when corrupted image is found

    return total_images, valid_images, corrupted_images, corrupted_image_paths


if __name__ == "__main__":
    directory_to_verify = "yoga_dataset"  # Directory to verify
    total, valid, corrupted, corrupted_paths = verify_images(directory_to_verify)

    print(f"\nTotal images: {total}")
    print(f"Valid images: {valid}")
    print(f"Corrupted images: {corrupted}")

    if corrupted > 0:
        print("\nCorrupted image paths:")
        for path in corrupted_paths:
            print(path)
