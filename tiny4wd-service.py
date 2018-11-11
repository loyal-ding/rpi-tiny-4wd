#!/usr/bin/python3

import picamera
import picamera.array
import numpy as np
import explorerhat
import time
from time import sleep
from PIL import Image
from io import BytesIO
import flask
from flask import Flask, send_file

# forward power should be 30 to 100
# backward power should be 70 to 100
# turnleft and turnright power should be 60 to 100
# motor 2 backward to go forward
# motor 1 forward to go forward


def forward(power):
  explorerhat.motor.two.backward(power)
  explorerhat.motor.one.forward(power)

def backward(power):
  explorerhat.motor.two.forward(power)
  explorerhat.motor.one.backward(power)

def turnright(power):
  explorerhat.motor.two.backward(power)
  explorerhat.motor.one.backward(power)

def turnleft(power):
  explorerhat.motor.two.forward(power)
  explorerhat.motor.one.forward(power)

  
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

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"

# camera image
@app.route('/getimage/<int:x>/<int:y>', methods=('GET', 'POST'))
def getimage(x,y):
    camera = picamera.PiCamera()
    camera.resolution = (x, y)
    camera.start_preview()
    # Camera warm-up time
    sleep(2)
    my_stream = BytesIO()
    timestamp = int(time.time())
    filename = str(timestamp) + '.jpg'
    camera.capture(my_stream, 'jpeg')
    flask.response.set_header('Content-type', 'image/jpeg')
    return my_stream.read()

# move
@app.route('/forward/<int:movepower>/<float:movetime>', methods=('GET', 'POST'))
def moveforward(movepower, movetime):
    forward(movepower)
    sleep(movetime)
    stop()
    return "Forward Done"

@app.route('/backward/<int:movepower>/<float:movetime>', methods=('GET', 'POST'))
def movebackard(movepower, movetime):
    backward(movepower)
    sleep(movetime)
    stop()
    return "Backward Done"

@app.route('/turnleft/<int:movepower>/<float:movetime>', methods=('GET', 'POST'))
def moveturnleft(movepower, movetime):
    turnleft(movepower)
    sleep(movetime)
    stop()
    return "Turn Left Done"

@app.route('/turnright/<int:movepower>/<float:movetime>', methods=('GET', 'POST'))
def moveturnright(movepower, movetime):
    turnright(movepower)
    sleep(movetime)
    stop()
    return "Turn Right Done"
	
# move motor one forward
@app.route('/oneforward/<int:movepower>/<float:movetime>', methods=('GET', 'POST'))
def moveoneforward(movepower, movetime):
    explorerhat.motor.one.forward(power)
    sleep(movetime)
    stop()
    return "One Forward Done"

# move motor one forward
@app.route('/twoforward/<int:movepower>/<float:movetime>', methods=('GET', 'POST'))
def movetwoforward(movepower, movetime):
    explorerhat.motor.two.backward(power)
    sleep(movetime)
    stop()
    return "Two Forward Done"

