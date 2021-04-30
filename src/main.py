import stmpy
import paho.mqtt.client as mqtt
import time
import PySimpleGUI as sg
import logging

from device import Device
from play_sound import play_sound 
#from recorder import Recorder
from voice_recognizer import VoiceRecognizer
from receiver import Receiver
#from ack_timout import AckTimeout

""" GUI """
sg.theme('DarkBlue')
button_subscribe = sg.Button('Subscribe to channel',font=('Helvetica',20))
button_unsubscribe = sg.Button('Unsubscribe', disabled=True, font=('Helvetica',20))
button_in = sg.Button('Button_in', disabled=True, font=('Helvetica',20))
button_out= sg.Button('Button_out', disabled=True, font=('Helvetica',20))

layout = [[sg.Text('Choose channel to subscribe to', key='_TextBox_',font=('Helvetica',20) )],
          [sg.Slider(range=(1, 10),
                     default_value=5,
                     size=(600, 25),
                     orientation='horizontal',
                     font=('Helvetica', 20))],
          [button_subscribe, button_unsubscribe],
          [button_in, button_out],
          [sg.Button('Power off', font=('Helvetica',20))],
          [sg.Button('Message', font=('Helvetica',20))]]
window = sg.Window('Braze device', layout, size=(1000,500))


""" Setup """
mqtt_client = mqtt.Client()
main_driver = stmpy.Driver()
second_driver = stmpy.Driver()
device = Device(main_driver, second_driver)
#recorder = Recorder()  
#receiver = Receiver(mqtt_client)
#ackTimeout = AckTimeout(mqtt_client)

voicerecognizer = VoiceRecognizer(main_driver)

main_driver.add_machine(device.stm)
#main_driver.add_machine(recorder.stm)
#main_driver.add_machine(receiver.stm)
#second_driver.add_machine(voicerecognizer.stm)

def application(main_driver, second_driver):
    # logging.DEBUG: Most fine-grained logging, printing everything
    # logging.INFO:  Only the most important informational log items
    # logging.WARN:  Show only warnings and errors.
    # logging.ERROR: Show only error messages.
    debug_level = logging.DEBUG
    logger = logging.getLogger(__name__)
    logger.setLevel(debug_level)
    ch = logging.StreamHandler()
    ch.setLevel(debug_level)
    formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    channel = ''
    oldChannel = ''
    main_driver.start(keep_active=True)
    second_driver.start(keep_active=True)
    main_driver.send("switch_on", "device")
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Power off':  # if user closes window or clicks cancel
            break
        if event == 'Subscribe to channel':
            channel = str(int(values[0]))
            main_driver.send("subscribe_channel", "device",
                        kwargs=({"channel": channel}))
            button_in.update(disabled=False)
            button_unsubscribe.update(disabled=False)
            if device.get_channel() != None:
                print('You are subscribed to channel ' + channel)
                window['_TextBox_'].update(
                    'You are subscribed to channel ' + channel)

        if event == 'Unsubscribe':
            oldChannel = str(int(values[0]))
            print('You are unsubscribed from channel ', oldChannel)
            window['_TextBox_'].update('No active subscriptions')
            main_driver.send("unsubscribe_channel", "device")
            button_in.update(disabled=True)
            button_unsubscribe.update(disabled=True)

        if event == 'Button_in':
            main_driver.send("button_in", "device",
                        kwargs=({"message": "off"}))
            button_in.update(disabled=True)
            button_out.update(disabled=False)
        if event == 'Button_out':
            main_driver.send("button_out", "device")
            button_in.update(disabled=False)
            button_out.update(disabled=True)
        if event == 'Message':
            play_sound('output.wav')
            #main_driver.send("message", "receiver")
    main_driver.stop()
    second_driver.stop()
    window.close()

application(main_driver,second_driver)
