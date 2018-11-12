#!/bin/sh

git pull origin master
export FLASK_APP=/home/pi/rpi-tiny-4wd/tiny4wd-service.py
flask run --host=0.0.0.0 --port=8080
