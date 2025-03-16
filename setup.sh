#!/bin/bash

echo "Yoga Pose Image Scraper Setup"
echo "==========================="
echo

echo "Step 1: Installing required packages..."
pip install -r requirements.txt
echo

echo "Step 2: Checking for ChromeDriver..."
cd yoga_scraper
python -c "from run_scraper import check_chromedriver; print('ChromeDriver available:', check_chromedriver())"
cd ..
echo

echo "Step 3: If ChromeDriver is not available, download it now..."
echo
read -p "Do you want to download ChromeDriver now? (y/n): " download_driver

if [ "$download_driver" = "y" ] || [ "$download_driver" = "Y" ]; then
    echo "Downloading ChromeDriver..."
    cd yoga_scraper
    python download_chromedriver.py
    cd ..
    echo
fi

echo "Setup completed!"
echo
echo "You can now run the scraper using:"
echo "  - python yoga_scraper/run_scraper.py: To run just the scraper"
echo "  - python run_pipeline.py: To run the entire pipeline"
echo
echo "If you encounter any issues with ChromeDriver, run:"
echo "  - python yoga_scraper/download_chromedriver.py: To download ChromeDriver manually"
echo

read -p "Press Enter to continue..." 
