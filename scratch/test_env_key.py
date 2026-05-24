import os
import sys
from dotenv import load_dotenv

# Ensure project root is in the system path
sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

print("sys.path:", sys.path)
print("Current Working Directory:", os.getcwd())
print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
print("MONGODB_URI:", os.getenv("MONGODB_URI"))
