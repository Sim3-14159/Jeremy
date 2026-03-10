import asyncio
import pygame
import os
import subprocess
import random

from requests.exceptions import HTTPError

from modules.gui import GUI
from modules.ai import PollinationsAI
from modules.stt import VoskSTT
from modules.tts import PiperTTS

running = True

# Global state to share data between the logic and the GUI

async def gui_update_loop(gui):
    """Updates the GUI 10 times per second."""
    global running
    while running:
        # Update and draw the GUI with whatever text is currently in state
        gui.update()
        gui.draw()
        pygame.display.flip() 
        await asyncio.sleep(1) # 10Hz

async def assistant_logic(stt, ai, tts, gui):
    """Your main voice assistant logic, modified to be non-blocking."""
    loop = asyncio.get_running_loop()
    global running

    while running:
        try:
            # We use run_in_executor to run blocking calls without freezing the GUI
            text = await loop.run_in_executor(None, stt.wait_for_phrase, "hey jeremy", "hi jeremy", "hello jeremy", 'jeremy')
            
            subprocess.run(["aplay", "responses/initial/" + random.choice(os.listdir("responses/initial/"))])
            
            text = await loop.run_in_executor(None, stt.listen)

            gui.update(f"User: {text}")
            response = await loop.run_in_executor(None, ai.ask, text)
            
            # Update the global state so the GUI loop picks up the new text
            gui_chat_messages = {"User": text, "AI": response['message']}
            gui.update(f"AI: {gui_chat_messages['AI']}")
            
            await loop.run_in_executor(None, tts.speak, response["message"])
        
        except HTTPError as e: # if it's an HTTP error, the pollinations API was probably just being dumb, so we can just handle it and keep going
            error_msg = f"Network error: {e}"
            print(error_msg)
            gui_chat_messages = {"User": "Error", "AI": e}
            gui.update(f"User: {gui_chat_messages['User']}\n\nAI: {gui_chat_messages['AI']}")
            await loop.run_in_executor(None, tts.speak, e)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    gui = GUI(screen)
    ai = PollinationsAI()
    stt = VoskSTT()
    tts = PiperTTS()

    # Run both loops concurrently
    await asyncio.gather(
        gui_update_loop(gui),
        assistant_logic(stt, ai, tts, gui)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pygame.quit()
