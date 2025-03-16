import os
import sys
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("yoga_pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_command(command, cwd=None):
    """Run a command and log the output."""
    logging.info(f"Running command: {command}")
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=cwd,
            universal_newlines=True
        )
        
        # Stream the output in real-time
        for line in process.stdout:
            line = line.strip()
            if line:
                logging.info(line)
        
        # Wait for the process to complete
        process.wait()
        
        # Check if the process was successful
        if process.returncode != 0:
            # Get the error output
            error_output = process.stderr.read()
            logging.error(f"Command failed with return code {process.returncode}")
            logging.error(f"Error output: {error_output}")
            return False
        
        return True
    
    except Exception as e:
        logging.error(f"Error running command: {e}")
        return False

def main():
    """Run the entire yoga pose image dataset pipeline."""
    start_time = time.time()
    logging.info("Starting the yoga pose image dataset pipeline...")
    
    # Create the yoga_dataset directory if it doesn't exist
    os.makedirs("yoga_dataset", exist_ok=True)
    
    # Create the processed_images directory if it doesn't exist
    os.makedirs("processed_images", exist_ok=True)
    
    # Run the scraper
    logging.info("Step 1: Running the scraper...")
    if not run_command("python main.py --scrape", cwd="yoga_scraper"):
        logging.error("Scraper failed. Exiting.")
        return
    
    # Preprocess the images
    logging.info("Step 2: Preprocessing the images...")
    if not run_command("python main.py --preprocess", cwd="yoga_scraper"):
        logging.error("Preprocessing failed. Exiting.")
        return
    
    # Verify the dataset
    logging.info("Step 3: Verifying the dataset...")
    if not run_command("python main.py --verify", cwd="yoga_scraper"):
        logging.error("Verification failed. Exiting.")
        return
    
    # Visualize the dataset
    logging.info("Step 4: Visualizing the dataset...")
    if not run_command("python main.py --visualize", cwd="yoga_scraper"):
        logging.error("Visualization failed. Exiting.")
        return
    
    # Display the images
    logging.info("Step 5: Displaying the images...")
    if not run_command("python display_images.py", cwd="yoga_scraper"):
        logging.error("Display failed. Exiting.")
        return
    
    # Calculate the total time
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Pipeline completed successfully in {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")

if __name__ == "__main__":
    main() 
