import requests
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import cv2


Laptop = True

urlRasp = "http://192.168.1.141:5000"
urlLaptop = "http://192.168.1.137:5000"
urlVideo = urlRasp + "/video_feed"

current_state = {

    "forward": 0,
    "backward": 0,
    "left": 0,
    "right": 0
}

#Sends any combination of w,a,s and d inputs
def sendInput():
    if Laptop:
        response = requests.post(urlLaptop + "/data", json=current_state)
    else:
        response = requests.post(urlRasp + "/data", json=current_state) 
    print(current_state)


# Application builder
class RoboFriendWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RoboFriend Teleop")


        #Video GUI parameters
        self.video_feed =QtWidgets.QLabel(
            "Video Here",
            alignment=QtCore.Qt.AlignCenter
        )
        self.video_feed.setFixedSize(640, 480)
        self.cap = cv2.VideoCapture(urlVideo)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.video_updater)
        self.timer.start(30)

        self.text = QtWidgets.QLabel(
            "Use wasd for movement",
            alignment=QtCore.Qt.AlignCenter
        )

        # Layout of GUI
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.video_feed)
        self.layout.addWidget(self.text)
        # Enables Keyboard
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    # VIDEO, updates image to the GUI taken fron URL
    def video_updater(self):
        ret,frame = self.cap.read()
        if not ret:
            self.video_feed.setText("No video frame")
            return
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape
        bytes_per_line = ch * w

        qt_image = QtGui.QImage(
            frame.data,
            w,
            h,
            bytes_per_line,
            QtGui.QImage.Format_RGB888
        )

        pixmap = QtGui.QPixmap.fromImage(qt_image)
        self.video_feed.setPixmap(pixmap)

    # KEY PRESSED
    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_W:
            current_state["forward"] = 1

        elif event.key() == QtCore.Qt.Key_S:
            current_state["backward"] = 1

        elif event.key() == QtCore.Qt.Key_A:
            current_state["left"] = 1

        elif event.key() == QtCore.Qt.Key_D:
            current_state["right"] = 1

        self.text.setText(str(current_state))

        sendInput()


    # KEY RELEASED
    def keyReleaseEvent(self, event):

        if event.key() == QtCore.Qt.Key_W:
            current_state["forward"] = 0

        elif event.key() == QtCore.Qt.Key_S:
            current_state["backward"] = 0

        elif event.key() == QtCore.Qt.Key_A:
            current_state["left"] = 0

        elif event.key() == QtCore.Qt.Key_D:
            current_state["right"] = 0

        self.text.setText(str(current_state))

        sendInput()



if __name__ == "__main__":
    
    app = QtWidgets.QApplication([])

    

    widget = RoboFriendWidget()
    widget.resize(1000, 1000)
    widget.show()

    sys.exit(app.exec())