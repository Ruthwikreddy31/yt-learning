import sys
import os
import json
from dotenv import load_dotenv

sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

# Avoid UnicodeEncodeError on Windows terminals
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from database.connection import db
from agents.quiz_agent import QuizAgent

print("Running Quiz Generation Test for video _uQrJ0TkZlc...")
vid_id = "_uQrJ0TkZlc"

video = db.get_collection("videos").find_one({"_id": vid_id})
if not video:
    print("Video not found!")
    sys.exit(1)

transcript_doc = db.get_collection("transcripts").find_one({"video_id": vid_id})
if not transcript_doc:
    print("Transcript not found!")
    sys.exit(1)

full_text = transcript_doc.get("text", "")
print(f"Transcript text length: {len(full_text)}")

agent = QuizAgent(provider="gemini")
print("Generating quiz via QuizAgent...")
res = agent.generate_quiz(video["title"], full_text, ["easy", "medium", "hard"])

print("\n--- Raw Result ---")
print(json.dumps(res, indent=2))
print("------------------")

quizzes = res.get("quizzes", [])
print(f"Number of quizzes generated: {len(quizzes)}")
