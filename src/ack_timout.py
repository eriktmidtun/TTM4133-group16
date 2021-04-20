

class ackTimeout:

    def message_heard(self):
        pass



ack_timeout = ackTimeout()

# TRANSITIONS
t0 = {'source': 'initial',
     'target' : 'idle'}

t1 = {'trigger': 'listen',
    'source': 'idle',
    'target' : 'listen_heard_messages'}

t2 = {'trigger': 'message_heard',
    'source': 'listen_heard_messages',
    'target': 'idle'}

t3 = {'trigger': 't',
    'source': 'listen_heard_messages',
    'target': 'idle',
    'effect': 'play_error'}

# STATES
idle = {'name': 'idle'}

listen_heard_messages = {'name': 'listen_heard_messages',
    'entry': 'start_timer("t",2000)',
    'exit': 'stop_timer("t")'}



machine = Machine(name='ack_timeout', transitions=[
                  t0, t1, t2], obj=ack_timeout, states=[idle, listen_heard_messages])
signal.stm = machine


