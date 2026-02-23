import base64
from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import cv2
import tempfile

# Load variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)


def encode_image_to_base64(image_path):
    """Encode an image file to base64"""
    with open(image_path, "rb") as image_file:
        return base64.standard_b64encode(image_file.read()).decode("utf-8")

def extract_video_frame(video_path, frame_number=0):
    """Extract a specific frame from a video file"""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"Could not extract frame {frame_number} from video")
    
    # Save frame temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    cv2.imwrite(temp_file.name, frame)
    temp_file.close()
    return temp_file.name

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

def ask_question_about_video(video_path, question, system_prompt=None, frame_number=0):
    """Ask OpenAI a question about a video by analyzing a specific frame"""
    frame_path = extract_video_frame(video_path, frame_number)
    try:
        return ask_question_about_image(frame_path, question, system_prompt)
    finally:
        os.unlink(frame_path)

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
