"""
AI module for interacting with APIs using Pollinations API and OpenAI API.
"""

## API communication 
from openai import OpenAI as _OpenAI # _OpenAI to avoid name conflict with OpenAIAI class below
import requests

## Response parsing 
import base64
import json 
import urllib.parse

## Environment variable loading 
from dotenv import load_dotenv
import os

__all__ = ["PollinationsAI", "OpenAIAI"]


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SYSTEM_PROMPT = open("prompt.txt").read()

################ AI CLASSES ################

class PollinationsAI:
    """
    [FREE / API] <-- TEXT & IMAGES
    Interface to Pollinations AI.
    """

    def __init__(self, model="openai", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("POLLINATIONS_API_KEY")
        self.messages = []

        if SYSTEM_PROMPT:
            self.messages.append({
                "role": "system",
                "content": SYSTEM_PROMPT
            })

    def ask(self, question: str, image_path: str | None = None) -> dict:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        content = [
            {"type": "text", "text": question}
        ]

        # Attach image if provided
        if image_path:
            base64_image = self._encode_image_to_base64(image_path)
            ext = os.path.splitext(image_path)[1].lower()

            media_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp"
            }

            media_type = media_type_map.get(ext, "image/jpeg")

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{base64_image}"
                }
            })

        self.messages.append({
            "role": "user",
            "content": content
        })

        headers = {
            "Content-Type": "application/json"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": self.messages
        }

        response = requests.post(
            "https://gen.pollinations.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        message_text = data["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(message_text)
            message = parsed.get("message", "")
            code = parsed.get("code", "")
        except Exception:
            message = message_text
            code = ""

        self.messages.append({
            "role": "assistant",
            "content": [
                {"type": "text", "text": message}
            ]
        })

        return {
            "message": message,
            "code": code,
            "raw": data
        }


    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


class OpenAIAI:
    """
    [PAID (API)] <-- TEXT & IMAGES
    Interface to OpenAI API.
    """

    def __init__(self, model="gpt-4.1"):
        self.client = _OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.messages = []

        if SYSTEM_PROMPT:
            self.messages.append({
                "role": "system",
                "content": [
                    {"type": "input_text", "text": SYSTEM_PROMPT}
                ]
            })

    def ask(self, question: str, image_path: str | None = None, sensor_data: dict | None = None) -> dict:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        content = [
            {"type": "input_text", "text": question}
        ]

        # Attach image if provided
        if image_path:
            base64_image = self._encode_image_to_base64(image_path)
            ext = os.path.splitext(image_path)[1].lower()

            media_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp"
            }

            media_type = media_type_map.get(ext, "image/jpeg")

            content.append({
                "type": "input_image",
                "image_url": f"data:{media_type};base64,{base64_image}"
            })

        # Attach sensor data if provided
        if sensor_data:
            content.append({
                "type": "input_sensor_data",
                "sensor_data": sensor_data
            })

        self.messages.append({
            "role": "user",
            "content": content
        })

        response = self.client.responses.create(
            model=self.model,
            input=self.messages
        )

        text = response.output_text

        try:
            parsed = json.loads(text)
            message = parsed.get("message", "")
            code = parsed.get("code", "")
            completed_task = parsed.get("completed_task", "yes") # default to completed so we don't get stuck in a loop
        except Exception:
            message = text
            code = ""
            completed_task = "yes" # if we can't parse the response, assume the task was completed to avoid getting stuck in a loop

        self.messages.append({
            "role": "assistant",
            "content": [
                {"type": "output_text", "text": message}
            ]
        })

        return {
            "message": message,
            "code": code,
            "completed_task": completed_task,
            "raw": response.model_dump()
        }


    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

