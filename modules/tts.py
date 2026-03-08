"""
TTS module for text-to-speech functionality using EspeakNG and Piper.
"""

import sounddevice as sd
from piper.voice import PiperVoice

__all__ = ["EspeakNGTTS", "PiperTTS"]


class EspeakNGTTS:
    """
    [FAST (LOCAL)] --> LOW-QUALITY AUDIO
    Interface to EspeakNG TTS engine.
    """
    def __init__(self, voice: str="en+male"):
        self.voice = voice
    def speak(self, text: str):
        import subprocess
        subprocess.run(["espeak-ng", "-v", self.voice, text])


class PiperTTS:
    """
    [MEDIUM-FAST (LOCAL)] --> MEDIUM-HIGH-QUALITY AUDIO
    Interface to Piper TTS engine.
    """
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
