from dotenv import load_dotenv
import os
from openai import OpenAI

# Load variables from .env file
load_dotenv()

# Now retrieve them with os.getenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def ask_question(question):
    """Ask OpenAI a question and return the response"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # Test the function when run directly
    result = ask_question("What is Python?")
    print(result)