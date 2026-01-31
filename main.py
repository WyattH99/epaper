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

AOC_YEARS = list(range(2015, 2026))  # 2015-2025

def get_url():
    """Get URL from command line arg, environment variable, or cycle through AoC years."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    if os.environ.get('EPAPER_URL'):
        return os.environ.get('EPAPER_URL')
    # Cycle through years based on current hour
    year = AOC_YEARS[datetime.now().hour % len(AOC_YEARS)]
    return f"https://adventofcode.com/{year}"

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
        options['cookie'] = [('session', session)]
    print("Rendering webpage...")
    img_bytes = imgkit.from_url(url, False, options=options)
    return Image.open(io.BytesIO(img_bytes))

def process_image(img, epd, authenticated=True, year=None):
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

    # Draw year at right middle
    if year:
        font_year = ImageFont.truetype('Font.ttc', 48)
        year_str = f"AoC {year}"
        bbox = font_year.getbbox(year_str)
        year_img = Image.new('L', (bbox[2] - bbox[0], bbox[3] - bbox[1]), 255)
        year_draw = ImageDraw.Draw(year_img)
        year_draw.text((-bbox[0], -bbox[1]), year_str, font=font_year, fill=0)
        year_img = year_img.rotate(90, expand=True)
        img.paste(year_img, (epd.width - year_img.width - 2 - int(epd.width * 0.10), (epd.height - year_img.height) // 2))

    # Draw days until December 1st or current AoC day at right middle
    font_days = ImageFont.truetype('Font.ttc', 36)
    today = datetime.now().date()
    if today.month == 12 and 1 <= today.day <= 25:
        days_str = f"Day {today.day} of Advent of Code"
    else:
        dec1 = datetime(today.year, 12, 1).date()
        if today >= dec1:
            dec1 = datetime(today.year + 1, 12, 1).date()
        days_until = (dec1 - today).days
        days_str = f"{days_until} days until Dec 1"
    bbox = font_days.getbbox(days_str)
    days_img = Image.new('L', (bbox[2] - bbox[0], bbox[3] - bbox[1]), 255)
    days_draw = ImageDraw.Draw(days_img)
    days_draw.text((-bbox[0], -bbox[1]), days_str, font=font_days, fill=0)
    days_img = days_img.rotate(90, expand=True)
    img.paste(days_img, (epd.width - days_img.width - 2, epd.height - days_img.height - 2))

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
        # Extract year from URL
        year = url.rstrip('/').split('/')[-1] if 'adventofcode.com' in url else None
        zoom = 1.35
        img = capture_webpage(url, int(epd.width * zoom), int(epd.height * zoom))
        combined = process_image(img, epd, authenticated, year)

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
