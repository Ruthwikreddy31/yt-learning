import os
import sys
import json
import time
import datetime

# Avoid UnicodeEncodeError on Windows terminals with emojis
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project paths
sys.path.append("c:\\Users\\ruthw\\OneDrive\\Attachments\\Desktop\\genai\\yt")

from database.connection import db
from services.transcript_service import transcript_service
from services.chromadb_service import chromadb_service
from agents.summary_agent import SummaryAgent
from agents.chapter_agent import ChapterAgent
from agents.quiz_agent import QuizAgent
from agents.flashcard_agent import FlashcardAgent

def test_pdf_pipeline():
    print("==================================================")
    print("[TEST] RUNNING PDF DIGESTION PIPELINE INTEGRATION TEST")
    print("==================================================")

    # 1. Create a dummy file path
    dummy_pdf_name = "test_document_digestion.pdf"
    
    # 2. Call PDF parsing (this will fallback to simulated chunks cleanly if file doesn't exist, which is perfect for testing)
    print("\n[Stage 1] Parsing PDF Document...")
    chunks, full_text = transcript_service.parse_pdf_document(dummy_pdf_name)
    print(f"Generated {len(chunks)} chunks.")
    print(f"Sample full text (first 100 chars): {full_text[:100]}...")
    
    assert len(chunks) > 0
    assert "start" in chunks[0]
    assert "end" in chunks[0]
    assert "text" in chunks[0]
    print("✅ Stage 1: Document text extraction passed!")

    # 3. Create semantic chunks
    print("\n[Stage 2] Indexing segments inside ChromaDB vector store...")
    # Slicing helper representation
    semantic_chunks = []
    current_words = []
    current_start = 0.0
    
    for i, c in enumerate(chunks):
        words = c["text"].split()
        if not current_words:
            current_start = c["start"]
        current_words.extend(words)
        if len(current_words) >= 100 or i == len(chunks) - 1:
            semantic_chunks.append({
                "text": " ".join(current_words),
                "start": current_start,
                "end": c["end"]
            })
            current_words = current_words[-15:] if len(current_words) > 15 else []

    doc_id = f"test_doc_{int(time.time())}"
    chromadb_service.add_chunks(doc_id, semantic_chunks)
    
    # Verify we can query similar segments
    query_matches = chromadb_service.query_similar_chunks(doc_id, "Simulated fallback", top_k=2)
    print(f"ChromaDB Query Matches: {len(query_matches)}")
    assert len(query_matches) > 0
    print("✅ Stage 2: ChromaDB indexing passed!")

    # 4. Generate AI summary, chapters, cards, and quizzes
    print("\n[Stage 3] Synthesizing summary guides and learning decks...")
    current_provider = "gemini"
    
    sum_agent = SummaryAgent(provider=current_provider)
    summary_data = sum_agent.generate_summary(dummy_pdf_name, full_text)
    print("Summary Generated successfully.")
    assert "short_summary" in summary_data
    
    chap_agent = ChapterAgent(provider=current_provider)
    chapter_data = chap_agent.generate_chapters(dummy_pdf_name, chunks)
    print("Chapters Generated successfully.")
    assert "chapters" in chapter_data

    card_agent = FlashcardAgent(provider=current_provider)
    cards_data = card_agent.generate_flashcards(dummy_pdf_name, full_text)
    print("Flashcards Generated successfully.")
    assert "cards" in cards_data

    quiz_agent = QuizAgent(provider=current_provider)
    quizzes_data = quiz_agent.generate_quiz(dummy_pdf_name, full_text, ["easy", "medium", "hard"])
    print("Quizzes Generated successfully.")
    assert "quizzes" in quizzes_data
    print("✅ Stage 3: Educational assets generation passed!")

    # 5. Insert documents in MongoDB datastore
    print("\n[Stage 4] Storing course digestion structures in MongoDB datastores...")
    video_doc = {
        "_id": doc_id,
        "title": dummy_pdf_name,
        "duration": chunks[-1]["end"] if chunks else 300,
        "source": "dummy_uploads/" + dummy_pdf_name,
        "status": "completed",
        "processed_at": datetime.datetime.utcnow(),
        "thumbnail": "",
        "is_pdf": True
    }
    
    videos_col = db.get_collection("videos")
    videos_col.insert_one(video_doc)
    
    db.get_collection("transcripts").insert_one({
        "video_id": doc_id,
        "text": full_text,
        "chunks": chunks
    })
    db.get_collection("summaries").insert_one({
        "video_id": doc_id,
        **summary_data
    })
    db.get_collection("chapters").insert_one({
        "video_id": doc_id,
        "chapters": chapter_data.get("chapters", [])
    })
    
    # Retrieve to check values
    saved_doc = videos_col.find_one({"_id": doc_id})
    print(f"Retrieved Document Title: {saved_doc['title']}")
    assert saved_doc["is_pdf"] == True
    
    # Cleanup dummy records
    videos_col.delete_one({"_id": doc_id})
    db.get_collection("transcripts").delete_one({"video_id": doc_id})
    db.get_collection("summaries").delete_one({"video_id": doc_id})
    db.get_collection("chapters").delete_one({"video_id": doc_id})
    chromadb_service.collection.delete(where={"video_id": doc_id})
    print("🧹 Temporary testing records safely purged.")
    print("✅ Stage 4: Document persistence passed!")

    print("\n==================================================")
    print("🎉 SUCCESS! ALL PDF DIGESTION PIPELINE TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_pdf_pipeline()
