@echo off
echo Checking for ChromeDriver...
cd yoga_scraper
python -c "from run_scraper import check_chromedriver; print('ChromeDriver available:', check_chromedriver())"
echo.
echo If ChromeDriver is not available, run download_chromedriver.bat to download it.
pause 
