from stmpy import Driver, Machine
import pyaudio
import wave
from play_sound import play_sound
import base64 
import json


class Receiver:
    def __init__(self, device):

        # DEFINING THE TRANSITIONS
        t0 = {'source': 'initial',
              'target': 'receiver_off'}

        # playing voice message
        t1 = {'trigger': 'message',
              'source': 'receiver_on',
              'target': 'play_voice_message'}

        # confirm voice message is done playing
        t2 = {'trigger': 'message_done',
              'source': 'play_voice_message',
              'target': 'receiver_on'}

        # error when receiving voice message
        t3 = {'trigger': 'error',
              'source': 'play_voice_message',
              'target': 'receiver_on',
              'effect': 'play_error_sound'}

        # turn off
        t3 = {'trigger': 'off',
              'source': 'receiver_on',
              'target': 'receiver_off'}

        # turn on
        t4 = {'trigger': 'on',
              'source': 'receiver_off',
              'target': 'receiver_on'}

        # DEFINING THE STATES
        receiver_off = {
            'name': 'receiver_off',
            'entry': 'state("receiver_off")'
        }

        receiver_on = {
            'name': 'receiver_on',
            'entry': 'state("receiver_on")'
        }

        play_voice_message = {
            'name': 'play_voice_message',
            'entry': 'state("play_voice_message");play_message()'
        }

        self.stm = Machine(name='receiver', transitions=[t0, t1, t2, t3, t4], obj=self,
                           states=[receiver_on, receiver_off, play_voice_message])

    def on_audio_message(self, client, userdata, msg):
        """ print("RECEIVER on_audio_message")
        filename = 'input.wav'
        print(msg.topic, msg.payload)
        try:
            payload = json.loads(msg.payload)
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
        self.stm.send("message") 
         data = msg.payload

        bytearr = bytearray(data)
        print("decoded") """
        f = open("input.wav", 'wb')
        f.write(msg.payload)
        f.close()
        print("RECEIVER: audio written")
        self.stm.send("message")
        print("message sent")

    def play_message(self):
        filename = 'input.wav'
        print("RECEIVER: Trying to play incoming message")

        # Set chunk size of 1024 samples per data frame
        chunk = 1024

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
        
        self.stm.send('message_done')
        print("message done")

    def play_error_sound(self):
        play_sound("./src/assets/audio/error_sound.mp3")

    def state(self, state):
        if not state:
            return
        print("RECEIVER state: {}".format(state))
