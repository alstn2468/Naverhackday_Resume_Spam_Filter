from PIL import Image
from pytesseract import *
import configparser
import os

# Config parser Init
config = configparser.ConfigParser()
# Config File Read
config.read(os.path.dirname(os.path.realpath(__file__))
            + os.sep + 'envs' + os.sep + 'property.ini')
