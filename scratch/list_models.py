import os
import sys
from dotenv import load_dotenv

sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    print("Listing models...")
    for m in genai.list_models():
        print(f"Name: {m.name}, Supported Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")
