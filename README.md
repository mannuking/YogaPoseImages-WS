# Yoga Pose Image Dataset Scraper

This project creates a dataset of yoga pose images by scraping Google Images. The dataset can be used to train an AI model for yoga pose detection and correction.

## Project Structure

-   `scrape_script.py`: Python script to scrape images from Google Images.
-   `Image_Preprocessing.py`: Python script to preprocess the downloaded images (resize, convert to JPEG).
-   `verify_Dataset.py`: Python script to verify the integrity of the downloaded images.
-   `requirements.txt`: List of required Python packages.
-   `yoga_dataset/`: Directory where the scraped images will be saved (created by `scrape_script.py`).
-   `processed_test_images/`: Directory where processed images will be saved (created by `Image_Preprocessing.py`).

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a virtual environment:**

    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the virtual environment:**

    *   **macOS/Linux:**

        ```bash
        source .venv/bin/activate
        ```

    *   **Windows:**

        ```bash
        .venv\Scripts\activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Download ChromeDriver:**

    *   Download the appropriate ChromeDriver version for your Chrome browser from [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads).
    *   Place the `chromedriver` executable in the project directory or in a location that is in your system's PATH. If you place it somewhere else, update the `CHROME_DRIVER_PATH` variable in `scrape_script.py`.

## Usage

1.  **Scrape Images:**

    ```bash
    python scrape_script.py
    ```

    This will create the `yoga_dataset` directory and download images of 10 yoga poses into subdirectories named after each pose.

2.  **Preprocess Images:**

    ```bash
    python Image_Preprocessing.py yoga_dataset processed_test_images
    ```

    This will resize the images to 224x224 pixels, convert them to JPEG format, and save them in the `processed_test_images` directory.

3.  **Verify Dataset:**

    ```bash
    python verify_Dataset.py
    ```

    This will check the integrity of the images in the `processed_test_images` directory and report any corrupted files.

4.  **Optional: Zip the Dataset:**

    To create a zip archive of the processed dataset:

    *   **macOS/Linux:**

        ```bash
        zip -r yoga_pose_images.zip processed_test_images
        ```

    *   **Windows (PowerShell):**

        ```powershell
        Compress-Archive -Path processed_test_images -DestinationPath yoga_pose_images.zip
        ```

## Advanced Dataset Filtering

The project now includes an advanced filtering script to clean the dataset and ensure high-quality training data:

```bash
python filter_dataset.py yoga_dataset cleaned_dataset
```

This script applies multiple filters to ensure the dataset only contains:

1. **Real human subjects** - Uses face detection and body analysis to filter out illustrations and animations
2. **Appropriate image sizes** - Ensures images are within the specified size range
3. **Clean backgrounds** - Analyzes background complexity to filter out cluttered images
4. **Accurate yoga poses** - Uses a classification model to verify the pose matches the expected category

### Filtering Parameters

The filtering parameters can be adjusted in the `filter_dataset.py` script:

* `MIN_IMAGE_SIZE` and `MAX_IMAGE_SIZE`: Acceptable image dimensions
* `MIN_ASPECT_RATIO` and `MAX_ASPECT_RATIO`: Acceptable aspect ratios
* `BACKGROUND_COMPLEXITY_THRESHOLD`: Threshold for background cleanliness
* `HUMAN_CONFIDENCE_THRESHOLD`: Confidence threshold for human detection
* `POSE_CONFIDENCE_THRESHOLD`: Confidence threshold for pose classification

### Filtering Process

The filtering process includes:

1. **Size and aspect ratio validation** - Ensures images have appropriate dimensions
2. **Human subject detection** - Uses face recognition and body analysis to detect real humans
3. **Illustration/animation detection** - Analyzes edge patterns and color distribution
4. **Background cleanliness assessment** - Evaluates background complexity
5. **Pose classification** - Verifies the pose matches the expected category

The script generates a detailed log file (`dataset_filtering.log`) with information about each filtered image.

## Visualizing Filtering Results

To better understand the filtering process and its results, you can use the visualization script:

```bash
python visualize_filtering.py yoga_dataset cleaned_dataset
```

This script generates three visualization files:

1. **filtering_visualization.png** - Shows sample images that passed and failed the filtering process
2. **filtering_stats.png** - A pie chart showing the percentage of images that passed vs. filtered out
3. **failure_reasons.png** - A bar chart showing the distribution of reasons why images were filtered out

These visualizations can help you understand the filtering process and fine-tune the parameters if needed.

### Visualization Options

You can customize the number of sample images shown in the visualization:

```bash
python visualize_filtering.py yoga_dataset cleaned_dataset --samples 10
```

## Troubleshooting

*   **`WebDriverException: 'chromedriver' executable needs to be in PATH.`:** Make sure you have downloaded ChromeDriver and placed it in the correct location (project directory or a directory in your PATH). Update the `CHROME_DRIVER_PATH` in `scrape_script.py` if necessary.
*   **`requests.exceptions.ConnectionError` or `requests.exceptions.Timeout`:** Check your internet connection. These errors can occur due to network issues.
*   **No images downloaded:** The structure of Google Images might have changed. You may need to update the CSS selectors in `scrape_script.py` (e.g., `img.rg_i`, `.mye4qd`). Use your browser's developer tools to inspect the Google Images page and find the correct selectors.
*   **`ModuleNotFoundError: No module named '...'`:** Make sure you have activated your virtual environment and installed the required packages using `pip install -r requirements.txt`.
*   **TensorFlow/OpenCV errors:** If you encounter errors with TensorFlow or OpenCV, ensure you have the correct versions installed and that your Python environment is properly configured.

## Notes

*   The scraping script uses Selenium with ChromeDriver in headless mode.
*   The number of images downloaded per pose can be adjusted in `scrape_script.py` (default is 100).
*   The image preprocessing script resizes images to 224x224 and converts them to JPEG with a quality of 90. You can change these parameters in `Image_Preprocessing.py`.
*   The `verify_Dataset.py` script performs a basic integrity check on the images.
*   The `filter_dataset.py` script performs advanced filtering to ensure high-quality training data.
*   This project is intended for educational and personal use. Be mindful of Google Images' terms of service when scraping.
