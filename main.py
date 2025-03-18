#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import epd13in3k
import time
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance
import traceback

import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

try:

    # epd setup
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear()

    # Fonts
    font6 = ImageFont.truetype('Font.ttc', 6)
    font12 = ImageFont.truetype('Font.ttc', 12)
    font18 = ImageFont.truetype('Font.ttc', 18)
    font24 = ImageFont.truetype('Font.ttc', 24)
    font35 = ImageFont.truetype('Font.ttc', 35)
    font100 = ImageFont.truetype('Font.ttc', 100)
    font250 = ImageFont.truetype('Font.ttc', 250)
    font500 = ImageFont.truetype('Font.ttc', 500)

    # Set up headless Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(epd.width, epd.height)

    # Fetch website
    # url = "https://example.com"
    # url = "https://adventofcode.com/2024"
    # url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Caspar_David_Friedrich_-_Wanderer_above_the_Sea_of_Fog.jpeg/1200px-Caspar_David_Friedrich_-_Wanderer_above_the_Sea_of_Fog.jpeg"
    # url = "https://wolfgang-ziegler.com/posts/2023/aoc2022/aoc2022_50stars.png"
    url = "https://www.markheath.net/posts/2020/advent-of-code-2020-1.png"
    # url = "https://images.squarespace-cdn.com/content/v1/5a05ececd55b4165f250f032/1606502813028-AILM0LTLRXNTKE23LTJY/Screen+Shot+2020-11-27+at+5.27.23+PM.png?format=1000w"
    driver.get(url)
    driver.save_screenshot("screenshot.png")
    driver.quit()

    img = Image.open("screenshot.png")
    img = img.convert('L')
    img = ImageOps.invert(img)
    img = ImageEnhance.Contrast(img)
    img = img.enhance(2)
    img = img.resize((epd.width // 5, epd.height // 2), Image.Resampling.LANCZOS)
    img.save("update.png")

    combined_image = Image.new('1', (epd.width, epd.height), 255)  
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
