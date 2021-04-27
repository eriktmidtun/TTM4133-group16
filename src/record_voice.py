import speech_recognition as sr
import time

def recognize_speech_from_mic(recognizer, mic):
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


if __name__ == "__main__":
  r = sr.Recognizer()
  mic = sr.Microphone(device_index=1)
  print('Say something')
  time.sleep(1)
  PROMPT_LIMIT = 2
  over = False

  while not over:
    for i in range(PROMPT_LIMIT):
      print('Now')
      output = recognize_speech_from_mic(r, mic)
      if (output['transcription']):
        break
      if not output['success']:
        break
      print("Didnt catch end word. Try again")

    if output['error']:
      print("ERROR: {}".format(output["error"]))

    print("You said: {}".format(output["transcription"]))
    end_word = output["transcription"].lower().split()[-1] == "over"
    if end_word:
      over = True
      break
    else:
      print("Not ended yet")