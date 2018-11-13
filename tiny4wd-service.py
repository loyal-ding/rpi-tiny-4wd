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
from flask import Flask, send_file, make_response

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
        # camera states
        self.camera_x = 1024
        self.camera_y = 768
        self.camera_init = 1

# power 60 - 100
power = 70
threshold = 500

# Initialize our rover 
Rover = RoverState()
Rover.turn_power = power
Rover.threshold = threshold

camera = picamera.PiCamera()
camera.resolution = (Rover.camera_x, Rover.camera_y)
camera.vflip =  True
camera.start_preview()
# Camera warm-up time
sleep(2)

app = Flask(__name__)

# prevent cached responses
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
def hello():
    return "Tiny 4wd service v0.1"

# camera image
@app.route('/getimage/<int:x>/<int:y>', methods=('GET', 'POST'))
def getimage(x,y):
    global camera
    my_stream = BytesIO()
    timestamp = int(time.time())
    filename = str(timestamp) + '.jpg'
    camera.capture(my_stream, 'jpeg')
    my_stream.seek(0)
    response = make_response(my_stream.read())
    response.headers.set('Content-type', 'image/jpeg')
    return response

@app.route('/getframe', methods=('GET', 'POST'))
def getframe():
    global camera
    my_stream = BytesIO()
    timestamp = int(time.time())
    filename = str(timestamp) + '.jpg'
    camera.capture(my_stream, 'jpeg')
    my_stream.seek(0)
    response = make_response(my_stream.read())
    response.headers.set('Content-type', 'image/jpeg')
    return response

@app.route('/setresolution/<int:x>/<int:y>', methods=('GET', 'POST'))
def setresolution(x,y):
    global camera
    global Rover
    camera.stop_preview()
    sleep(2)
    Rover.camera_x = x
    Rover.camera_y = y	
    camera.resolution = (Rover.camera_x, Rover.camera_y)
    camera.start_preview()
    return response

@app.route('/getcameraconfig', methods=('GET', 'POST'))
def getcameraconfig():
    global camera
    global Rover
    result = "X: " + str(Rover.camera_x) + "\n"
    result = "Y: " + str(Rover.camera_y) + "\n"
    result = "ISO: " + str(camera.iso) + "\n"
    result = "Analog Gain: " + str(camera.analog_gain) + "\n"
    # Auto White Balance: (red, blue) balance in fraction 0.0 - 8.0 (typical 0.9 - 1.9)
    result = "AWB Gain: " + str(camera.awb_gain[0]) + " , " + str(camera.awb_gain[1]) + "\n"
    result = "AWB Mode: " + str(camera.awb_mode) + "\n"
    return result
	
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

