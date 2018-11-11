# rpi-tiny-4wd
Raspberry Pi Tiny Four Wheel Drive

Installation

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

python get-pip.py

pip install Flask

export FLASK_APP=/home/pi/rpi-tiny-4wd/tiny4wd-service.py


flask run --host=0.0.0.0 --port=8080

* Running on http://localhost:5000/

