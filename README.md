# Eduka Flip-Book Downloader

A Python tool to download pages from Eduka flip-books as high-quality PNG images.

## Features

- **Interactive Login**: Opens a browser window for you to log in securely to your Eduka account.
- **Automated Scraping**: Automatically iterates through all pages of the book.
- **Smart Token Extraction**: Uses advanced selectors to find the correct image token for each page.
- **Resume Capability**: Skips pages that have already been downloaded.

## Prerequisites

- Python 3.7+
- Google Chrome or Chromium installed (Playwright will handle this)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/eduka-downloader.git
   cd eduka-downloader
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Usage

1. Run the script:
   ```bash
   python3 eduka_downloader.py
   ```

2. A browser window will open. **Log in** to your Eduka account in this window.

3. Once you can see the dashboard or the book content, return to your terminal and **press Enter**.

4. The script will automatically navigate to the book pages and start downloading them to the `matematika9` folder.

## Configuration

You can modify the `eduka_downloader.py` file to change:
- `base_url_template`: The URL pattern for the book you want to download.
- `output_dir`: The folder where images will be saved.
- `total_pages`: The number of pages to download.

## Disclaimer

This tool is for educational purposes and personal archiving only. Please respect copyright laws and the terms of service of the content provider.
