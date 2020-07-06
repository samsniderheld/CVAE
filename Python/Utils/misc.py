import numpy as np
import cv2
import re
from config import ConfigOptions
config = ConfigOptions()

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def process(img):
    retval, threshold = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
    return threshold

def convert(img):
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return grayscale

def resize(img):
    resized = cv2.resize(img, dsize=(config.img_dim, config.img_dim), interpolation=cv2.INTER_NEAREST)
    return resized

