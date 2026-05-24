import sys
import os
from dotenv import load_dotenv

sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

from database.connection import db

videos_col = db.collection("videos")
transcripts_col = db.collection("transcripts")
quizzes_col = db.collection("quizzes")

for v in videos_col.find():
    vid_id = v["_id"]
    title = v["title"]
    print(f"VIDEO: {title} (ID: {vid_id})")
    
    t_doc = transcripts_col.find_one({"video_id": vid_id})
    if t_doc:
        text = t_doc.get("text", "")
        print(f"  Transcript length: {len(text)}")
        print(f"  Transcript preview: {text[:200]}")
    else:
        print("  NO TRANSCRIPT!")
        
    q_doc = quizzes_col.find_one({"video_id": vid_id})
    if q_doc:
        quizzes = q_doc.get("quizzes", [])
        print(f"  Quizzes count: {len(quizzes)}")
        if quizzes:
            print(f"  First Quiz Question: {quizzes[0]['question']}")
    else:
        print("  NO QUIZZES!")
    print("-" * 50)
