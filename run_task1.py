#!/usr/bin/env python3
"""
Simplified runner for HanuAI Task 1
Run this file to execute the complete web scraping and sentiment analysis
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        # If requirements.txt doesn't exist, install individually
        packages = [
            "selenium", "webdriver-manager", "beautifulsoup4", 
            "pandas", "textblob", "python-dateutil", "lxml", 
            "requests", "fake-useragent"
        ]
        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except:
                print(f"Failed to install {package}")

def main():
    """Main runner function"""
    print("🚀 HanuAI Task 1 - Web Scraping & Sentiment Analysis")
    print("=" * 60)
    
    # Check if requirements are installed
    try:
        import selenium
        import textblob
        import pandas
        print("✓ All required packages are installed")
    except ImportError as e:
        print(f"Missing packages: {e}")
        print("Installing required packages...")
        install_requirements()
    
    # Download TextBlob corpora if needed
    try:
        from textblob import TextBlob
        # Test if corpora is downloaded
        test_blob = TextBlob("test")
        print("✓ TextBlob corpora are available")
    except:
        print("Downloading TextBlob corpora...")
        try:
            subprocess.check_call([sys.executable, "-m", "textblob.download_corpora"])
        except:
            print("Warning: Could not download TextBlob corpora")
    
    # Run the main script
    print("\nStarting web scraping and sentiment analysis...")
    try:
        from web_scraping_sentiment import main as task_main
        task_main()
    except Exception as e:
        print(f"Error running main script: {e}")
        print("Please check the error above and fix any issues.")

if __name__ == "__main__":
    main()