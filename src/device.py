import stmpy
import paho.mqtt.client as mqtt
from playsound import playsound

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_CHANNEL_BASE = 'ttm4115/team_16/channel/'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_16/answer'


class Device(object):

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.channel = None

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
            "effect": "change_channel",
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
            "target": "reserve_channel_button",
        }

        t6 = {
            "trigger": "channel_unavailable",
            "source": "reserve_channel_button",
            "target": "idle",
            "effect": "play_unavailable_sound",
        }

        t7 = {
            "trigger": "channel_reserved",
            "source": "reserve_channel_button",
            "target": "speaking_button",
        }

        t8 = {
            "trigger": "button_out",
            "source": "speaking_button",
            "target": "idle",
        }

        t9 = {
            "trigger": "over",
            "source": "speaking_voice",
            "target": "idle",
        }

        t10 = {
            "trigger": "channel_reserved",
            "source": "reserve_channel_voice",
            "target": "speaking_voice",
        }

        t11 = {
            "trigger": "wake_word",
            "source": "idle",
            "target": "reserve_channel_voice",
        }

        t12 = {
            "trigger": "channel_unavailable",
            "source": "reserve_channel_voice",
            "target": "idle",
            "effect": "play_unavailable_sound",
        }

        t13 = {
            "trigger": "change_channel",
            "source": "idle",
            "target": "idle",
            "effect": "change_channel",
        }

        t14 = {
            "trigger": "switch_off",
            "source": "idle",
            "target": "off",
        }

        """ control states """
        off = {'name': 'off'}

        no_channel = {'name': 'no_channel'}

        idle = {'name': 'idle',
                'entry': 'receiver(on)'}

        reserve_channel_voice = {'name': 'reserve_channel_voice',
                                 'entry': 'channel_availability(); reserve_channel()'}

        reserve_channel_button = {'name': 'reserve_channel_buttton',
                                  'entry': 'channel_availability(); reserve_channel()'}
        speaking_voice = {'name': 'speaking_voice',
                          'entry': 'receiver(off);start_stream_audio();',
                          'exit': 'stop_stream_audio();release_channel();ack_timout("listen")'}

        speaking_button = {'name': 'speaking_button',
                           'entry': 'receiver(off);start_stream_audio();',
                           'exit': 'stop_stream_audio();release_channel();ack_timout("listen")'}

        self.stm = stmpy.Machine(name="Device" transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14],
                                 states=[off, no_channel, idle, reserve_channel_voice, reserve_channel_button, speaking_voice, speaking_button])

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
        pass

    def reserve_channel(self):
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
        pass

    def play_unavailable_sound(self):
        playsound("./assets/audio/unavailable_sound.mp3")
