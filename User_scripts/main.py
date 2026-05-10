#Becomes Really slow with video, need to change later

import requests
import sys
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, Slot, QThread, Signal, QObject, QRunnable, QThreadPool
import cv2
import time


Laptop = False

urlRasp = "http://192.168.1.141:5000"
urlLaptop = "http://192.168.1.137:5000"
urlVideo = urlRasp + "/video_feed"

current_state = {

    "forward": 0,
    "backward": 0,
    "left": 0,
    "right": 0
}


# Application builder
class RoboFriendWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RoboFriend Teleop")


        #Video GUI parameters 
        self.video_feed =QtWidgets.QLabel(
            "Video Here",
            alignment=Qt.AlignCenter
        )
        self.video_feed.setFixedSize(640, 480)

        # Video Thread Initialitation
        self.video_thread = QThread()
        self.video_worker = VideoWorker(urlVideo)
        self.video_worker.moveToThread(self.video_thread) #Moves video_worker to the new Thread
        self.video_thread.started.connect(self.video_worker.run)
        self.video_worker.frame_ready.connect(self.video_updater) #Conects Video to the GUI
        self.video_thread.start()

        # Global ThreadPool (can share with other tasks, current;y only wasd) 
        self.threadpool = QThreadPool.globalInstance()

        # Instruction text
        self.text = QtWidgets.QLabel(
            "Use wasd for movement",
            alignment=Qt.AlignCenter
        )

        # Layout of GUI
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.video_feed)
        self.layout.addWidget(self.text)
        # Enables Keyboard
        self.setFocusPolicy(QtCore.Qt.StrongFocus)


    # VIDEO (Receives the frame emitted by the worker)
    @Slot(object)
    def video_updater(self,frame):
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
    
    # Conects to sendInputs
    def send_input_async(self):
        url = urlLaptop if Laptop else urlRasp

        task = SendInputTask(url, current_state)

        self.threadpool.start(task)

    # KEY PRESSED
    def keyPressEvent(self, event):
        # Checks if the key is being prssed down and doesnt send the same input multiple times
        if event.isAutoRepeat():
            return

        if event.key() == QtCore.Qt.Key_W:
            current_state["forward"] = 1

        elif event.key() == QtCore.Qt.Key_S:
            current_state["backward"] = 1

        elif event.key() == QtCore.Qt.Key_A:
            current_state["left"] = 1

        elif event.key() == QtCore.Qt.Key_D:
            current_state["right"] = 1

        self.text.setText(str(current_state))
        self.send_input_async()

    # KEY RELEASED
    def keyReleaseEvent(self, event):
        # Checks if the key is being prssed down and doesnt send the same input multiple times
        if event.isAutoRepeat():
            return

        if event.key() == QtCore.Qt.Key_W:
            current_state["forward"] = 0

        elif event.key() == QtCore.Qt.Key_S:
            current_state["backward"] = 0

        elif event.key() == QtCore.Qt.Key_A:
            current_state["left"] = 0

        elif event.key() == QtCore.Qt.Key_D:
            current_state["right"] = 0

        self.text.setText(str(current_state))
        self.send_input_async()

# Different thread for video, QThread is perfect for long tasks, it will crash without this
class VideoWorker(QObject):

    frame_ready = Signal(object)
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.running = True

    @Slot()
    def run(self):
        self.cap = cv2.VideoCapture(self.url)

        while self.running:
            ret, frame = self.cap.read()

            if not ret:
                continue

            self.frame_ready.emit(frame)

            # FPS control, stops every 30 ms
            time.sleep(0.03)

        self.cap.release()

    @Slot()
    def stop(self):
        self.running = False


class SendInputTask(QRunnable):
    def __init__(self, url, state):
        super().__init__()
        self.url = url
        self.state = state.copy()

    #Sends any combination of w,a,s and d inputs
    def run(self):
        response = requests.post(self.url + "/data", json=self.state) 



if __name__ == "__main__":
    
    app = QtWidgets.QApplication([])
    widget = RoboFriendWidget()
    widget.resize(680, 1000)
    widget.show()

    sys.exit(app.exec())