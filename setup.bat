@echo off
echo Yoga Pose Image Scraper Setup
echo ===========================
echo.

echo Step 1: Installing required packages...
pip install -r requirements.txt
echo.

echo Step 2: Checking for ChromeDriver...
cd yoga_scraper
python -c "from run_scraper import check_chromedriver; print('ChromeDriver available:', check_chromedriver())"
cd ..
echo.

echo Step 3: If ChromeDriver is not available, download it now...
echo.
set /p download_driver=Do you want to download ChromeDriver now? (y/n): 

if /i "%download_driver%"=="y" (
    echo Downloading ChromeDriver...
    cd yoga_scraper
    python download_chromedriver.py
    cd ..
    echo.
)

echo Setup completed!
echo.
echo You can now run the scraper using:
echo   - run_scraper.bat: To run just the scraper
echo   - run_pipeline.bat: To run the entire pipeline
echo.
echo If you encounter any issues with ChromeDriver, run:
echo   - download_chromedriver.bat: To download ChromeDriver manually
echo.
pause 
