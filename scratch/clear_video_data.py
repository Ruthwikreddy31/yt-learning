import sys
import os
from dotenv import load_dotenv

sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")
load_dotenv()

from database.connection import db

def clear_video(video_id):
    print(f"Clearing all database entries for Video ID: {video_id}...")
    
    # Collections to clear
    collections = {
        "videos": "_id",
        "transcripts": "video_id",
        "quizzes": "video_id",
        "summaries": "video_id",
        "flashcards": "video_id"
    }
    
    for col_name, field in collections.items():
        col = db.get_collection(col_name)
        res = col.delete_one({field: video_id})
        print(f"  Collection '{col_name}': Deleted {res.deleted_count} documents.")
        
    print("Database cleared successfully for this video!")

if __name__ == "__main__":
    target_id = "_uQrJ0TkZlc"
    if len(sys.argv) > 1:
        target_id = sys.argv[1]
    clear_video(target_id)
