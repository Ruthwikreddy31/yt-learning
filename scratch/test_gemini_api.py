import os
import sys
from dotenv import load_dotenv

# Ensure project root is in system path
sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

from services.gemini_service import gemini_service

gemini_service.default_model = "gemini-2.5-flash"

print("Gemini configured:", gemini_service.is_configured)
print("Default model:", gemini_service.default_model)

prompt = "Hello, please reply in 3 words: 'Gemini is active!'"
print("Sending test prompt to Gemini...")
res = gemini_service.generate_text(prompt)
print("Response:")
print(res)
