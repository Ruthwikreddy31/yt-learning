import sys
import os
from dotenv import load_dotenv

sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

from database.connection import db

quizzes_col = db.get_collection("quizzes")
q_doc = quizzes_col.find_one({"video_id": "_uQrJ0TkZlc"})
if q_doc:
    print("Found Quizzes!")
    for idx, q in enumerate(q_doc.get("quizzes", [])):
        print(f"Question {idx+1}: {q['question']}")
        print(f"  Type: {q['type']}")
        print(f"  Options: {q.get('options', [])}")
        print(f"  Answer: {q['answer']}")
        print(f"  Explanation: {q.get('explanation', '')}")
        print("-" * 40)
else:
    print("No quizzes found for _uQrJ0TkZlc")
