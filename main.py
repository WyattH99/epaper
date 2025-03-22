#!/usr/bin/python
# -*- coding:utf-8 -*-

import epd13in3k
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance,ImageFilter

import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

try:

    # epd setup
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear()

    # Fonts
    font18 = ImageFont.truetype('Font.ttc', 18)

    # Set up headless Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(epd.width, epd.height)

    # Fetch website
    url = "https://www.markheath.net/posts/2020/advent-of-code-2020-1.png"
    # url = "https://wolfgang-ziegler.com/posts/2023/aoc2022/aoc2022_50stars.png"
    driver.get(url)
    driver.save_screenshot("screenshot.png")
    driver.quit()

    # Image Editing
    img = Image.open("screenshot.png")
    img = img.convert('L')
    img = ImageOps.invert(img)
    img = ImageEnhance.Contrast(img)
    img = img.enhance(10.0)
    img = img.resize((epd.width // 5, epd.height // 2), Image.Resampling.LANCZOS)

    # Merge Images
    combined_image = Image.new('L', (epd.width, epd.height), 255)  
    combined_image.paste(img, (0, 0))
    combined_image.paste(img, ((epd.width // 5) * 1, 0))
    combined_image.paste(img, ((epd.width // 5) * 2, 0))
    combined_image.paste(img, ((epd.width // 5) * 3, 0))
    combined_image.paste(img, ((epd.width // 5) * 4, 0))
    combined_image.paste(img, (0, (epd.height // 2)))
    combined_image.paste(img, ((epd.width // 5) * 1, (epd.height // 2)))
    combined_image.paste(img, ((epd.width // 5) * 2, (epd.height // 2)))
    combined_image.paste(img, ((epd.width // 5) * 3, (epd.height // 2)))
    combined_image.paste(img, ((epd.width // 5) * 4, (epd.height // 2)))

    # Draw Date
    draw = ImageDraw.Draw(combined_image)
    date_str = datetime.now().strftime('%m-%d-%Y')
    draw.text((2, 0), date_str, font = font18, fill = 0)
    
    # Display
    epd.display_4Gray(epd.getbuffer_4Gray(combined_image))
    print("sleep")
    time.sleep(20)

    # Clear
    epd.init()
    epd.Clear()

    # Sleep
    epd.sleep()

except IOError as e:
    print(e)
    
except KeyboardInterrupt:    
    epd13in3k.epdconfig.module_exit(cleanup=True)
    exit()
