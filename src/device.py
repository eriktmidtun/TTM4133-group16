import stmpy
import paho.mqtt.client as mqtt
from play_sound import play_sound
import json
import logging
import pyaudio
import wave
from recorder import Recorder
from receiver import Receiver

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_CHANNEL_BASE = 'ttm4115/team_16/test/channel/'


class DeviceLogic(object):

    def __init__(self, component, name="device", id=1):
        self.component = component
        self.name = name
        self.id = id
        self._logger = logging.getLogger(__name__)
        print("DEVICE id", self.id)

        """ transitions """
        t0 = {
            "source": "initial",
            "target": "off",
        }

        t1 = {
            "trigger": "switch_on",
            "source": "off",
            "target": "no_channel",
        }

        t2 = {
            "trigger": "switch_off",
            "source": "no_channel",
            "target": "off",
        }

        t3 = {
            "trigger": "subscribe_channel",
            "source": "no_channel",
            "target": "idle",
            "effect": "change_channel(*)",
        }

        t4 = {
            "trigger": "unsubscribe_channel",
            "source": "idle",
            "target": "no_channel",
            "effect": "unsubscribe_channel",
        }

        t5 = {
            "trigger": "button_in",
            "source": "idle",
            "target": "reserve_channel",
            "effect": "voice_recognizer(*)",  # off
        }

        t6 = {
            "trigger": "channel_unavailable",
            "source": "reserve_channel",
            "target": "idle",
            "effect": "play_unavailable_sound",
        }

        t7 = {
            "trigger": "channel_reserved",
            "source": "reserve_channel",
            "target": "speaking",
            "effect": "play_success_sound",
        }

        t8 = {
            "trigger": "button_out",
            "source": "speaking",
            "target": "idle",
        }

        t9 = {
            "trigger": "over",
            "source": "speaking",
            "target": "idle",
            "effect": "play_success_sound",
        }

        t10 = {
            "trigger": "wake_word",
            "source": "idle",
            "target": "reserve_channel",
            "effect": "voice_recognizer(*)",  # end
        }

        t11 = {
            "trigger": "subscribe_channel",
            "source": "idle",
            "target": "idle",
            "effect": "change_channel(*)",
        }

        t12 = {
            "trigger": "switch_off",
            "source": "idle",
            "target": "off",
        }

        t13 = {'trigger': 'message',
              'source': 'idle',
              'target': 'play_voice_message'}

        # confirm voice message is done playing
        t14 = {'trigger': 'message_done',
              'source': 'play_voice_message',
              'target': 'idle'}

        # error when receiving voice message
        t15 = {'trigger': 'error',
              'source': 'play_voice_message',
              'target': 'idle',
              'effect': 'play_error_sound'}


        """ control states """
        off = {'name': 'off',
               'entry': "state('off')"}

        no_channel = {'name': 'no_channel',
                      'entry': "state('no_channel')"}

        idle = {'name': 'idle',
                'entry': 'state("idle");voice_recognizer("wake")'}

        reserve_channel = {'name': 'reserve_channel',
                           'entry': 'state("reserve_channel");channel_availability(); reserve_channel()'}

        speaking = {'name': 'speaking',
                    'entry': 'state("speaking");start_stream_audio();receiver("off");',
                    'exit': 'stop_stream_audio();release_channel();ack_timout("listen")'}
        play_voice_message = {
            'name': 'play_voice_message',
            'entry': 'state("play_voice_message");play_message()'
        }

        self.stm = stmpy.Machine(name=self.name, transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14,t15 ],
                                 states=[off, no_channel, idle, reserve_channel, speaking, play_voice_message], obj=self)

    def change_channel(self, channel):
        new_channel = channel
        if not new_channel:
            print("no channel given")
            return
        self.unsubscribe_channel()
        self.component.set_channel(new_channel)
        self.component.mqtt_client.subscribe(
            self.component.make_topic_string("/#", channel=new_channel))
        return

    def unsubscribe_channel(self):
        if self.component.get_channel() == None:
            return
        channel_topic = self.component.make_topic_string("/#")
        self.component.set_channel(None)
        self.component.mqtt_client.unsubscribe(channel_topic)

    def channel_availability(self):
        if self.component.is_channel_available():
            self.stm.send('channel_unavailable')
            return False
        return True

    def reserve_channel(self):
        """ if not self.channel_availability():
            return """
        reserve_topic = self.component.make_topic_string("/reserve")
        data = {"device_id": self.id, "reserved": True}
        self.component.publish_message(reserve_topic, data)  # , retain=True)
        self.stm.send("channel_reserved")
        print("self.stm.send('channel_reserved')")

    def release_channel(self):
        reserve_topic = self.component.make_topic_string("/reserve")
        data = {"device_id": self.id, "reserved": False}
        self.component.publish_message(reserve_topic, data, retain=True)

    def receiver(self, message):
        print("sendt on to receiver")
        self.component.driver.send(message, "receiver")

    def start_stream_audio(self):
        print("start_stream_audio")
        self.component.driver.send("start", "recorder")

    def stop_stream_audio(self):
        print("stop_stream_audio")
        self.stm.driver.send("done", "recorder")

    def ack_timout(self, message):
        if message != "listen":
            return  # Error
        self.stm.driver.send(message, "ack_timeout")
        return

    def voice_recognizer(self, message):
        print("DEVICE, voice_recognizer message : ", message)
        self.component.second_driver.send(message, "voice_recognizer")

    def play_message(self):
        filename = 'input.wav'
        print("RECEIVER: Trying to play incoming message")

        # Set chunk size of 1024 samples per data frame
        chunk = 1024
        try:
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
        except:
            self.stm.send('error')
        
    def play_unavailable_sound(self):
        try:
            print("error sound")
            play_sound("./src/assets/audio/error_sound.wav")
        except:
            print("Error sound could not be played")

    def play_success_sound(self):
        try:
            play_sound("./src/assets/audio/pling.wav")
        except:
            print("Success sound could not be played")


    def state(self, state):
        if not state:
            return
        print("DEVICE state: {}".format(state))


