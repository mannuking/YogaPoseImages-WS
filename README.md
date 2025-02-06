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

## Troubleshooting

*   **`WebDriverException: 'chromedriver' executable needs to be in PATH.`:** Make sure you have downloaded ChromeDriver and placed it in the correct location (project directory or a directory in your PATH). Update the `CHROME_DRIVER_PATH` in `scrape_script.py` if necessary.
*   **`requests.exceptions.ConnectionError` or `requests.exceptions.Timeout`:** Check your internet connection. These errors can occur due to network issues.
*   **No images downloaded:** The structure of Google Images might have changed. You may need to update the CSS selectors in `scrape_script.py` (e.g., `img.rg_i`, `.mye4qd`). Use your browser's developer tools to inspect the Google Images page and find the correct selectors.
*   **`ModuleNotFoundError: No module named '...'`:** Make sure you have activated your virtual environment and installed the required packages using `pip install -r requirements.txt`.

## Notes

*   The scraping script uses Selenium with ChromeDriver in headless mode.
*   The number of images downloaded per pose can be adjusted in `scrape_script.py` (default is 100).
*   The image preprocessing script resizes images to 224x224 and converts them to JPEG with a quality of 90. You can change these parameters in `Image_Preprocessing.py`.
*   The `verify_Dataset.py` script performs a basic integrity check on the images.
*   This project is intended for educational and personal use. Be mindful of Google Images' terms of service when scraping.
