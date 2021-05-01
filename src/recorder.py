from stmpy import Machine, Driver
from os import system
import os
import time
import base64
import json

import pyaudio
import wave


class Recorder:
    def __init__(self, mqtt_client, device):
        self.recording = False
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 2  # you might change this based on your mic
        self.fs = 44100
        self.filename = "output.wav"
        self.p = pyaudio.PyAudio()
        self.mqtt_client = mqtt_client
        self.device = device

        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'recording'}
        t2 = {'trigger': 'done', 'source': 'recording',
              'target': 'processing', 'effect': 'stop'}
        t3 = {'trigger': 'done', 'source': 'processing', 'target': 'ready'}

        s_recording = {'name': 'recording', 'do': 'record()',
                       "stop": "stop()", "start_timer": "start_timer('stop', 5000)"}
        s_processing = {'name': 'processing', 'do': 'process()'}

        self.stm = Machine(name='recorder', transitions=[t0, t1, t2, t3], states=[
            s_recording, s_processing], obj=self)

    def record(self):
        stream = self.p.open(format=self.sample_format,
                             channels=self.channels,
                             rate=self.fs,
                             frames_per_buffer=self.chunk,
                             input=True
                             # input_device_index=x to specify mic input
                             )
        self.frames = []  # Initialize array to store frames
        # Store data in chunks for 3 seconds
        self.recording = True
        self.stm.send("start_timer")
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        self.p.terminate()

    def stop(self):
        self.recording = False

    def process(self):
        # Save the recorded data as a WAV file
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        f = open("output.wav", "rb")
        imagestring = f.read()
        f.close()

        # endoding
        byteArray = bytearray(imagestring)
        self.mqtt_client.publish(self.device.make_topic_string(
            "/audio/" + str(self.device.device.id)), payload=byteArray, qos=2)
        self.device.driver.send("over", "device")
