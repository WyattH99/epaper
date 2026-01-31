#!/bin/bash

sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install spidev
sudo apt install python3-gpiozero
sudo apt install python3-selenium chromium-chromedriver

echo -e "\n\nNext enable the SPI interface using \"sudo raspi-config\" and reboot\n\n"
