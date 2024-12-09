import json
import math
import time
from serial import *
from util import *

ser = Serial("COM9",baudrate=9600,timeout=5)
frame_size = 1500
with open("image.jpg",'rb') as imageFile:
    time.sleep(1)
    content = imageFile.read()
    total_size = len(content)
    print(total_size)
    noOfSend = math.ceil(total_size / frame_size)
    lastTime = 0
    startTime = time.time()

    fileIndex = 0