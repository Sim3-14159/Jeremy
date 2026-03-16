from ai import *

ai = PollinationsAI("sk_jc6v0vih789OzqrlRI9Rtl0Wf7pDFsBU")

resp = ai.ask("Hello")
print(resp["message"])

resp = ai.ask(
    "What is in this image?",
    image_path="image.jpg"
)

print(resp["message"])
