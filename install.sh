#!/bin/bash
virtFold=venvParser
sudo apt-get install python3-dev python3-pip
sudo apt-get install virtualenv
virtualenv -p /usr/bin/python3 $virtFold
source $virtFold/bin/activate
pip3 install beautifulsoup4
