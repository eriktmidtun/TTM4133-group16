import stmpy
import paho.mqtt.client as mqtt
from playsound import playsound
import json

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_CHANNEL_BASE = 'ttm4115/team_16/channel/'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_16/answer'


class DeviceLogic(object):

    def __init__(self, component):
        self.component = component
        self.channel = None
        self.channel_available = False

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
            "effect": "voice_recognizer('off')",
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
            "effect": "voice_recognizer('end')",
        }

        t11 = {
            "trigger": "change_channel",
            "source": "idle",
            "target": "idle",
            "effect": "change_channel",
        }

        t12 = {
            "trigger": "switch_off",
            "source": "idle",
            "target": "off",
        }

        """ control states """
        off = {'name': 'off'}

        no_channel = {'name': 'no_channel'}

        idle = {'name': 'idle',
                'entry': 'receiver(on);voice_recognizer("wake")'}

        reserve_channel = {'name': 'reserve_channel',
                           'entry': 'channel_availability(); reserve_channel()'}

        speaking = {'name': 'speaking',
                    'entry': 'receiver(off);start_stream_audio();',
                    'exit': 'stop_stream_audio();release_channel();ack_timout("listen")'}

        self.machine = stmpy.Machine(name="Device" transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12],
                                     states=[off, no_channel, idle, reserve_channel, speaking])

    def change_channel(self):
        new_channel = 1  # TODO hent channel fra UI
        if not self.channel:
            self.channel = new_channel
            return self.mqtt_client.subscribe(MQTT_TOPIC_CHANNEL_BASE + str(new_channel) + "/#")
        old_topic = MQTT_TOPIC_CHANNEL_BASE + str(self.channel) + "/#"
        self.unsubscribe_channel()
        self.channel = new_channel
        return self.mqtt_client.subscribe(MQTT_TOPIC_CHANNEL_BASE + str(new_channel) + "/#")

    def unsubscribe_channel(self):
        channel_topic = MQTT_TOPIC_CHANNEL_BASE + str(self.channel) + "/#"
        self.mqtt_client.unsubscribe(channel_topic)

    def channel_availability(self):
        reserve_topic = MQTT_TOPIC_CHANNEL_BASE + \
            str(self.channel) + "/reserve"
        if self.channel_unavailable:
            self.machine.send('channel_unavailable')
            return False
        return True

    def reserve_channel(self):
        reserve_topic = MQTT_TOPIC_CHANNEL_BASE + \
            str(self.channel) + "/reserve"
        if self.channel_availability()
        self.mqtt_client.publish(reserve_topic, payload="")
        pass

    def release_channel(self):
        pass

    def receiver(self, message):
        pass

    def start_stream_audio(self):
        pass

    def stop_stream_audio(self):
        pass

    def ack_timout(self, message):
        if message != "listen"
        return  # Error
        self.driver.send("")

    def voice_recognizer(self, message):
        self.driver.send("")

    def play_unavailable_sound(self):
        playsound("./assets/audio/unavailable_sound.mp3")


class Device(object):

    def __init__(self, mqtt_client, driver):
        self.mqtt_client = mqtt_client
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.driver = driver
        self.stm = DeviceLogic(self)
        driver.add_machine(self.stm.machine)

    def on_connect(self):
        print("connected")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(
                msg.topic, err))
            return

    def publish_message(self, data):
        payload = json.dumps(data)
        self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)
