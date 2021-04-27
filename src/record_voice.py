import speech_recognition as sr
from stmpy import Driver, Machine
import time
class VoiceRecognizer:
    def __init__(self): #), device):
        self.over = False
        self.r = sr.Recognizer()
        self.mic = sr.Microphone(device_index=1)
        # self.device_driver = device_driver

        t0 = {'source': 'initial',
              'target': 'recognizer_off'}
        t1 = {'trigger': 'on',
              'source': 'recognizer_off',
              'target': 'recognizer_on',
              'effect': 'check_for_word(*)'}
        t2 = {'trigger': 'off',
              'source': 'recognizer_on',
              'target': 'recognizer_off'}

        recognizer_off = {
            'name': 'recognizer_off',
            'entry': 'turn_off'
        }
        recognizer_on = {
            'name': 'recognizer_on',
        }

        self.machine = Machine(name="voice_recognizer", transitions=[t0, t1, t2], obj=self,
                                     states=[recognizer_off, recognizer_on])

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

    def check_for_word(self, word):
        print('Say something')
        time.sleep(1)
        PROMPT_LIMIT = 2
        print(self.over)
        while not self.over:
            for i in range(PROMPT_LIMIT):
                print('Now')
                output = self.recognize_speech_from_mic(self.r, self.mic)
                if output['transcription']:
                    break
                if not output['success']:
                    break
                print("Didn't catch the word. Try again")

            if output['error']:
                print("ERROR: {}".format(output["error"]))

            print("You said: {}".format(output["transcription"]))
            transcript = output["transcription"]
            if word in transcript:
                self.over = True
                print("Ended")
                break
            else:
                print("Not ended yet")

    def turn_off(self):
        self.over = False

# VoiceRecognizer = VoiceRecognizer()
# driver = Driver()
# driver.add_machine(VoiceRecognizer.machine)
# driver.start()
# time.sleep(2)
# driver.send("on", "voice_recognizer", kwargs={"word":"over"})