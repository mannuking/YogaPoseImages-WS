import os
import sys
from PIL import Image
import multiprocessing

def process_image(input_path, output_dir, target_size, quality, min_size, max_size, min_aspect_ratio, max_aspect_ratio):
    """Processes a single image, including size and aspect ratio checks."""
    relative_path = os.path.relpath(input_path, os.path.dirname(input_path))
    output_path = os.path.join(output_dir, os.path.dirname(relative_path), os.path.splitext(os.path.basename(input_path))[0] + '.jpg')

    # Create necessary subdirectories in output_dir
    output_subdir = os.path.dirname(output_path)
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir, exist_ok=True)

    try:
        with Image.open(input_path) as img:
            width, height = img.size

            # Check image size
            if width < min_size or height < min_size:
                print(f"Skipping {input_path}: Image too small ({width}x{height})")
                return
            if width > max_size or height > max_size:
                print(f"Skipping {input_path}: Image too large ({width}x{height})")
                return

            # Check aspect ratio
            aspect_ratio = width / height
            if aspect_ratio < min_aspect_ratio:
                print(f"Skipping {input_path}: Aspect ratio too small ({aspect_ratio:.2f})")
                return
            if aspect_ratio > max_aspect_ratio:
                print(f"Skipping {input_path}: Aspect ratio too large ({aspect_ratio:.2f})")
                return

            # If all checks pass, proceed with processing
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=quality)
            print(f"Processed: {input_path} -> {output_path}")

    except (IOError, OSError) as e:
        print(f"Error processing {input_path}: {e}", file=sys.stderr)


def preprocess_images(input_dir, output_dir, target_size=(224, 224), quality=90,
                      min_size=50, max_size=5000, min_aspect_ratio=0.5, max_aspect_ratio=2.0,
                      num_processes=multiprocessing.cpu_count()):
    """
    Preprocesses images with size and aspect ratio filtering.

    Args:
        input_dir: Path to the input directory.
        output_dir: Path to the output directory.
        target_size: Target image size (width, height).
        quality: JPEG quality.
        min_size: Minimum image dimension (width or height).
        max_size: Maximum image dimension (width or height).
        min_aspect_ratio: Minimum aspect ratio (width / height).
        max_aspect_ratio: Maximum aspect ratio (width / height).
        num_processes: Number of processes to use.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_paths = []
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                image_paths.append(os.path.join(root, filename))

    with multiprocessing.Pool(processes=num_processes) as pool:
        processes = [(path, output_dir, target_size, quality, min_size, max_size, min_aspect_ratio, max_aspect_ratio)
                     for path in image_paths]
        pool.starmap(process_image, processes)

    print("Image preprocessing complete.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python image_preprocessing.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.isdir(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    preprocess_images(input_directory, output_directory)
    print("Image preprocessing with multiprocessing complete.")
