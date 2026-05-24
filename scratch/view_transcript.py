import sys
import os
from dotenv import load_dotenv

sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\Desktop\\genai\\yt")
load_dotenv()

from database.connection import db

transcripts_col = db.get_collection("transcripts")
t_doc = transcripts_col.find_one({"video_id": "_uQrJ0TkZlc"})
if t_doc:
    print("Found Transcript!")
    text = t_doc.get("text", "")
    print(f"Transcript Length: {len(text)}")
    print("First 1000 characters:")
    print(text[:1000])
    
    # Check if there are matches for the key keywords
    content_to_analyze = ("Python Full Course for Beginners" + " " + text).lower()
    for kw in ["rag", "chroma", "vector", "embedding", "similarity", "retrieval", "jwt", "auth", "token", "security", "sign", "stateless", "mongodb", "sqlite", "database", "collection", "pymongo", "sql", "streamlit", "st.", "dashboard", "widget", "session_state", "hotel", "luxury", "booking", "room", "reservation", "travel", "guest", "reception", "stay", "css", "html", "styling", "design", "flexbox", "grid"]:
        if kw in content_to_analyze:
            print(f"Matched Keyword: {kw}")
else:
    print("No transcript found for _uQrJ0TkZlc")
