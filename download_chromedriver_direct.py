import os
import sys
import zipfile
import platform
import requests
from io import BytesIO

def main():
    """Download ChromeDriver directly for Chrome 134."""
    try:
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
            print(f"Unsupported platform: {system}")
            return 1
        
        # Use the latest stable version from Chrome for Testing
        print("Getting latest stable ChromeDriver version...")
        response = requests.get("https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE")
        if response.status_code == 200:
            latest_version = response.text.strip()
            print(f"Latest stable version: {latest_version}")
            url = f"https://storage.googleapis.com/chrome-for-testing-public/{latest_version}/{platform_name}/chromedriver-{platform_name}.zip"
        else:
            print("Failed to get latest stable version, using fallback version")
            url = f"https://storage.googleapis.com/chrome-for-testing-public/114.0.5735.90/{platform_name}/chromedriver-{platform_name}.zip"
        
        print(f"Downloading ChromeDriver from: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to download ChromeDriver: {response.status_code}")
            return 1
        
        # Create a directory for ChromeDriver if it doesn't exist
        os.makedirs("chromedriver", exist_ok=True)
        
        # Extract the ZIP file
        with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
            # List all files in the ZIP
            file_list = zip_file.namelist()
            print(f"Files in ZIP: {file_list}")
            
            # Extract only the chromedriver executable
            for file in file_list:
                if "chromedriver" in file.lower() and file.endswith(".exe" if system == "Windows" else ""):
                    print(f"Extracting: {file}")
                    # Extract the file with a new name
                    source = zip_file.open(file)
                    target_path = os.path.join("chromedriver", "chromedriver.exe" if system == "Windows" else "chromedriver")
                    
                    with open(target_path, "wb") as target:
                        target.write(source.read())
                    
                    # Make the file executable on Unix-like systems
                    if system != "Windows":
                        os.chmod(target_path, 0o755)
                    
                    break
        
        # Get the full path to the ChromeDriver executable
        chromedriver_path = os.path.abspath(os.path.join("chromedriver", "chromedriver.exe" if system == "Windows" else "chromedriver"))
        
        print("ChromeDriver downloaded successfully.")
        print(f"ChromeDriver path: {chromedriver_path}")
        
        print("\nTo use this ChromeDriver with the yoga pose scraper:")
        print(f"1. Set the CHROMEDRIVER_PATH environment variable to: {chromedriver_path}")
        print(f"   - Windows: set CHROMEDRIVER_PATH={chromedriver_path}")
        print(f"   - macOS/Linux: export CHROMEDRIVER_PATH={chromedriver_path}")
        print("2. Or move the ChromeDriver executable to the yoga_scraper directory")
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
