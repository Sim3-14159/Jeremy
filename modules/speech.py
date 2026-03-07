"""
Speech module for text-to-speech functionality using EspeakNG and Piper.
"""

import sounddevice as sd
import numpy as np
from piper.voice import PiperVoice

__all__ = ["EspeakNGTTS", "PiperTTS"]

class EspeakNGTTS:
    def __init__(self, voice: str="en+male"):
        self.voice = voice
    def speak(self, text: str):
        import subprocess
        subprocess.run(["espeak-ng", "-v", self.voice, text])


class PiperTTS:
    def __init__(self, model_path: str="en_US-hfc_male-medium.onnx"):
        self.voice = PiperVoice.load(model_path)
    
    def speak(self, text: str):
        sample_rate = self.voice.config.sample_rate
        stream = sd.OutputStream(samplerate=sample_rate, channels=1, dtype="int16")
        stream.start()
        
        for chunk in self.voice.synthesize(text):
            audio_data = chunk.audio_int16_array
            stream.write(audio_data)
        
        stream.stop()
        stream.close()


def play_text(voice: PiperVoice, text: str):
    sample_rate = voice.config.sample_rate
    stream = sd.OutputStream(samplerate=sample_rate, channels=1, dtype="int16")
    stream.start()
    
    for chunk in voice.synthesize(text):
        audio_data = chunk.audio_int16_array
        stream.write(audio_data)
    
    stream.stop()
    stream.close()


if __name__ == "__main__":
    model = "en_US-hfc_male-medium.onnx"
    voice = PiperVoice.load(model)
    text = "Hey, I'm Jeremy, your AI assistant. How can I help you today?"
    play_text(voice, text)