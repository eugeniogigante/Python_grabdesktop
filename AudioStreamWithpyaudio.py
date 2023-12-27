import pyaudio
import wave
import os
from flask import Flask, Response
import sys

#-------Hidden Python output message---------
output = open("output.txt", "wt")
sys.stdout = output
sys.stderr = output
#--------------------------


app = Flask(__name__)

# Define global variables for audio capture
audio_stream = None
audio_format = pyaudio.paInt16
audio_channels = 1
audio_sample_rate = 44100
audio_chunk_size = 1024

# Initialize PyAudio
p = pyaudio.PyAudio()

# Create a stream for audio capture
audio_stream = p.open(format=audio_format,
                      channels=audio_channels,
                      rate=audio_sample_rate,
                      input=True,
                      frames_per_buffer=audio_chunk_size)

@app.route('/')
def index():
    return "Audio Streaming Server"

def generate_audio():
    while True:
        # Read audio data from the stream
        audio_data = audio_stream.read(audio_chunk_size)
        yield (b'--frame\r\n' +
               b'Content-Type: audio/wav\r\n\r\n' +
               audio_data + b'\r\n')

@app.route('/audio')
def audio():
    return Response(generate_audio(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
