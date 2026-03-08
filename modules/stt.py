"""
STT module for speech-to-text functionality using Vosk.
"""

from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json
import time

__all__ = ["VoskSTT"]


class VoskSTT:
    """
    [FAST (LOCAL)] --> MEDIUM-QUALITY TEXT
    Interface to Vosk STT engine.
    """
    def __init__(self, model_path: str = "model"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)

    def listen(self, silence_timeout: float = 1.0) -> str:
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=4000,
            dtype="int16",
            channels=1
        ) as stream:

            started = False
            silence_start = None
            results = []

            while True:
                data = bytes(stream.read(4000)[0])

                if self.recognizer.AcceptWaveform(data):
                    res = json.loads(self.recognizer.Result())
                    text = res.get("text", "")

                    if text:
                        started = True
                        silence_start = None
                        results.append(text)

                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get("partial", "")

                    if partial_text:
                        started = True
                        silence_start = None
                    elif started:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > silence_timeout:
                            break

            final_res = json.loads(self.recognizer.FinalResult())
            if final_res.get("text"):
                results.append(final_res["text"])

            return " ".join(results)

    def wait_for_phrase(self, *phrases: str) -> str:
        phrases = [phrase.lower().split() for phrase in phrases]

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=4000,
            dtype="int16",
            channels=1
        ) as stream:

            while True:
                data = bytes(stream.read(4000)[0])

                if self.recognizer.AcceptWaveform(data):
                    res = json.loads(self.recognizer.Result())
                    text = res.get("text", "").lower()
                else:
                    res = json.loads(self.recognizer.PartialResult())
                    text = res.get("partial", "").lower()

                if not text:
                    continue

                words = text.split()

                for phrase_words in phrases:
                    for i in range(len(words) - len(phrase_words) + 1):
                        if words[i:i + len(phrase_words)] == phrase_words:
                            return text