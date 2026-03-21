from modules.ai import *
from modules.stt import *
from modules.tts import *
from modules.movement import *
from modules.camera import capture_image

import os
import subprocess
import random
import argparse
import time
from pyrplidar import PyRPlidar
import json

from requests.exceptions import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument("--image-path", default="image.jpg")
args = parser.parse_args()

stt = VoskSTT()
ai = OpenAIAI()
tts = PiperTTS()
movement = MovementController()
lidar = PyRPlidar()   
lidar.connect(port="/dev/ttyUSB0", baudrate=460800, timeout=3)
lidar.set_motor_pwm(500)
time.sleep(2) # wait to initialize
scan_generator = lidar.force_scan()
#updating_scans = scan_generator()

response = {"completed_task": "yes"} # initialize task_completed so that we don't get an error when we try to check it before the first AI response is received

tts.speak("Initialization complete.")


scan_iter = scan_generator()

def get_scan_data():
    scan_data = {}

    count = 0
    MAX_POINTS = 360  # tweak as needed

    for scan in scan_iter:
        angle = int(scan.angle)
        distance = int(scan.distance)

        if -100 <= angle <= 100:
            scan_data[angle] = distance
            count += 1

        if count >= MAX_POINTS:
            return scan_data


# main loop
while True:
    try:
        # go in a non-name saying loop while the task isn't completed
        while response.get("completed_task", "yes") == "no":
            print(f"\033[35mListening...\033[0m")

            text = stt.listen()
            image = capture_image(args.image_path)

            print(f"\033[35mHeard:\033[36m {text}\033[0m")

            response = ai.ask(text, args.image_path, get_scan_data())

            ## +
            response = json.loads("{" + response["message"].split("{")[1]) # in case if the AI puts its JSON inside of its response
            message = response.get("message", None)            
            code = response.get("code", None)
            completed_task = response.get
            ## ~

            # temp is used because, prior to Python 3.12, you can't use escape sequences within the { and } of an f-string
            temp = "\033[31m(no message returned)" 
            print(f"\033[35mAI response:\033[36m {response.get('message', temp)}\033[0m")

            temp = "\033[31m(no code returned)"
            print(f"\033[35mAI code:\033[0m {response.get('code', temp)}")

            temp = "\033[31m(no completed_task)"
            print(f"\033[35mAI completed task:\033[36m {response.get('completed_task', temp)}\033[0m")

            tts.speak(response.get("message", "I think something went wrong. I didn't get any response from the AI."))
            movement.send(response.get("code", ""))


        print("\033[35mWaiting for 'Hey Jeremy' to be said...\033[0m")
        text = stt.wait_for_phrase("hey jeremy", "hi jeremy", "hello jeremy", 'jeremy')
        print(f"\033[35mHeard:\033[36m {text}\033[0m")
        
        subprocess.run(["aplay", "responses/initial/" + random.choice(os.listdir("responses/initial/"))])

        print("\033[35mListening for your question...\033[0m")
        text = stt.listen()
        image = capture_image(args.image_path)

        print(f"\033[35mYou said:\033[36m {text}\033[0m")
        response = ai.ask(text, args.image_path, get_scan_data())

        ## +
        try:
            response2 = json.loads("{" + response["message"].split("{")[1]) # in case if the AI puts its JSON inside of its response
            message = response.get("message", None)            
            code = response.get("code", None)
            completed_task = response.get("completed_task", "yes")
        except IndexError:
            pass
        else:
            response = response2
        ## ~

        # temp is used because, prior to Python 3.12, you can't use escape sequences within the { and } of an f-string
        temp = "\033[31m(no message returned)" 
        print(f"\033[35mAI response:\033[36m {response.get('message', temp)}\033[0m")

        temp = "\033[31m(no code returned)"
        print(f"\033[35mAI code:\033[0m {response.get('code', temp)}")

        temp = "\033[31m(no completed_task)"
        print(f"\033[35mAI completed task:\033[36m {response.get('completed_task', temp)}\033[0m")

        tts.speak(response.get("message", "I didn't get any message back from the API."))
        movement.send(response.get("code", ""))


    except HTTPError as e: # if it's an HTTPError, it's probably just Pollinations API being dumb, so it can be ignored and moved on from
        print(f"\033[35mDumb network error (ignoring):\033[36m {e}\033[0m")
        tts.speak(f"Huh, it looks like there was a network error. I think my AI is just being dumb right now, so I'm going to ignore it.")
    

    except KeyboardInterrupt:
        lidar.stop()
        lidar.disconnect()
        print("\033[35mExiting...\033[0m")
        break


    except Exception as e:
        lidar.stop()
        lidar.disconnect() 
        raise e # if it's not an HTTPError, re-raise it so we can see the full traceback and fix the bug