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
    [FREE (API)] --> TEXT
    Interface to Pollinations AI.
    """
    
    def __init__(self, model="openai-fast"):
        self.conversation = SYSTEM_PROMPT
        self.model = model

    def ask(self, question: str) -> dict:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        self.conversation += f"\nUser: {question}\nAssistant:"

        prompt = urllib.parse.quote(self.conversation, safe="")
        url = (
            f"https://text.pollinations.ai/{prompt}?model={self.model}&json=true"
        )

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        try: 
            data = response.json()
        except ValueError:
            raise RuntimeError("Invalid JSON returned by AI")

        message = data.get("message", "")
        code = data.get("code", "")

        # Append raw AI response to conversation (same as JS)
        self.conversation += response.text

        return {
            "message": message,
            "code": code,
            "raw": data
        }
    

class OpenAIAI:
    """
    [PAID (API)] --> TEXT & IMAGES
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

    def ask(self, question: str, image_path: str | None = None) -> dict:
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
        except Exception:
            message = text
            code = ""

        self.messages.append({
            "role": "assistant",
            "content": [
                {"type": "output_text", "text": message}
            ]
        })

        return {
            "message": message,
            "code": code,
            "raw": response.model_dump()
        }

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

