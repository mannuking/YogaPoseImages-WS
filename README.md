# Yoga Pose Image Dataset Scraper

This project creates a dataset of yoga pose images by scraping Google Images using Scrapy and Selenium. The dataset can be used to train an AI model for yoga pose detection and correction.

## Project Structure

- `yoga_scraper/`: Scrapy project directory
  - `yoga_scraper/spiders/`: Directory containing Scrapy spiders
    - `yoga_pose_spider.py`: Basic Scrapy spider for scraping yoga pose images
    - `selenium_yoga_spider.py`: Advanced Scrapy spider using Selenium for better image extraction
  - `yoga_scraper/items.py`: Definition of the YogaPoseImage item
  - `yoga_scraper/pipelines.py`: Custom image pipeline for processing and storing images
  - `yoga_scraper/settings.py`: Scrapy project settings
- `run_scraper.py`: Script to run the Scrapy spider
- `preprocess_images.py`: Script to preprocess the downloaded images
- `verify_dataset.py`: Script to verify the integrity of the dataset
- `main.py`: Main script to run the entire pipeline
- `requirements.txt`: List of required Python packages
- `yoga_dataset/`: Directory where the scraped images will be saved
- `processed_images/`: Directory where processed images will be saved

## Yoga Poses

The scraper is configured to download images for the following yoga poses:

1. Tadasana (Mountain Pose) - ताड़ासन
2. Trikonasana (Triangle Pose) - त्रिकोणासन
3. Durvasana (Durva Grass Pose) - दुर्वासन
4. Ardha Chandrasana (Half Moon Pose) - अर्धचंद्रासन
5. Ustrasana (Camel Pose) - उष्ट्रासन
6. Dhanurasana (Bow Pose) - धनुरासन
7. Bhujangasana (Cobra Pose) - भुजंगासन
8. Vrksasana (Tree Pose) - वृक्षासन
9. Halasana (Plow Pose) - हलासन
10. Setu Bandhasana (Bridge Pose) - सेतुबंधासन
11. Akarna Dhanurasana (Shooting Bow Pose) - आकर्ण धनुरासन
12. Gomukhasana (Cow Face Pose) - गोमुखासन

## Setup

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - **Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Install Chrome and ChromeDriver:**

   - Download and install Chrome browser if you don't have it already
   - The script will automatically download the appropriate ChromeDriver version using webdriver-manager

## Usage

### Running the Entire Pipeline

To run the entire pipeline (scraping, preprocessing, verification, and visualization):

```bash
cd yoga_scraper
python main.py
```

### Running Individual Steps

You can also run individual steps of the pipeline:

1. **Scrape Images:**

   ```bash
   python main.py --scrape
   ```

   This will create the `yoga_dataset` directory and download images of yoga poses into subdirectories.

2. **Preprocess Images:**

   ```bash
   python main.py --preprocess
   ```

   This will resize the images to 224x224 pixels, convert them to JPEG format, and save them in the `processed_images` directory.

3. **Verify Dataset:**

   ```bash
   python main.py --verify
   ```

   This will check the integrity of the images in the `processed_images` directory and report any corrupted files.

4. **Visualize Dataset:**

   ```bash
   python main.py --visualize
   ```

   This will create a visualization of the dataset, showing random samples from each yoga pose.

### Advanced Options

You can customize the pipeline with additional command-line options:

```bash
python main.py --input-dir yoga_dataset --output-dir processed_images --target-width 224 --target-height 224 --quality 90 --num-workers 4
```

Run `python main.py --help` to see all available options.

## Troubleshooting

- **Selenium WebDriver issues:** If you encounter issues with Selenium, make sure you have Chrome installed and that the webdriver-manager package is correctly installed.
- **Network errors:** If you experience network errors during scraping, try increasing the `DOWNLOAD_DELAY` in `yoga_scraper/yoga_scraper/settings.py`.
- **Image processing errors:** If you encounter errors during image preprocessing, check that the Pillow package is correctly installed and that the input images are valid.
- **Google blocking requests:** Google may block requests if too many are made in a short period. Try increasing the `DOWNLOAD_DELAY` and using a different user agent.

## Notes

- The scraper is configured to download between 200 and 500 images per yoga pose.
- The image preprocessing script resizes images to 224x224 pixels and converts them to JPEG with a quality of 90.
- The verification script checks the integrity of the images and reports any corrupted files.
- The visualization script creates a visual representation of the dataset, showing random samples from each yoga pose.
- This project is intended for educational and personal use. Be mindful of Google Images' terms of service when scraping.
