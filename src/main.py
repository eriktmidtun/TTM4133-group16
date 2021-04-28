import stmpy
import paho.mqtt.client as mqtt
import time
import PySimpleGUI as sg

from device import Device
from recorder import Recorder
from voice_recognizer import VoiceRecognizer
#from receiver import Receiver
#from ack_timout import AckTimeout

""" GUI """
sg.theme('DarkBlue')
layout = [[sg.Text('Choose channel to subscribe to', key='_TextBox_')],
          [sg.Slider(range=(1, 10),
                     default_value=5,
                     size=(600, 25),
                     orientation='horizontal',
                     font=('Helvetica', 12))],
          [sg.Button('Subscribe to channel'), sg.Button('Unsubscribe')],
          # TODO: gjør den til en toggle button eller legg til en button til. Kan ikke skru av snakking nå
          [sg.Button('Push to talk',font=('Helvetica',20))],
          [sg.Button('Power off', font=('Helvetica',20))]]
window = sg.Window('Braze device', layout, size=(600,400))


""" Setup """
mqtt_client = mqtt.Client()
driver = stmpy.Driver()
device = Device(driver)
recorder = Recorder()
recorder = Recorder()
voicerecognizer = VoiceRecognizer()
#receiver = Receiver(mqtt_client)
#ackTimeout = AckTimeout(mqtt_client)

driver.add_machine(device.stm)
driver.add_machine(voicerecognizer.stm)
driver.add_machine(recorder.stm)
# driver.add_machine(receiver.stm)

def application(driver):
    channel = ''
    oldChannel = ''
    driver.start(keep_active=True)
    driver.send("switch_on", "device")
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Power off':  # if user closes window or clicks cancel
            break
        if event == 'Subscribe to channel':
            channel = str(int(values[0]))
            print('You are subscribed to channel ' + channel)
            window['_TextBox_'].update(
                'You are subscribed to channel ' + channel)
            driver.send("subscribe_channel", "device",
                        kwargs=({"channel": channel}))

        if event == 'Unsubscribe':
            oldChannel = str(int(values[0]))
            print('You are unsubscribed from channel ', oldChannel)
            window['_TextBox_'].update('No active subscriptions')
            driver.send("unsubscribe_channel", "device")
        if event == 'Push to talk':
            print('Talk')
            driver.send("button_in", "device",
                        kwargs=({"message": "off"}))
    driver.stop()
    window.close()


application(driver)
