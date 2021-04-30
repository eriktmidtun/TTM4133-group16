import base64 
import json

import pyaudio
import wave

chunk = 1024
sample_format = pyaudio.paInt16
channels = 2
fs = 44100
filename = "output_2.wav"
p = pyaudio.PyAudio()

def process():
    print("processing")
    # Save the recorded data as a WAV file
    """ wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close() """

    f = open("output_2.wav", "rb")
    imagestring = f.read()
    f.close()

    # endoding
    byteArray = bytearray(imagestring)
    print(byteArray[0:12])
    print(byteArray[-12:])

    imageStringEncoded = base64.b64encode(imagestring)

    return imageStringEncoded

def write_to_file(imageStringEncoded):
    bytearr = bytearray(imageStringEncoded)
    imageStringDecoded = base64.b64decode(bytearr)
    print("decoded")
    f = open("input-test.wav", 'wb')
    f.write(imageStringDecoded)
    f.close()

def to_json():
    

def on_audio_message():
    filename = 'input.wav'
    try:
        payload = json.loads(payload)
    except Exception as err:
        print('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(
            msg.topic, err))
    print("RECEIVER: json loaded")
    #device_id = payload.get("id")
    audioString = payload["audio"]
    print("RECEIVER audiostring type" ,type(audioString))
    print("RECEIVER audiostring" ,audioString[0:12])
    bytearr = bytearray(audioString.encode("ascii"))
    print("bytearr type", type(bytearr), bytearr[0:12] )
    imageStringDecoded = base64.b64decode(bytearr)
    print("RECEIVER: audioString decoded")
    f = open(filename, 'wb')
    f.write(imageStringDecoded)
    f.close()
    print("RECEIVER: audio written") 

def play_message():
    filename = 'input-test.wav'
    print("Trying to play incoming message")

    # Open the sound file
    wf = wave.open(filename, 'rb')

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather than recorded
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks
    data = wf.readframes(chunk)

    # Play the sound by writing the audio data to the stream
    while data != '':
        stream.write(data)
        data = wf.readframes(chunk)
        if len(data) == 0:
            break

    # Close and terminate the stream
    stream.close()
    p.terminate()
    print("message done")

imageStringEncoded = process()
write_to_file(imageStringEncoded)
play_message()
