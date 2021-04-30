import stmpy
import paho.mqtt.client as mqtt
from play_sound import play_sound
import json
import logging
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

        """ control states """
        off = {'name': 'off',
               'entry': "state('off')"}

        no_channel = {'name': 'no_channel',
                      'entry': "state('no_channel')"}

        idle = {'name': 'idle',
                'entry': 'state("idle");receiver("on");voice_recognizer("wake")'}

        reserve_channel = {'name': 'reserve_channel',
                           'entry': 'state("reserve_channel");channel_availability(); reserve_channel()'}

        speaking = {'name': 'speaking',
                    'entry': 'state("speaking");start_stream_audio();receiver("off");',
                    'exit': 'stop_stream_audio();release_channel();ack_timout("listen")'}

        self.stm = stmpy.Machine(name=self.name, transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12],
                                 states=[off, no_channel, idle, reserve_channel, speaking], obj=self)

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
        return True  # TODO fix this
        if not self.component.is_channel_available():
            self.stm.send('channel_unavailable')
            return False

    def reserve_channel(self):
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

    def play_unavailable_sound(self):
        try:
            print("error sound")
            play_sound("./src/assets/audio/error_sound.wav")
        except:
            print("Error sound could not be played")

    def state(self, state):
        if not state:
            return
        print("DEVICE state: {}".format(state))


class Device(object):

    def __init__(self, driver, second_driver):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        #self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_unsubscribe = self.on_unsubscribe
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.loop_start()
        self.driver = driver
        self.device = DeviceLogic(self)
        self.stm = self.device.stm
        self.second_driver = second_driver
        self.channel = None
        self.channel_available = False
        self._logger = logging.getLogger(__name__)
        self.recorder = Recorder(self.mqtt_client, self)
        self.receiver = Receiver(self)
        self.driver.add_machine(self.recorder.stm)
        self.driver.add_machine(self.receiver.stm)

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
        client.message_callback_add(self.make_topic_string(
            "/audio"), self.receiver.on_audio_message)
        self._logger.debug('MQTT subsribed to {}'.format(
            self.make_topic_string("/#")))

    def on_unsubscribe(self, client, userdata, mid):
        client.message_callback_remove(self.make_topic_string("/reserve"))
        client.message_callback_remove(self.make_topic_string("/audio"))
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

    def on_message(self, client, userdata, msg):
        print("on_message: ", "userdata", userdata, "\nmsg", msg)
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            print(payload)
        except Exception as err:
            print('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(
                msg.topic, err))

    def publish_message(self, topic, data, retain=False):
        payload = json.dumps(data)
        self.mqtt_client.publish(topic, payload=payload, qos=2, retain=retain)

    def make_topic_string(self, sub_topic, channel=None):
        if not channel:
            return MQTT_TOPIC_CHANNEL_BASE + str(self.get_channel()) + sub_topic
        return MQTT_TOPIC_CHANNEL_BASE + str(channel) + sub_topic
