#!/usr/bin/python
# -*- coding:utf-8 -*-

import epd13in3k
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

import os
import sys
import io
from datetime import datetime

import imgkit

DEFAULT_URL = "https://adventofcode.com/2024"

def get_url():
    """Get URL from command line arg or environment variable."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.environ.get('EPAPER_URL', DEFAULT_URL)

def capture_webpage(url, width, height):
    """Capture a webpage screenshot and return as PIL Image."""
    print(f"Fetching: {url}")
    options = {
        'width': width,
        'height': height,
        'quiet': ''
    }
    print("Rendering webpage...")
    img_bytes = imgkit.from_url(url, False, options=options)
    return Image.open(io.BytesIO(img_bytes))

def process_image(img, epd):
    """Process image for e-paper display."""
    print("Processing image...")
    img = img.convert('L')
    img = ImageOps.invert(img)
    img = ImageEnhance.Contrast(img).enhance(10.0)
    img = img.rotate(90, expand=True)
    img = ImageOps.fit(img, (epd.width, epd.height), Image.Resampling.LANCZOS, centering=(0.25, 0.25))

    # Draw date rotated 90 degrees at bottom right
    font18 = ImageFont.truetype('Font.ttc', 18)
    date_str = datetime.now().strftime('%m-%d-%Y')
    bbox = font18.getbbox(date_str)
    text_img = Image.new('L', (bbox[2] - bbox[0], bbox[3] - bbox[1]), 255)
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((-bbox[0], -bbox[1]), date_str, font=font18, fill=0)
    text_img = text_img.rotate(90, expand=True)
    x = epd.width - text_img.width - 2
    y = 2
    img.paste(text_img, (x, y))

    return img

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

        # Capture webpage and process image
        img = capture_webpage(url, epd.width, epd.height)
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
