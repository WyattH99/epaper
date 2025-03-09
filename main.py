#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import epd13in3k
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import requests

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

    # Fetch website
    # url = "https://example.com"
    url = "https://adventofcode.com/2024"
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve website. Status code: {response.status_code}")
        exit()

    # Clear
    Himage = Image.new('1', (epd.width, epd.height), 255) 
    draw = ImageDraw.Draw(Himage)

    # Draw the HTML content as text (truncate or wrap as needed)
    html_content = response.text
    lines = html_content.split("\n")
    y_position = 10
    for line in lines:
        draw.text((10, y_position), line[:100], font=font12, fill="black")
        y_position += 20
    
    # Save as BMP
    Himage.save("website.bmp", "BMP")
    print("Saved as website.bmp")

    #display 4Gray bmp
    Himage = Image.open('website.bmp')
    epd.display_4Gray(epd.getbuffer_4Gray(Himage))
    time.sleep(20)

    '''
    # CLOCK
    while(True):
        # Clear
        Himage = Image.new('1', (epd.width, epd.height), 255) 
        draw = ImageDraw.Draw(Himage)
        draw.text((0, epd.height/4), time.strftime('%H:%M:%S'), font = font250, fill = 0)
        # Write to display
        epd.display_Base(epd.getbuffer(Himage))
        time.sleep(60*5)

    '''
    '''
    # Drawing on the Horizontal image
    # Clear
    Himage = Image.new('1', (epd.width, epd.height), 255) 
    draw = ImageDraw.Draw(Himage)
    # Text and Shapes
    draw.text((10, 0), 'hello world', font = font24, fill = 0)
    draw.text((10, 20), '13.3inch e-Paper (K)', font = font24, fill = 0)
    draw.line((20, 50, 70, 100), fill = 0)
    draw.line((70, 50, 20, 100), fill = 0)
    draw.rectangle((20, 50, 70, 100), outline = 0)
    draw.line((165, 50, 165, 100), fill = 0)
    draw.line((140, 75, 190, 75), fill = 0)
    draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
    draw.rectangle((80, 50, 130, 100), fill = 0)
    draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
    # Clock
    draw.rectangle((0, 110, 120, 150), fill = 255)
    draw.text((10, 120), time.strftime('%H:%M:%S'), font = font24, fill = 0)
    # Write to display
    epd.display_Base(epd.getbuffer(Himage))
    time.sleep(2)
    '''

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
