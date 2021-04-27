import speech_recognition as sr
import time
class VoiceRecognizer:
    def __init__(self, device):
        self.over = False
        self.r = sr.Recognizer()
        self.mic = sr.Microphone(device_index=1)
        self.device_driver = device_driver

        t0 = {'source': 'initial'
              'target': 'off'}
        t1 = {'trigger': 'on'
              'source': 'recognizer_off'
              'target': 'recognizer_on',
              'effect': 'check_for_word(*)'}
        t2 = {'trigger': 'off'
              'source': 'recognizer_on'
              'target': 'recognizer_off'}

        recognizer_off = {
            'name': 'recognizer_off',
            'entry': 'turn_off'
        }
        recognizer_on = {
            'name': 'recognizer_on',
            'entry': 'check_for_word()'
        }

        self.machine = stmpy.Machine(name="voice_recognizer" transitions=[t0, t1, t2],
                                     states=[off, recognizer_off, recognizer_on])

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
        while not over:
            for i in range(PROMPT_LIMIT):
                print('Now')
                output = recognize_speech_from_mic(self.r, self.mic)
                if output['transcription']:
                    break
                if not output['success']:
                    break
                print("Didnt catch end word. Try again")

            if output['error']:
                print("ERROR: {}".format(output["error"]))

            print("You said: {}".format(output["transcription"]))
            transcript = output["transcription"].lower()
            if word.lower() in transcript:
                self.turn_off()
                break
            else:
                print("Not ended yet")

    def turn_off(self):
        self.over = True
