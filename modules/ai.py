from openai import OpenAI

import requests
import urllib.parse


class PollinationsAI:
    """[FREE (API)] Interface to Pollinations AI for text generation and code execution."""
    def __init__(self, prompt: str="", model="openai-fast"):
        self.conversation = prompt
        self.model = model

    def ask(self, question: str) -> dict:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        self.conversation += f"\nUser: {question}\nAssistant:"

        prompt = urllib.parse.quote(self.conversation, safe="")
        url = (
            f"https://text.pollinations.ai/{prompt}"
            f"?model={self.model}&json=true"
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
    """[PAID (API)] Interface to OpenAI API for text generation and code execution."""
    def __init__(self, api_key: str, prompt: str="", model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = prompt
        self.model = model
        self.messages = []
        if prompt:
            self.messages.append({"role": "system", "content": prompt})

    def ask(self, question: str) -> dict:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        # Add user message
        self.messages.append({"role": "user", "content": question})

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        # Extract response
        message = response.choices[0].message.content
        
        # Add assistant response to conversation history
        self.messages.append({"role": "assistant", "content": message})

        # Try to extract code if present (looking for code blocks)
        # TODO: make it so that the AI can return code in a structured way instead of relying on markdown parsing. Return it in a dict with "message" and "code" keys, where "code" is the code to execute. This would be more reliable than parsing markdown.
        code = ""
        if "```" in message:
            # Simple extraction of code blocks
            parts = message.split("```")
            for i in range(1, len(parts), 2):
                if i < len(parts):
                    code += parts[i].strip() + "\n"

        return {
            "message": message,
            "code": code,
            "raw": response.model_dump()
        }