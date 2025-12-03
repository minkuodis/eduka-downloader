import os
import time
import requests
from playwright.sync_api import sync_playwright

"""
Eduka Downloader
----------------
A script to download flip-book pages from Eduka.lt.
It uses Playwright for navigation and token extraction, and Requests for downloading images.

Usage:
    python3 eduka_downloader.py
"""

def main():
    # Configuration
    # URL template for the book pages. {0} will be replaced by the page number.
    base_url_template = "https://eduka.lt/publisher/material/open/theory/49429/601?teachingPackageId=601&teachingGroupCreation=0&lesson=52845&subtype=tasks&pageFlip={}"
    output_dir = "matematika9"
    total_pages = 226
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    with sync_playwright() as p:
        # Launch browser (headful so user can see and log in)
        # We use a persistent context or just a standard launch. 
        # Standard launch is fine as long as we keep the session open.
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 1. Navigate to initial page (will likely redirect to login)
        print("Navigating to Eduka...")
        page.goto("https://eduka.lt/auth")

        # 2. Wait for user login
        print("\n" + "="*50)
        print("PLEASE LOG IN MANUALLY IN THE BROWSER WINDOW.")
        print("Once you are logged in and can see the dashboard/content,")
        print("come back here and PRESS ENTER to start the download.")
        print("="*50 + "\n")
        input("Press Enter to continue...")

        print("Starting download process...")

        # 3. Loop through pages
        for i in range(1, total_pages + 1):
            page_num_str = f"{i:03d}"
            filename = os.path.join(output_dir, f"{page_num_str}.png")
            
            if os.path.exists(filename):
                print(f"Skipping page {i} (already exists)")
                continue

            url = base_url_template.format(i)
            print(f"Processing page {i}/{total_pages}...")
            
            try:
                page.goto(url)
                
                # Wait for the image element with the token
                # The user specified: <image ... xlink:href="/teaching-tool-page-image/TOKEN">
                # We look for an 'image' tag with an 'href' or 'xlink:href' attribute containing the prefix.
                # Note: In SVG, attributes can be tricky in selectors.
                # We'll try a CSS selector for the image tag.
                
                # Wait for the element to be present
                # Strategy 1: Look for the thumbnail image which contains the token in data-src
                # This seems to be present in the DOM for navigation
                token_element = None
                href = None
                
                try:
                    print("  Checking thumbnails...")
                    # Selector for thumbnail
                    thumb_selector = f'img[data-pageflip-goto="{i}"]'
                    # We don't strictly need it to be visible if it's just in the DOM, but let's wait a bit
                    try:
                        token_element = page.wait_for_selector(thumb_selector, state="attached", timeout=5000)
                        if token_element:
                            href = token_element.get_attribute("data-src")
                            if href:
                                print("  Found token in thumbnail data-src")
                    except:
                        pass
                except Exception as e:
                    print(f"  Thumbnail strategy failed: {e}")

                # Strategy 2: If thumbnail failed, try the main SVG image
                if not href:
                    try:
                        print("  Checking main SVG image...")
                        # Robust XPath for SVG image with href/xlink:href
                        # We look for any <image> tag that has an attribute ending with the token pattern or containing the path
                        xpath = '//*[local-name()="image" and @*[local-name()="href" and contains(., "/teaching-tool-page-image/")]]'
                        token_element = page.wait_for_selector(f'xpath={xpath}', timeout=5000)
                        if token_element:
                            # We need to get the attribute. We can't easily know which one (href or xlink:href) via get_attribute if we don't know the name
                            # But we can evaluate JS
                            href = token_element.evaluate('(el) => el.getAttribute("xlink:href") || el.getAttribute("href")')
                            if href:
                                print("  Found token in SVG image")
                    except Exception as e:
                        print(f"  SVG strategy failed: {e}")
                
                if not href:
                    print(f"Could not find image token for page {i}")
                    # Debug: Save screenshot and HTML
                    page.screenshot(path=f"debug_page_{i}.png")
                    with open(f"debug_page_{i}.html", "w") as f:
                        f.write(page.content())
                    print(f"  Saved debug info to debug_page_{i}.png and .html")
                    continue
                
                if not href:
                    print(f"Found element but no href for page {i}")
                    continue
                
                # Construct full image URL
                # href is like /teaching-tool-page-image/TOKEN
                image_url = f"https://eduka.lt{href}"
                
                # Download the image
                # We use the browser context cookies to ensure we are authorized
                cookies = context.cookies()
                session = requests.Session()
                for cookie in cookies:
                    session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
                
                response = session.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    print(f"Saved: {filename}")
                else:
                    print(f"Failed to download image for page {i}: Status {response.status_code}")
                
                # Small pause to be polite
                time.sleep(0.5)

            except Exception as e:
                print(f"Error processing page {i}: {e}")
        
        print("\nDownload complete!")
        browser.close()

if __name__ == "__main__":
    main()
