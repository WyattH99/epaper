#!/usr/bin/python
# -*- coding:utf-8 -*-

import epd13in3k
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

import os
import sys
import tempfile
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DEFAULT_URL = "https://www.markheath.net/posts/2020/advent-of-code-2020-1.png"

def get_url():
    """Get URL from command line arg or environment variable."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.environ.get('EPAPER_URL', DEFAULT_URL)

def capture_screenshot(url, width, height):
    """Capture a screenshot of the URL and return as PIL Image."""
    print("Starting headless browser...")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(width, height)

    try:
        print(f"Fetching: {url}")
        driver.get(url)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        print("Capturing screenshot...")
        driver.save_screenshot(temp_path)
        img = Image.open(temp_path)
        img.load()  # Load image data before deleting file
        os.unlink(temp_path)
        return img
    finally:
        driver.quit()

def process_image(img, epd):
    """Process image for e-paper display."""
    print("Processing image...")
    img = img.convert('L')
    img = ImageOps.invert(img)
    img = ImageEnhance.Contrast(img).enhance(10.0)
    img = img.resize((epd.width // 5, epd.height // 2), Image.Resampling.LANCZOS)

    # Tile image in 5x2 grid
    combined = Image.new('L', (epd.width, epd.height), 255)
    for row in range(2):
        for col in range(5):
            combined.paste(img, (col * (epd.width // 5), row * (epd.height // 2)))

    # Draw date
    font18 = ImageFont.truetype('Font.ttc', 18)
    draw = ImageDraw.Draw(combined)
    date_str = datetime.now().strftime('%m-%d-%Y')
    draw.text((2, 0), date_str, font=font18, fill=0)

    return combined

def main():
    epd = None
    try:
        url = get_url()

        # Initialize display
        print("Initializing display...")
        epd = epd13in3k.EPD()
        epd.init()
        print("Clearing display...")
        epd.Clear()

        # Capture and process image
        img = capture_screenshot(url, epd.width, epd.height)
        combined = process_image(img, epd)

        # Display image (e-paper retains image without power)
        print("Rendering to display...")
        epd.display_4Gray(epd.getbuffer_4Gray(combined))
        print("Display updated, entering sleep mode")

        # Put display controller to sleep (image remains)
        epd.sleep()
        print("Done")

    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if epd:
            try:
                epd13in3k.epdconfig.module_exit(cleanup=True)
            except:
                pass

if __name__ == '__main__':
    main()
