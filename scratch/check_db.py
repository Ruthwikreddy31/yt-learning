import sys
import os
from dotenv import load_dotenv

sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

from database.connection import db

videos_col = db.get_collection("videos")
transcripts_col = db.get_collection("transcripts")
quizzes_col = db.get_collection("quizzes")
summaries_col = db.get_collection("summaries")
flashcards_col = db.get_collection("flashcards")

videos = list(videos_col.find({}))
print(f"Total videos in database: {len(videos)}")
print("-" * 60)

for v in videos:
    vid_id = v["_id"]
    title = v.get("title", "No Title")
    
    t_doc = transcripts_col.find_one({"video_id": vid_id})
    t_status = "EXISTS" if t_doc else "MISSING"
    
    s_doc = summaries_col.find_one({"video_id": vid_id})
    s_status = "EXISTS" if s_doc else "MISSING"
    
    q_doc = quizzes_col.find_one({"video_id": vid_id})
    q_count = len(q_doc.get("quizzes", [])) if q_doc else 0
    
    f_doc = flashcards_col.find_one({"video_id": vid_id})
    f_count = len(f_doc.get("cards", [])) if f_doc else 0
    
    print(f"Video ID: {vid_id}")
    print(f"  Title: {title}")
    print(f"  Transcript: {t_status}")
    print(f"  Summary: {s_status}")
    print(f"  Quizzes: {q_count}")
    print(f"  Flashcards: {f_count}")
    print("-" * 60)

