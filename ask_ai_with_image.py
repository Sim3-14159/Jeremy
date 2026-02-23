import base64
from dotenv import load_dotenv
import os
from openai import OpenAI
import json # for response from AI

# Load variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)


def encode_image_to_base64(image_path):
    """Encode an image file to base64"""
    with open(image_path, "rb") as image_file:
        return base64.standard_b64encode(image_file.read()).decode("utf-8")

def ask_question_about_image(image_path, question, system_prompt=None):
    """Ask OpenAI a question about an image"""
    base64_image = encode_image_to_base64(image_path)
    
    ext = os.path.splitext(image_path)[1].lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    media_type = media_type_map.get(ext, "image/jpeg")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{base64_image}",
                },
            },
            {
                "type": "text",
                "text": question
            }
        ],
    })
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    image_path = "street.jpg"
    system_prompt = open("systemPrompt.txt", "r").read()
    
    print(f"Loaded image: {image_path}")
    print("Ask questions about the image (type 'exit' to quit):\n")
    
    while True:
        question = input("Your question: ").strip()
        
        if question.lower() == "exit":
            print("Goodbye!")
            break
        
        if not question:
            print("Please enter a valid question.\n")
            continue
        
        result = json.loads(ask_question_about_image(image_path, question, system_prompt))
        
        print(f"Response: {result['message']}\n")
        print(f"Code: {result['code']}")
