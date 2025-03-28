import os
import sys
import zipfile
import platform
import requests
import subprocess
from io import BytesIO

def get_chrome_version():
    """Get the installed Chrome version."""
    system = platform.system()
    
    try:
        if system == "Windows":
            # Try using the registry
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        elif system == "Darwin":  # macOS
            process = subprocess.Popen(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                stdout=subprocess.PIPE
            )
            version = process.communicate()[0].decode("UTF-8").replace("Google Chrome ", "").strip()
            return version
        elif system == "Linux":
            process = subprocess.Popen(
                ["google-chrome", "--version"],
                stdout=subprocess.PIPE
            )
            version = process.communicate()[0].decode("UTF-8").replace("Google Chrome ", "").strip()
            return version
    except Exception as e:
        print(f"Error detecting Chrome version: {e}")
    
    # If automatic detection fails, ask the user
    print("Could not automatically detect Chrome version.")
    version = input("Please enter your Chrome version (e.g., 114.0.5735.90): ")
    return version

def get_chromedriver_url(chrome_version):
    """Get the ChromeDriver download URL for the given Chrome version."""
    # Extract major version
    major_version = chrome_version.split(".")[0]
    
    # Determine the platform
    system = platform.system()
    if system == "Windows":
        platform_name = "win32"
    elif system == "Darwin":  # macOS
        if platform.machine() == "arm64":  # Apple Silicon
            platform_name = "mac_arm64"
        else:
            platform_name = "mac64"
    elif system == "Linux":
        if platform.machine() == "aarch64":  # ARM64
            platform_name = "linux64_arm"
        else:
            platform_name = "linux64"
    else:
        raise Exception(f"Unsupported platform: {system}")
    
    # For Chrome version 115 and above, use the new URL format
    if int(major_version) >= 115:
        # Get the latest ChromeDriver version for this Chrome version
        response = requests.get(f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}")
        chromedriver_version = response.text.strip()
        
        # Construct the download URL
        url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{platform_name}.zip"
    else:
        # For older Chrome versions, use the legacy URL format
        response = requests.get(f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}")
        chromedriver_version = response.text.strip()
        
        # Construct the download URL
        url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{platform_name}.zip"
    
    return url

def download_chromedriver(url):
    """Download ChromeDriver from the given URL."""
    print(f"Downloading ChromeDriver from: {url}")
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download ChromeDriver: {response.status_code}")
    
    # Extract the ZIP file
    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        # Extract all files
        zip_file.extractall()
    
    # Make the ChromeDriver executable on Unix-like systems
    system = platform.system()
    if system != "Windows":
        os.chmod("chromedriver", 0o755)
    
    print("ChromeDriver downloaded successfully.")
    
    # Get the full path to the ChromeDriver executable
    chromedriver_path = os.path.abspath("chromedriver.exe" if system == "Windows" else "chromedriver")
    print(f"ChromeDriver path: {chromedriver_path}")
    
    return chromedriver_path

def main():
    """Main function."""
    try:
        # Get the installed Chrome version
        chrome_version = get_chrome_version()
        print(f"Detected Chrome version: {chrome_version}")
        
        # Get the ChromeDriver download URL
        url = get_chromedriver_url(chrome_version)
        
        # Download ChromeDriver
        chromedriver_path = download_chromedriver(url)
        
        print("\nTo use this ChromeDriver with the yoga pose scraper:")
        print(f"1. Set the CHROMEDRIVER_PATH environment variable to: {chromedriver_path}")
        print("   - Windows: set CHROMEDRIVER_PATH=" + chromedriver_path)
        print("   - macOS/Linux: export CHROMEDRIVER_PATH=" + chromedriver_path)
        print("2. Or move the ChromeDriver executable to the yoga_scraper directory")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
