"""
Camera module for interfacing with the Raspberry Pi Camera Module.
"""

import subprocess

    
def capture_image(file_path: str):
    subprocess.run(["rpicam-jpeg", "-t", "1", "--nopreview", "-o", file_path])


