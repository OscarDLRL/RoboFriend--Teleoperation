import requests
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui


Laptop = True

urlRasp = "http://192.168.1.80:5000/data"
urlLaptop = "http://192.168.1.137:5000/data"

current_state = {
    "forward": 0,
    "backward": 0,
    "left": 0,
    "right": 0
}

#Sends any combination of w,a,s and d inputs
def sendInput():
    if Laptop:
        response = requests.post(urlLaptop, json=current_state)
    else:
        response = requests.post(urlRasp, json=current_state) 
    print(current_state)


# Application builder
class RoboFriendWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World",alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = RoboFriendWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())