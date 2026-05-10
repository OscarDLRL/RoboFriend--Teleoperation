import cv2
from picamera2 import Picamera2
from flask import Flask, request, jsonify, Response


app = Flask(__name__)
latest_data = {}

#Camera configs
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={
    "format":"",
    "size": (640,480)
    }))
camera.start


#First thing the user sees (well not really, that's GUI work, need to change later)
@app.route("/")
def home():
    return "Flask server is running"

@app.route("/data", methods=["POST"])
def receive_data():
    global latest_data

    latest_data = request.json
    print("Received:", latest_data)

    return jsonify({
        "status": "ok",
        "received": latest_data
    })

@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(latest_data)


def generate_frames():
    while True:
        frame = camera.capture_array()
        ret,buffer = cv2.imencode("jpg",frame)
        frame = buffer.tobytes
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame  +
            b"\r\n"
        )
    

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)