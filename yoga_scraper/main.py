import os
import sys
import time
import logging
import argparse
from run_scraper import run_scraper
from preprocess_images import preprocess_images
from verify_dataset import verify_dataset, count_images_by_pose, visualize_dataset

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("yoga_dataset_pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Yoga Pose Image Dataset Pipeline")
    
    parser.add_argument("--scrape", action="store_true", help="Run the scraper")
    parser.add_argument("--preprocess", action="store_true", help="Preprocess the images")
    parser.add_argument("--verify", action="store_true", help="Verify the dataset")
    parser.add_argument("--visualize", action="store_true", help="Visualize the dataset")
    
    parser.add_argument("--input-dir", default="yoga_dataset", help="Input directory for preprocessing")
    parser.add_argument("--output-dir", default="processed_images", help="Output directory for preprocessing")
    
    parser.add_argument("--target-width", type=int, default=224, help="Target image width")
    parser.add_argument("--target-height", type=int, default=224, help="Target image height")
    parser.add_argument("--quality", type=int, default=90, help="JPEG quality (0-100)")
    
    parser.add_argument("--num-workers", type=int, default=None, help="Number of worker processes")
    
    return parser.parse_args()

def main():
    """Run the yoga pose image dataset pipeline."""
    args = parse_arguments()
    
    # If no actions are specified, run the entire pipeline
    if not (args.scrape or args.preprocess or args.verify or args.visualize):
        args.scrape = True
        args.preprocess = True
        args.verify = True
        args.visualize = True
    
    # Run the scraper
    if args.scrape:
        logging.info("Starting the scraper...")
        start_time = time.time()
        run_scraper()
        elapsed_time = time.time() - start_time
        logging.info(f"Scraping completed in {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    
    # Preprocess the images
    if args.preprocess:
        logging.info("Starting image preprocessing...")
        start_time = time.time()
        preprocess_images(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            target_size=(args.target_width, args.target_height),
            quality=args.quality,
            num_workers=args.num_workers
        )
        elapsed_time = time.time() - start_time
        logging.info(f"Preprocessing completed in {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    
    # Verify the dataset
    if args.verify:
        logging.info("Verifying the dataset...")
        start_time = time.time()
        valid_images, invalid_images = verify_dataset(args.output_dir, num_workers=args.num_workers)
        elapsed_time = time.time() - start_time
        logging.info(f"Verification completed in {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        
        # Count images by pose
        pose_counts = count_images_by_pose(args.output_dir)
        
        # Print the counts
        print("\nImage counts by pose:")
        for pose, count in sorted(pose_counts.items()):
            print(f"  {pose}: {count} images")
    
    # Visualize the dataset
    if args.visualize:
        logging.info("Visualizing the dataset...")
        start_time = time.time()
        visualize_dataset(args.output_dir)
        elapsed_time = time.time() - start_time
        logging.info(f"Visualization completed in {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    
    logging.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main() 
