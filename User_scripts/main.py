import requests
from pynput import keyboard

Laptop = True

urlRasp = "http://192.168.1.80:5000/data"
urlLaptop = "http://192.168.1.137:5000/data"

data = {
    "forward": 1,
    "backward": 0,
    "left": 0,
    "right": 1,
    "led": "red"
}

if Laptop:
    response = requests.post(urlLaptop, json=data)
else:
    response = requests.post(urlRasp, json=data)

print(response.json())