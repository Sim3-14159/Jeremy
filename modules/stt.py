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

    def listen(self, silence_timeout: float = 1.0) -> str:
        recognizer = KaldiRecognizer(self.model, 16000)

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

                if recognizer.AcceptWaveform(data):
                    res = json.loads(recognizer.Result())
                    text = res.get("text", "")

                    if text:
                        started = True
                        silence_start = None
                        results.append(text)

                else:
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = partial.get("partial", "")

                    if partial_text:
                        started = True
                        silence_start = None
                    elif started:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > silence_timeout:
                            break

            final_res = json.loads(recognizer.FinalResult())
            if final_res.get("text"):
                results.append(final_res["text"])

            return " ".join(results)
