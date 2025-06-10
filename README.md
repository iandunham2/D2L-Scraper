# Brightspace Discussion Scraper

This script automates the collection of discussion posts from a Brightspace course shell using Selenium WebDriver.

## Setup

1. Install Python 3.8 or higher
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Copy `brightspace_scraper.py` to a new file and replace the placeholder values:
   - Replace `YOUR_USERNAME` with your Brightspace username
   - Replace `YOUR_PASSWORD` with your Brightspace password
   - Replace `YOUR_COURSE_URL` with the URL of your course shell

2. Run the script:
   ```
   python brightspace_scraper.py
   ```

## Output

The script will create a CSV file containing:
- Thread Title
- Thread Author
- Thread Date
- Post Author
- Post Date
- Post Content

The filename will include a timestamp (e.g., `brightspace_discussions_20250606_141258.csv`).

## Notes

- Ensure Chrome browser is installed on your system
- The script uses ChromeDriverManager to automatically download the appropriate ChromeDriver version
- The script includes error handling and cleanup procedures
- Data is saved in UTF-8 encoding to handle special characters
