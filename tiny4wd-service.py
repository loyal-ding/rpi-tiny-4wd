#!/usr/bin/python3

import picamera
import picamera.array
import numpy as np
import explorerhat
from time import sleep
from PIL import Image

from flask import Flask

# forward power should be 30 to 100
# backward power should be 70 to 100
# turnleft and turnright power should be 60 to 100
# motor 2 forward to go forward
# motor 1 backward to go forward


def forward(power):
  explorerhat.motor.two.forward(power)
  explorerhat.motor.one.backward(power)

def backward(power):
  explorerhat.motor.two.backward(power)
  explorerhat.motor.one.forward(power)

def turnright(power):
  explorerhat.motor.two.forward(power)
  explorerhat.motor.one.forward(power)

def turnleft(power):
  explorerhat.motor.two.backward(power)
  explorerhat.motor.one.backward(power)

  
def stop():
  explorerhat.motor.two.stop()
  explorerhat.motor.one.stop()


class RoverState():
	def __init__(self):
		self.img = None # Current camera image
		self.frame = 0
		# rock in front detection using Camera Warped image
		self.rock_in_front = 0
		self.rock_in_front_left = 0
		self.rock_in_front_right = 0
		# threshold of number of bright pixels to decide not rock. Sample calibration image has 1
		self.rock_in_front_thresh = 15
		self.turn_power = 75
		self.threshold = 900

# power 60 - 100
power = 70
threshold = 500

# Initialize our rover 
Rover = RoverState()
Rover.turn_power = power
Rover.threshold = threshold

xsize = 320
ysize = 240

image = np.empty((xsize, ysize, 3), dtype=np.uint8)
camera = picamera.PiCamera()
camera.resolution = (xsize, ysize)
camera.framerate = 30
camera.hflip = True
camera.vflip = True
camera.awb_mode = 'incandescent'
camera.brightness = 70
rawCapture = picamera.array.PiRGBArray(camera, size=(xsize, ysize))

# let the camera warm up
sleep(2)

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"

# move
@bp.route('/forward/<int:movepower>/<movetime>', methods=('GET', 'POST'))
def moveforward(movepower, movetime):
    forward(movepower)
    sleep(movetime)
    stop()

