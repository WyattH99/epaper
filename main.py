#!/usr/bin/python
# -*- coding:utf-8 -*-

import epd13in3k
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

import os
import sys
import io
from datetime import datetime

import imgkit
import urllib.request
import socket
import getpass

DEFAULT_URL = "https://adventofcode.com/2024"

def get_url():
    """Get URL from command line arg or environment variable."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.environ.get('EPAPER_URL', DEFAULT_URL)

def get_ssh_info():
    """Get username@ip for SSH connection."""
    username = getpass.getuser()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = '?'
    return f"{username}@{ip}"

def check_auth(url):
    """Check if session cookie is valid by looking for login link."""
    session = os.environ.get('AOC_SESSION')
    if not session:
        return False
    req = urllib.request.Request(url)
    req.add_header('Cookie', f'session={session}')
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        return '[Log Out]' in html

def capture_webpage(url, width, height):
    """Capture a webpage screenshot and return as PIL Image."""
    print(f"Fetching: {url}")
    options = {
        'width': width,
        'height': height,
        'quiet': ''
    }
    session = os.environ.get('AOC_SESSION')
    if session:
        options['cookie'] = [('session', session, 'adventofcode.com')]
    print("Rendering webpage...")
    img_bytes = imgkit.from_url(url, False, options=options)
    return Image.open(io.BytesIO(img_bytes))

def process_image(img, epd, authenticated=True):
    """Process image for e-paper display."""
    print("Processing image...")
    img = img.convert('L')
    img = ImageOps.invert(img)
    img = ImageEnhance.Contrast(img).enhance(10.0)
    img = img.rotate(90, expand=True)
    img = ImageOps.fit(img, (epd.width, epd.height), Image.Resampling.LANCZOS, centering=(0.25, 1.0))

    font18 = ImageFont.truetype('Font.ttc', 24)
    x = epd.width - 2
    y = 2

    # Draw SSH info (rightmost)
    ssh_str = get_ssh_info()
    bbox = font18.getbbox(ssh_str)
    ssh_img = Image.new('L', (bbox[2] - bbox[0], bbox[3] - bbox[1]), 255)
    ssh_draw = ImageDraw.Draw(ssh_img)
    ssh_draw.text((-bbox[0], -bbox[1]), ssh_str, font=font18, fill=0)
    ssh_img = ssh_img.rotate(90, expand=True)
    x -= ssh_img.width
    img.paste(ssh_img, (x, y))
    x -= 5  # spacing

    # Draw warning if not authenticated (middle)
    if not authenticated:
        warn_str = "SESSION EXPIRED"
        bbox = font18.getbbox(warn_str)
        warn_img = Image.new('L', (bbox[2] - bbox[0], bbox[3] - bbox[1]), 255)
        warn_draw = ImageDraw.Draw(warn_img)
        warn_draw.text((-bbox[0], -bbox[1]), warn_str, font=font18, fill=0)
        warn_img = warn_img.rotate(90, expand=True)
        x -= warn_img.width
        img.paste(warn_img, (x, y))
        x -= 5  # spacing

    # Draw date (leftmost)
    date_str = datetime.now().strftime('%m-%d-%Y')
    bbox = font18.getbbox(date_str)
    text_img = Image.new('L', (bbox[2] - bbox[0], bbox[3] - bbox[1]), 255)
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((-bbox[0], -bbox[1]), date_str, font=font18, fill=0)
    text_img = text_img.rotate(90, expand=True)
    x -= text_img.width
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

        # Check authentication and capture webpage
        print("Checking authentication...")
        authenticated = check_auth(url)
        if os.environ.get('AOC_SESSION'):
            if authenticated:
                print("Session: Valid")
            else:
                print("Session: EXPIRED or invalid")
        else:
            print("Session: No AOC_SESSION set")
        zoom = 1.5
        img = capture_webpage(url, int(epd.width * zoom), int(epd.height * zoom))
        combined = process_image(img, epd, authenticated)

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
