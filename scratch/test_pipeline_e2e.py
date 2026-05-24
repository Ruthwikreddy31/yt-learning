import sys
import os
import json
from dotenv import load_dotenv

# Ensure base directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

# Prevent Windows console encoding issues
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from services.transcript_service import transcript_service
from agents.quiz_agent import QuizAgent

def run_e2e_test():
    print("=============================================================")
    print(" E2E INTEGRATION TEST: TRANSCRIPTION & QUIZ ALIGNMENT")
    print("=============================================================")
    
    # Test Case 1: Ingestion of a YouTube video (DBMS introduction)
    print("\n[TEST 1] Processing YouTube Video (3EJlovevfcA - Introduction to DBMS)...")
    yt_url = "https://www.youtube.com/watch?v=3EJlovevfcA"
    
    try:
        chunks, full_text = transcript_service.process_video_pipeline(yt_url, is_youtube=True)
        print(f"  --> Successfully transcribed YouTube video!")
        print(f"  --> Number of transcript chunks: {len(chunks)}")
        print(f"  --> Consolidated transcript length: {len(full_text)} characters")
        print(f"  --> Sample text: {full_text[:200]}...")
        
        # Generate Quiz
        print("\n  [QUIZ GENERATION] Synthesizing questions for YouTube Video...")
        quiz_agent = QuizAgent(provider="gemini")
        quiz_data = quiz_agent.generate_quiz("Introduction to DBMS", full_text, ["easy", "medium", "hard"])
        
        print("\n  [QUIZ RESULT] Generated Quiz Questions:")
        quizzes = quiz_data.get("quizzes", [])
        for idx, q in enumerate(quizzes):
            print(f"    Question {idx+1}: {q['question']}")
            print(f"      Type: {q['type']}")
            print(f"      Options: {q.get('options', [])}")
            print(f"      Answer: {q['answer']}")
            print(f"      Explanation: {q.get('explanation', '')}")
            print("    " + "-"*40)
            
    except Exception as e:
        print(f"  --> TEST 1 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()

    # Test Case 2: Uploading a completely custom general file (e.g. "Space Exploration and Rockets")
    print("\n[TEST 2] Simulating physical file upload with a custom topic...")
    # We will write a mock transcript that represents space/rocket contents
    custom_transcript = (
        "Space exploration is the ongoing discovery and exploration of celestial structures in outer space. "
        "Spacecraft are vehicles designed to travel beyond the Earth's atmosphere. "
        "A rocket is a projectile that can be propelled to a great height by the combustion of fuel. "
        "Rockets carry payloads such as communication satellites, space telescopes, and scientific sensors. "
        "The first human to journey into outer space was Yuri Gagarin in 1961. "
        "The Apollo missions successfully landed the first humans on the Moon in 1969. "
        "Mars is often targeted for exploration because of its potential compatibility with life. "
        "Space telescopes like Hubble and James Webb provide high-resolution images of distant galaxies."
    )
    
    try:
        print(f"  --> Processing simulated transcript for topic 'Space Exploration'...")
        # Since it is a general topic not matching standard categories, it will exercise our dynamic sentence analyzer!
        quiz_agent = QuizAgent(provider="gemini")
        quiz_data = quiz_agent.generate_quiz("Space Exploration and Rockets", custom_transcript, ["easy", "medium", "hard"])
        
        print("\n  [QUIZ RESULT] Generated Quiz Questions for Space Exploration:")
        quizzes = quiz_data.get("quizzes", [])
        for idx, q in enumerate(quizzes):
            print(f"    Question {idx+1}: {q['question']}")
            print(f"      Type: {q['type']}")
            print(f"      Options: {q.get('options', [])}")
            print(f"      Answer: {q['answer']}")
            print(f"      Explanation: {q.get('explanation', '')}")
            print("    " + "-"*40)
            
    except Exception as e:
        print(f"  --> TEST 2 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_e2e_test()
