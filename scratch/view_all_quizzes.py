import sys
import os
from dotenv import load_dotenv

sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

from database.connection import db

quizzes_col = db.get_collection("quizzes")
videos_col = db.get_collection("videos")

for video in videos_col.find():
    vid_id = video["_id"]
    title = video["title"]
    print(f"============================================================")
    print(f"VIDEO: {title} (ID: {vid_id})")
    print(f"============================================================")
    q_doc = quizzes_col.find_one({"video_id": vid_id})
    if q_doc and q_doc.get("quizzes"):
        for idx, q in enumerate(q_doc["quizzes"]):
            print(f"Question {idx+1}: {q['question']}")
            print(f"  Type: {q['type']}")
            print(f"  Answer: {q['answer']}")
            print(f"  Explanation: {q.get('explanation', '')}")
            print("-" * 30)
    else:
        print("No quizzes found.")
