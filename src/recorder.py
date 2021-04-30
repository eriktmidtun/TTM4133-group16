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
        self.channels = 2
        self.fs = 44100
        self.filename = "output.wav"
        self.p = pyaudio.PyAudio()
        self.mqtt_client = mqtt_client
        self.device = device

        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'recording'}
        t2 = {'trigger': 'done', 'source': 'recording', 'target': 'processing'}
        t3 = {'trigger': 'done', 'source': 'processing', 'target': 'ready'}

        s_recording = {'name': 'recording', 'do': 'record()', "stop": "stop()", "start_timer": "start_timer('stop', 000)"}
        s_processing = {'name': 'processing', 'do': 'process()'}

        self.stm = Machine(name='recorder', transitions=[t0, t1, t2, t3], states=[
              s_recording, s_processing], obj=self)

    def record(self):
        print("RECOORDER starting recording")
        stream = self.p.open(format=self.sample_format,
                             channels=self.channels,
                             rate=self.fs,
                             frames_per_buffer=self.chunk,
                             input=True)
        self.frames = []  # Initialize array to store frames
        # Store data in chunks for 3 seconds
        self.recording = True
        self.stm.send("start_timer")
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
        print("RECORDER done recording")
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        self.p.terminate()
        print("done recording")

    def stop(self):
        print("stop")
        self.recording = False

    def process(self):
        print("processing")
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
        print(byteArray[0:12])
        print(byteArray[-12:])

        byteArrayEncoded = base64.b64encode(byteArray)
        imageStringEncoded = base64.b64encode(imagestring)
        #print("bytearrayEncoded", byteArrayEncoded)
        #print("imageStringEncoded", imageStringEncoded)
        #print('imageStringEncoded utf8',imageStringEncoded.decode('utf-8') )

        #print(imageStringEncoded[0:12])
        #print(imageStringEncoded[-12:])
        print("type",type(imageStringEncoded))
        print("done processing")
        print("start sending")
        audioString = imageStringEncoded.decode('utf-8')
        print(audioString[0:12])
        data = {'id': 1, 'audio': audioString}
        #print(data)
        payload = json.dumps(data)
        self.mqtt_client.publish(self.device.make_topic_string("/audio"), payload=imageStringEncoded, qos=2, retain=True)
        #print(imageStringEncoded)







# here we have it as a string, that should be safe to send via JSON


# Decoding




""" recorder = Recorder()

stm = recorder.stm

driver = Driver()
driver.add_machine(stm)
driver.start()

print("driver started")

driver.send('start', 'recorder')
print("sent start, now waiting for a 2 seconds long recording")
time.sleep(2)
print("wait is over")
driver.send('stop', 'recorder')
print("sent stop")
time.sleep(2)
driver.stop()  """
