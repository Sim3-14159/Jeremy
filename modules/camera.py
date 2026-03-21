"""
Camera module for interfacing with the Raspberry Pi Camera Module.
"""

import subprocess

__all__ = ["capture_image"]

##### IMAGE CAPTURE #####
def capture_image(file_path: str="image.jpg"):
    subprocess.run(["rpicam-jpeg", "-t", "1", "--nopreview", "-o", file_path], stdout=subprocess.DEVNULL) 
    # no output because of DEVNULL
