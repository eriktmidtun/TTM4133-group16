import PySimpleGUI as sg

sg.theme('DarkBlue')
layout = [[sg.Text('Choose channel to subscribe to', key='_TextBox_',font=('Helvetica',20) )],
          [sg.Slider(range=(1, 10),
                     default_value=5,
                     size=(600, 25),
                     orientation='horizontal',
                     font=('Helvetica', 20))],
          [sg.Button('Subscribe to channel',font=('Helvetica',20)), sg.Button('Unsubscribe',font=('Helvetica',20))],
          # TODO: gjør den til en toggle button eller legg til en button til. Kan ikke skru av snakking nå
          [sg.Button('Push to talk',font=('Helvetica',20))],
          [sg.Button('Power off', font=('Helvetica',20))]]
window = sg.Window('Braze device', layout, size=(1000,500))

channel = ''
oldChannel = ''
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Power off':  # if user closes window or clicks cancel
        break
    if event == 'Subscribe to channel':
        channel = str(int(values[0]))
        print('You are subscribed to channel ' + channel)
        window['_TextBox_'].update('You are subscribed to channel ' + channel)
        # driver.send("subscribe_channel","device", kwargs("channel" : channel))

    if event == 'Unsubscribe':
        oldChannel = str(int(values[0]))
        print('You are unsubscribed from channel ', oldChannel)
        window['_TextBox_'].update('No active subscriptions')
        # driver.send("unsubscribe_channel","device")
    if event == 'Push to talk':
        print('Talk')

window.close()
