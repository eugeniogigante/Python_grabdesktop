#-------------------------------------------------------------------------------
# Name:        Flask SreamDesktop HTML page
# Purpose: Publish a Desktop into HTML page
#
# Author:      eugenio.gigante
#
# Created:     20/09/2023
# Copyright:   (c) eugenio.gigante 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from PIL import ImageGrab
import cv2
from flask import Flask, render_template, Response
import numpy as np
import sys
import pyautogui
from flask_basicauth import BasicAuth  # Import Flask-BasicAuth

def getMousePosition():
    pyautogui.displayMousePosition()
    coords = pyautogui.position()
    return coords

#-------Hidden Python output message---------
output = open("output.txt", "wt")
sys.stdout = output
sys.stderr = output
#--------------------------




app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'egigante'  # Set your desired username
app.config['BASIC_AUTH_PASSWORD'] = 'password'  # Set your desired password
basic_auth = BasicAuth(app)  # Initialize Flask-BasicAuth

#camera = cv2.VideoCapture(0)  # Use camera index 0 for the default camera
#address = f'rtsp://service:Cam3raBr1dg32023!@10.145.123.190'
#camera = cv2.VideoCapture(address)

def generate_frames():
    while True:
        #success, frame = camera.read()  # Read the camera frame
        #if not success:
            #break
        #else:
            #frame = np.array(ImageGrab.grab(bbox=(0,0,1024,768))) #grab display active 
            #ret, buffer = cv2.imencode('.jpg', frame)  # Encode the frame as JPEG
            #frame = buffer.tobytes()
            #yield (b'--frame\r\n'
                   #b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Yield the frame in the response
        x, y = pyautogui.position()
        #print('x=', x , 'y=', y)
        frame = np.array(ImageGrab.grab(bbox=(0,0,1572,945))) #grab display (1024x768) primary 
        cv2.circle(frame, (x, y), 4, (0,0,255),-1)
        ret, buffer = cv2.imencode('.jpg', frame)  # Encode the frame as JPEG
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Yield the frame in the respon
        

#@app.route('/')
#def index():
#    return render_template('index.html')  # Render the HTML template

#@app.route('/video_feed')
#@basic_auth.required 
#def video_feed():
#    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Return the response with the frames


@app.route('/video_feed')
@basic_auth.required
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
@basic_auth.required
def index():
    return ('<html><head><title>Video Stream</title></head>'
            '<body><h1>Video Stream</h1>'
            '<img src="/video_feed" width="1572" height="945">'
            '</body></html>')



if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080")
    #app.run(debug=True)