#!/bin/bash

sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install --break-system-packages spidev
sudo apt install python3-gpiozero
sudo apt install wkhtmltopdf
sudo pip3 install --break-system-packages imgkit

echo -e "\n\nNext steps:"
echo -e "1. Enable SPI interface: sudo raspi-config → Interface Options → SPI → Enable"
echo -e "2. Reboot"
echo -e "3. (Optional) Set up authentication: echo 'export AOC_SESSION=your_cookie' > ~/.env"
echo -e "4. (Optional) Set up cron job: crontab -e"
echo -e "   Example: 0 3 * * * . ~/.env && cd ~/repos/epaper && python main.py"
echo -e "\nSee README.md for more details.\n"
