import picamera
import picamera.array
import numpy as np
import explorerhat
from time import sleep
from PIL import Image
import argparse

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


def color_thresh(img, rgb_thresh=(200, 200, 200)):
	# Create an array of zeros same xy size as img, but single channel
	color_select = np.zeros_like(img[:,:,0])
	# Require that each pixel be above all three threshold values in RGB
	# above_thresh will now contain a boolean array with "True"
	# where threshold was met
	above_thresh = (img[:,:,0] > rgb_thresh[0]) \
				& (img[:,:,1] > rgb_thresh[1]) \
				& (img[:,:,2] > rgb_thresh[2])
	# Index the array of zeros with the boolean array and set to 1
	color_select[above_thresh] = 1
	# Return the binary image
	return color_select

def perception_step(Rover):
	colorsel = color_thresh(Rover.img, rgb_thresh=(200, 200, 200))
	# rock in front detection
	Rover.rock_in_front = 0
	Rover.rock_in_front_left = 0
	Rover.rock_in_front_right = 0
	#print(colorsel.shape)
	
	if Rover.frame % 100 == 0:
		colorsave = colorsel * 255
		im = Image.fromarray(colorsave)
		im.save("colorsel-" + str(Rover.frame).zfill(5) + ".jpg")

	rif_clip_left = colorsel[80:,60:160]
	rif_clip_right = colorsel[80:,161:261]
	
	rif_clip_left_ypos, rif_clip_left_xpos = rif_clip_left.nonzero()
	num_left = len(rif_clip_left_ypos)
	if (len(rif_clip_left_ypos) > Rover.rock_in_front_thresh):
		Rover.rock_in_front_left = 1
	
	rif_clip_right_ypos, rif_clip_right_xpos = rif_clip_right.nonzero()
	num_right = len(rif_clip_right_ypos)
	if (len(rif_clip_right_ypos) > Rover.rock_in_front_thresh):
		Rover.rock_in_front_right = 1

	bias = len(rif_clip_left_ypos) - len(rif_clip_right_ypos)
	if (Rover.rock_in_front_right == 1) and (Rover.rock_in_front_left == 1):
		if (bias > Rover.threshold):
			Rover.rock_in_front_left = 1
			Rover.rock_in_front_right = 0
		elif (bias < -Rover.threshold):
			Rover.rock_in_front_left = 0
			Rover.rock_in_front_right = 1
		else:
			Rover.rock_in_front = 1
			
	print(Rover.frame,num_left,num_right,bias)
	return Rover

def decision_step(Rover):
	if Rover.rock_in_front == 1:
		stop()
	elif Rover.rock_in_front_left == 1:
		turnleft(Rover.turn_power)    
	else:
		turnright(Rover.turn_power)
	return Rover
	
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

parser = argparse.ArgumentParser(description='Tiny 4WD White Object Chaser')
parser.add_argument("power", type=int, help="Turning power 60 - 100")
parser.add_argument('threshold', type=int, help="Threshold default 500")
args = parser.parse_args()

		
# Initialize our rover 
Rover = RoverState()
Rover.turn_power = args.power
Rover.threshold = args.threshold


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

# Wait for analog gain to settle on a higher value than 1
#while camera.analog_gain <= 1:
#    sleep(0.1)

k = 0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image - this array
	# will be 3D, representing the width, height, and # of channels
	Rover.img = frame.array
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	
	#print(k,np.mean(Rover.img))
	#im = Image.fromarray(Rover.img)
	#im.save("frame" + str(k).zfill(3) + ".jpg")
	
	Rover = perception_step(Rover)
	Rover = decision_step(Rover)  
	
	# if the `q` key was pressed, break from the loop
	Rover.frame += 1
	if Rover.frame > 10000:
		stop()
		break

#for k in range(10):
#  capture(camera)
  #print(k)

print("Done")
  
exit()

with picamera.PiCamera() as camera:
	camera.resolution = (320, 240)
	sleep(2)
	image = np.empty((320, 240, 3), dtype=np.uint8)
	camera.capture(image, 'rgb')
	print(image.shape)

turnleft(60)
sleep(15)
stop()



sleep(1)

turnright(60)
sleep(1)
stop()

sleep(1)


backward(70)
sleep(1)
stop()

sleep(1)

forward(30)
sleep(1)
stop()

def capture(camera):
  global image
  camera.capture(image, 'rgb')
