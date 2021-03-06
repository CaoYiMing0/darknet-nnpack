from picamera import PiCamera
from subprocess import Popen, PIPE
import threading
from time import sleep
import os, fcntl
import cv2
import select
import shutil
import time
iframe = 0

camera = PiCamera()

#Yolo v3 is a full convolutional model. It does not care the size of input image, as long as h and w are multiplication of 32

#camera.resolution = (160,160)
#camera.resolution = (416, 416)
#camera.resolution = (544, 544)
camera.resolution = (608, 608)
#camera.resolution = (608, 288)


camera.capture('frame.jpg')
sleep(0.1)

#spawn darknet process
yolo_proc = Popen(["./darknet",
                   "detect",
                   "./cfg/yolov3-tiny.cfg",
                   "./yolov3-tiny.weights",
                   "-thresh","0.1"],
                   stdin = PIPE, stdout = PIPE)

fcntl.fcntl(yolo_proc.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

stdout_buf = ""
while True:
    try:
        select.select([yolo_proc.stdout], [], [])
        stdout = yolo_proc.stdout.read()
        stdout_buf += stdout
        if 'Enter Image Path' in stdout_buf:
            try:
               im = cv2.imread('predictions.png')
               print(im.shape)
               cv2.imshow('yolov3-tiny',im)
               key = cv2.waitKey(5) 
            except Exception as e:
                print("Error:", e)
            camera.capture('frame.jpg')
            yolo_proc.stdin.write('frame.jpg\n')
            stdout_buf = ""
        if len(stdout.strip())>0:
            print('get %s' % stdout)
    except Exception as e:
        print("Error:", e)
