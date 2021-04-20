from stmpy import Driver, Machine


class Receiver:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

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
        receiver_off{
            'name': 'receiver_off',
        }

        receiver_on{
            'name': 'receiver_on'
        }

        play_voice_message{
            'name': 'play_voice_message',
            'entry': 'play_message'
        }

        self.stm = Machine(name='receiver', transitions=[t0, t1, t2, t3, t4], obj=receiver,
                           states=[receiver_on, receiver_off, play_voice_message])

    def play_message(self):
        pass

    def play_error_sound(self):
        pass
