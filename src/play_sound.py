import pyaudio
import wave
import os

def play_sound(filename):
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    RATE = 44100
    FILE_SIZE = os.path.getsize(filename)

    p = pyaudio.PyAudio()
    output = p.open(format=FORMAT,
                            channels=1,
                            rate=RATE,
                            output=True) # frames_per_buffer=CHUNK_SIZE
    with open(filename, 'rb') as fh:
        while fh.tell() != FILE_SIZE: # get the file-size from the os module
            AUDIO_FRAME = fh.read(CHUNK_SIZE)
            output.write(AUDIO_FRAME)