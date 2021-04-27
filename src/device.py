import stmpy
import paho.mqtt.client as mqtt
from playsound import playsound
import json

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_CHANNEL_BASE = 'ttm4115/team_16/channel/'


class DeviceLogic(object):

    def __init__(self, component, name="device"):
        self.component = component
        self.channel = None
        self.channel_available = False
        self.name = name

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
            "target": "reserve_channel_voice",
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
                    'entry': 'state("speaking");receiver("off");start_stream_audio();',
                    'exit': 'stop_stream_audio();release_channel();ack_timout("listen")'}

        self.stm = stmpy.Machine(name=self.name, transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12],
                                 states=[off, no_channel, idle, reserve_channel, speaking], obj=self)

    def change_channel(self, channel):
        if not channel:
            return
        new_channel = channel
        if not self.channel:
            self.channel = new_channel
            return self.component.mqtt_client.subscribe(MQTT_TOPIC_CHANNEL_BASE + str(new_channel) + "/#")
        self.unsubscribe_channel()
        self.channel = new_channel
        return self.component.mqtt_client.subscribe(MQTT_TOPIC_CHANNEL_BASE + str(new_channel) + "/#")

    def unsubscribe_channel(self):
        channel_topic = MQTT_TOPIC_CHANNEL_BASE + str(self.channel) + "/#"
        self.component.mqtt_client.unsubscribe(channel_topic)

    def channel_availability(self):
        if not self.channel_available:
            self.component.driver.send('channel_unavailable', 'device')
            return False
        return True

    def reserve_channel(self):
        reserve_topic = MQTT_TOPIC_CHANNEL_BASE + \
            str(self.channel) + "/reserve"
        if self.channel_availability():
            self.component.publish_message(reserve_topic, payload="")
        pass

    def release_channel(self):
        pass

    def receiver(self, message):
        self.component.driver.send(message, "receiver")

    def start_stream_audio(self):
        pass

    def stop_stream_audio(self):
        pass

    def ack_timout(self, message):
        if message != "listen":
            return  # Error
        self.component.driver.send(message, "ack_timeout")
        return

    def voice_recognizer(self, message):
        self.component.driver.send(message, "voice_recognizer")

    def play_unavailable_sound(self):
        try:
            playsound("./assets/audio/unavailable_sound.mp3")
        except:
            print("Error sound could not be played")

    def state(self, state):
        if not state:
            return
        print("You are in state: {}".format(state))


class Device(object):

    def __init__(self, driver):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.driver = driver
        device = DeviceLogic(self)
        self.stm = device.stm
        # driver.add_machine(self.stm.machine)

    def on_connect(self):
        print("connected")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(
                msg.topic, err))
            return

    def publish_message(self, topic, data):
        payload = json.dumps(data)
        self.mqtt_client.publish(topic, payload=payload, qos=2)
