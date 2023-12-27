import cv2
import numpy as np
import threading
import wave
import pyaudio
import os
from flask import Flask, render_template, Response
import sys
import pyautogui
from PIL import ImageGrab
from flask_basicauth import BasicAuth  # Import Flask-BasicAuth

def getMousePosition():
    pyautogui.displayMousePosition()
    coords = pyautogui.position()
    return coords

#-------Hidden Python output message---------
#output = open("output.txt", "wt")
#sys.stdout = output
#sys.stderr = output
#--------------------------

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'egigante'  # Set your desired username
app.config['BASIC_AUTH_PASSWORD'] = 'password'  # Set your desired password
basic_auth = BasicAuth(app)  # Initialize Flask-BasicAuth

# Global variables for video and audio capture
video_capture = cv2.VideoCapture(0)
audio_capture = pyaudio.PyAudio()

# Constants for audio streaming
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Global variable to store audio frames
audio_frames = []

# Function to capture desktop
def generate_frames():
    while True:
        x, y = pyautogui.position()
        global desk_frame 
        desk_frame = np.array(ImageGrab.grab(bbox=(0,0,1024,768))) #grab display (1024x768) primary 
        cv2.circle(desk_frame, (x, y), 4, (0,0,255),-1)
        ret, buffer = cv2.imencode('.jpg', desk_frame)  # Encode the frame as JPEG
        desk_frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + desk_frame + b'\r\n')  # Yield the frame in the respon

# Function to capture audio
def audio_stream():
    global audio_frames
    audio_stream = audio_capture.open(format=FORMAT, channels=CHANNELS,
                                     rate=RATE, input=True,
                                     frames_per_buffer=CHUNK)
    while True:
        data = audio_stream.read(CHUNK)
        audio_frames.append(data)

# Function to generate video frames
def video_stream():
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Function to generate audio frames
def audio_gen():
    global audio_frames
    while True:
        if len(audio_frames) > 0:
            yield audio_frames.pop(0)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio_feed')
def audio_feed():
    return Response(audio_gen(),
                    mimetype='audio/x-wav')
@app.route('/desk_feed')
#@basic_auth.required 
def desk_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Return the response with the frames


if __name__ == '__main__':
    audio_thread = threading.Thread(target=audio_stream)
    audio_thread.daemon = True
    audio_thread.start()
    desk_thread = threading.Thread(target=generate_frames)
    desk_thread.daemon = True
    desk_thread.start()

    app.run(host='0.0.0.0', debug=True)
