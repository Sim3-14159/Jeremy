from modules import *
from modules.movement import MovementController
MovementController = MovementController()

import os
import subprocess
import random
import argparse

from requests.exceptions import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument("--image-path", default="image.jpg")
args = parser.parse_args()

stt = stt.VoskSTT()
ai = ai.OpenAIAI()
tts = tts.PiperTTS()

while True:
    try:
        print("\033[35mWaiting for 'Hey Jeremy' to be said...\033[0m")
        text = stt.wait_for_phrase("hey jeremy", "hi jeremy", "hello jeremy", 'jeremy')
        print(f"\033[35mHeard:\033[36m {text}\033[0m")
        
        subprocess.run(["aplay", "responses/initial/" + random.choice(os.listdir("responses/initial/"))])

        print("\033[35mListening for your question...\033[0m")
        text = stt.listen()
        image = camera.capture_image(args.image_path)

        print(f"\033[35mYou said:\033[36m {text}\033[0m")
        response = ai.ask(text, image_path=args.image_path)
        print(f"\033[35mAI response:\033[36m {response['message']}\033[0m")
        print(f"\033[35mAI code:\033[0m {response['code']}")
        tts.speak(response["message"])
        exec(response["code"])

    except HTTPError as e: # if it's an HTTPError, it's probably just Pollinations API being dumb, so it can be ignored and moved on from
        print(f"\033[35mDumb network error (ignoring):\033[36m {e}\033[0m")
        tts.speak(f"Huh, it looks like there was a network error. The code raised an HTTPError with status code {e.response.status_code}. Here are some details:")
        for attr in dir(e):
            if not attr.startswith("__"):
                tts.speak(f"\t{attr}: {getattr(e, attr)}")
    
    except KeyboardInterrupt:
        print("\033[35mExiting...\033[0m")
        break

    except Exception as e:
        print(f"An error occurred: {e}")
        tts.speak(f"Huh, something went wrong. It looks like the code raised a {e}. Here are some details:")
        for attr in dir(e):
            if not attr.startswith("__"):
                if not callable(getattr(e, attr)):
                    tts.speak(f"\t{attr}: {getattr(e, attr)}")
        
        raise e # if it's not an HTTPError, re-raise it so we can see the full traceback and fix the bug