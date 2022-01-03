# import flask things
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import threading
from flask.templating import render_template_string

import pickledb
import logging
from email_file import send_file_email
db = pickledb.load('db.db', False)

import pyaudio
import wave
from time import time, sleep
import base64


import sys
import os
import tkinter as tk
from tkinter import messagebox
from flaskwebgui import FlaskUI

def alert(title, alert_content):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, alert_content)



# instantiate flask app
app = Flask(__name__)
ui = FlaskUI(app, width=800, height=600, port=5000, start_server="flask")
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
# routes
@app.route('/')
def index():
    return redirect(url_for('begin'))


@app.route('/begin', methods=['POST' , 'GET'])
def begin():
    if request.method == 'POST':
        return redirect('/plugin')
    else:
        return render_template('begin.html')

@app.route('/plugin', methods=['POST' , 'GET'])
def plugin():
    if request.method == 'POST':
        return redirect('/rewind')
    else:
        return render_template('plugin.html')

@app.route('/rewind', methods=['POST' , 'GET'])
def rewind():
    if request.method == 'POST':
        try:
            db.set('start', 'true')
            print('start set to true')
            return redirect('/play')
        except Exception as e:
            logging.warning(e)
    else:
        return render_template('rewind.html')

@app.route('/play', methods=['POST' , 'GET'])
def play():
    if request.method == 'POST':
        db.set('stop', 'true')
        print('stop set to true')
        # db.dump()
        

        return redirect('/sending')
    else:
        return render_template('play.html')

@app.route('/sending')
def sending():
    return render_template('sending.html')

@app.route('/endcard', methods=['POST' , 'GET'])
def endcard():
    if request.method == 'POST':
        # print("that's it")

        sleep(10)
        os._exit(1)
        return render_template_string("here")

        

    else:
        send_file_email('zwc1223@gmail.com', 'audio.wav')
        return render_template('endcard.html')






class Recorder():
    def __init__(self, filename):
        self.audio_format    = pyaudio.paInt16
        self.channels        = 4
        self.sample_rate     = 44100
        self.chunk           = int(0.03*self.sample_rate)
        self.filename        = filename
        self.start           = 's'
        self.quit            = 'q'
    
    def get_index(self):
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
         
        for i in range(0, numdevices):

            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                device_name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                print(f"DEVICE: {device_name}\nINDEX: {i}")
        # self.respeaker_index = input("Please enter the index of the device you want to use: ")
        #         if device_name == 'ac108':
        #             # Respeaker found
        #             self.respeaker_index = i
        #             return
        
        # Runs if respeaker is not found, 
        # on "Built-in Microphone"
        self.respeaker_index = 1

    def record(self):
        self.start_time = time()

        recorded_data = []
        p = pyaudio.PyAudio()

        stream = p.open(format              = self.audio_format, 
                        channels            = self.channels,
                        rate                = self.sample_rate, 
                        input               = True,
                        input_device_index  = self.respeaker_index,
                        frames_per_buffer   = self.chunk)

        print('\nRecording STARTED...')

        while True:
            data = stream.read(self.chunk)
            recorded_data.append(data)

            self.end = time()
            if db.get('stop') == 'true':
                db.set('stop', 'false')
                print('stop set to false')


                print('\nRecording STOPPED...')
                
                print(self.end - self.start_time)

                # Stop and close the stream
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                wf = wave.open(self.filename, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(p.get_sample_size(self.audio_format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(recorded_data))
                wf.close()

                break

    def listen(self):
        print("Press `" + self.start + "` to start and `" + self.quit + "` to quit!")
        while True:

            if db.get('start') == 'true':
                print('listen found start = true')
                db.set('start', 'false')
                print('start set to false')
                # db.dump()

                self.record()
                break
    
    def get_info(self):
        f = open(self.filename, 'rb')
        bytes = bytearray(f.read())
        audio_file_encoded = base64.b64encode(bytes)
        f.close()

        audio_info = {
            "channels":     self.channels,
            "sample_rate":  self.sample_rate,
            "audio_file":   audio_file_encoded
        }

        return audio_info


def record_audio(filename):
    recorder = Recorder(filename)
    recorder.get_index()
    recorder.listen()

def recording_loop():
    while True:
        record_audio("audio.wav")
    # sys.exit()


alert("Please Wait | Dictaphone Digitizer", "This program can take a few minutes to start fully. Thank you for your patience.")

threading.Thread(target=recording_loop).start()
threading.Thread(target=ui.run()).start()