class Device(object):

    def __init__(self, driver, second_driver, device_id):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        #self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_unsubscribe = self.on_unsubscribe
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.loop_start()
        self.driver = driver
        self.device = DeviceLogic(self, id=device_id)
        self.stm = self.device.stm
        self.second_driver = second_driver
        self.channel = None
        self.channel_available = False
        self.has_channel = False
        self._logger = logging.getLogger(__name__)
        self.recorder = Recorder(self.mqtt_client, self)
        #self.receiver = Receiver(self)
        self.driver.add_machine(self.recorder.stm)
        #self.driver.add_machine(self.receiver.stm)

    def set_channel(self, channel):
        if channel == None:
            self.channel_available = False
        self.channel = channel

    def get_channel(self):
        return self.channel

    def is_channel_available(self):
        return self.channel_available

    def set_channel_availability(self, availability):
        self.channel_available = availability

    def on_connect(self, client, userdata, flags, rc):
        print("userdata", userdata, "\nflags", flags, "\nrc", rc)
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        client.message_callback_add(self.make_topic_string(
            "/reserve"), self.on_reserve_message)
        audiotopic = self.make_topic_string("/audio/+")
        print("Trying to make callback", audiotopic)
        client.message_callback_add(audiotopic, self.on_audio_message)
        self._logger.debug('MQTT subsribed to {}'.format(
            self.make_topic_string("/#")))

    def on_unsubscribe(self, client, userdata, mid):
        client.message_callback_remove(self.make_topic_string("/reserve"))
        client.message_callback_remove(self.make_topic_string("/audio/+"))
        self._logger.debug('MQTT unsubsribed from topic')

    def on_reserve_message(self, client, userdata, msg):
        self._logger.debug(
            'MQTT message on topic {} \n {}'.format(msg.topic, msg))
        print(msg.topic, msg.payload)
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(
                msg.topic, err))
        reserved = payload["reserved"]
        device_id = payload["device_id"]
        self.set_channel_availability(reserved)

    def on_audio_message(self, client, userdata, msg):
        print("on_audio_message" ,msg.topic, "payload size:", len(msg.payload))
        f = open("input.wav", 'wb')
        device_id = msg.topic.split("/")[-1]
        print("device_id", device_id)
        if str(device_id) != str(self.device.id):
            f.write(msg.payload)
            f.close()
            print("on_audio_message: audio written")
            self.stm.send("message")

    def on_message(self, client, userdata, msg):
        print("on_message: ", "userdata", userdata, "\nmsg", msg)

    def publish_message(self, topic, data, retain=False):
        payload = json.dumps(data)
        self.mqtt_client.publish(topic, payload=payload, qos=2, retain=retain)

    def make_topic_string(self, sub_topic, channel=None):
        if not channel:
            return MQTT_TOPIC_CHANNEL_BASE + str(self.get_channel()) + sub_topic
        return MQTT_TOPIC_CHANNEL_BASE + str(channel) + sub_topic
