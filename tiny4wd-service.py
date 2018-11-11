import picamera
import picamera.array
import numpy as np
import explorerhat
from PIL import Image

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
