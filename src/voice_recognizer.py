import speech_recognition as sr
from stmpy import Driver, Machine
import time
import pyaudio


class VoiceRecognizer:

    def __init__(self, device_driver, wake_word="google", end_word="over"):
        self.over = False
        self.r = sr.Recognizer()
        self.mic = sr.Microphone(device_index=choose_from_available_devices())
        self.device_driver = device_driver

        t0 = {'source': 'initial',
              'target': 'recognizer_off'}
        t1 = {'trigger': 'wake',
              'source': 'recognizer_off',
              'target': 'recognizer_on_wake', }
        t2 = {'trigger': 'wake',
              'source': 'recognizer_on_end',
              'target': 'recognizer_on_wake', }
        t3 = {'trigger': 'end',
              'source': 'recognizer_off',
              'target': 'recognizer_on_end', }
        t4 = {'trigger': 'end',
              'source': 'recognizer_on_wake',
              'target': 'recognizer_on_end', }
        t5 = {'trigger': 'off',
              'source': 'recognizer_on_end',
              'target': 'recognizer_off'}
        t6 = {'trigger': 'off',
              'source': 'recognizer_on_wake',
              'target': 'recognizer_off'}

        recognizer_off = {
            'name': 'recognizer_off',
            'entry': 'state("recognizer_off");turn_off',
            'exit': 'turn_on'
        }
        recognizer_on_end = {
            'name': 'recognizer_on_end',
            'entry': 'state("recognizer_on_end");check_for_word("' + end_word + ' ", "over")'
        }

        recognizer_on_wake = {
            'name': 'recognizer_on_wake',
            'entry': 'state("recognizer_on_wake");check_for_word("' + wake_word + '","wake_word")'
        }

        self.stm = Machine(name="voice_recognizer", transitions=[t0, t1, t2, t3, t4, t5, t6], obj=self,
                           states=[recognizer_off, recognizer_on_wake, recognizer_on_end])

    def recognize_speech_from_mic(self, recognizer, mic):
        if not isinstance(recognizer, sr.Recognizer):
            raise TypeError('`recognizer` must be `Recognizer` instance')

        if not isinstance(mic, sr.Microphone):
            raise TypeError('`microphone` must be a `Microphone` instance')

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            # r.adjust_for_ambient_noise(source, duration=0.5)

        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            response["transcription"] = recognizer.recognize_google(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"

        return response

    def check_for_word(self, word, trigger):
        print('VOICERECOGNIZER', 'Say something')
        time.sleep(1)
        PROMPT_LIMIT = 2
        print('VOICERECOGNIZER', self.over)
        while not self.over:
            for i in range(PROMPT_LIMIT):
                print('VOICERECOGNIZER', 'Now')
                output = self.recognize_speech_from_mic(self.r, self.mic)
                if output['transcription']:
                    break
                if not output['success']:
                    break
                print('VOICERECOGNIZER', "Didn't catch the word. Try again")

            if output['error']:
                print('VOICERECOGNIZER', "ERROR: {}".format(output["error"]))

            print('VOICERECOGNIZER', "You said: {}".format(
                output["transcription"]))
            transcript = output["transcription"]
            if word.lower() in str(transcript).lower():
                self.over = True
                print('VOICERECOGNIZER', "Ended")
                self.device_driver.send(
                    trigger, "device", kwargs=({"message": word}))
                self.stm.send("off")
                break
            else:
                print('VOICERECOGNIZER', "Not ended yet")

    def turn_off(self):
        self.over = True

    def turn_on(self):
        self.over = False

    def state(self, state):
        if not state:
            return
        print("VOICERECOGNIZER state: {}".format(state))


def print_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print('VOICERECOGNIZER', "Input Device id ", i, " - ",
                  p.get_device_info_by_host_api_device_index(0, i), "\n")

def choose_from_available_devices(index=0):
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    devices = []
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            devices.append(i)
    print("using device ", p.get_device_info_by_host_api_device_index(0, index))
    return devices[index]


""" VoiceRecognizer = VoiceRecognizer()
print_devices()
driver = Driver()
driver.add_machine(VoiceRecognizer.stm)
driver.start()
time.sleep(2)
driver.send("end", "voice_recognizer", kwargs={"word":"over"}) """
