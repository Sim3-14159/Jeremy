from modules import *

import os
import subprocess
import random

stt = stt.VoskSTT()
ai = ai.PollinationsAI()
tts = tts.PiperTTS()

while True:
    print("Waiting for 'Hey Jeremy' to be said...")
    text = stt.wait_for_phrase("hey jeremy", "hi jeremy", "hello jeremy", 'jeremy')
    print(f"\tHeard: {text}")
    
    subprocess.run(["aplay", "responses/initial/" + random.choice(os.listdir("responses/initial/"))])

    print("\tListening for your question...")
    text = stt.listen()
    print(f"\tYou said: {text}")
    response = ai.ask(text)
    print(f"\tAI response: {response['message']}")
    tts.speak(response["message"])