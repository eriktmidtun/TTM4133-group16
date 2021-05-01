import stmpy
import paho.mqtt.client as mqtt
import time
import PySimpleGUI as sg
import logging
import sys

from device import Device
from play_sound import play_sound
from voice_recognizer import VoiceRecognizer

""" GUI """
sg.theme('DarkBlue')
button_subscribe = sg.Button('Subscribe to channel', font=('Helvetica', 20))
button_unsubscribe = sg.Button(
    'Unsubscribe', disabled=True, font=('Helvetica', 20))
button_in = sg.Button('Button_in', disabled=True, font=('Helvetica', 20))
button_out = sg.Button('Button_out', disabled=True, font=('Helvetica', 20))

layout = [[sg.Text('Choose channel to subscribe to', key='_TextBox_', font=('Helvetica', 20))],
          [sg.Slider(range=(1, 10),
                     default_value=5,
                     size=(600, 25),
                     orientation='horizontal',
                     font=('Helvetica', 20),
                     enable_events=True,
                     key='slider')],
          [button_subscribe, button_unsubscribe],
          [button_in, button_out],
          [sg.Button('Power off', font=('Helvetica', 20))],
          [sg.Button('Message', font=('Helvetica', 20))]]
window = sg.Window('Braze device', layout, size=(1000, 500))

device_id = 0
if len(sys.argv) > 1:
    device_id = sys.argv[1]

""" Setup """
mqtt_client = mqtt.Client()
main_driver = stmpy.Driver()
second_driver = stmpy.Driver()
device = Device(main_driver, second_driver, device_id)

voicerecognizer = VoiceRecognizer(main_driver)

main_driver.add_machine(device.stm)
# commend out the line under to disable voice recognizion
second_driver.add_machine(voicerecognizer.stm)


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
    formatter = logging.Formatter(
        '%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    channel = ''
    main_driver.start(keep_active=True)
    second_driver.start(keep_active=True)
    main_driver.send("switch_on", "device")
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        window.refresh()
        if event == sg.WIN_CLOSED or event == 'Power off':  # if user closes window or clicks cancel
            break
        if event == 'Subscribe to channel':
            channel = str(int(values['slider']))
            main_driver.send("subscribe_channel", "device",
                             kwargs=({"channel": channel}))
            button_in.update(disabled=False)
            button_unsubscribe.update(disabled=False)
            button_subscribe.update(disabled=True)
            button_unsubscribe.update('Unsubscribe to channel ' + channel)
            if device.get_channel() != None:
                window['_TextBox_'].update(
                    'Subscribed to channel ' + channel)

        if event == 'slider':
            channel = str(int(values['slider']))
            button_subscribe.update(disabled=False)
            button_subscribe.update('Subscribe to channel ' + channel)

        if event == 'Unsubscribe':
            window['_TextBox_'].update('No active subscriptions')
            main_driver.send("unsubscribe_channel", "device")
            button_in.update(disabled=True)
            button_unsubscribe.update(disabled=True)
            button_subscribe.update(disabled=False)
            button_unsubscribe.update('Unsubscribe')

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
    main_driver.stop()
    second_driver.stop()
    window.close()


application(main_driver, second_driver)
