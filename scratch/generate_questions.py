#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Load settings and API keys from .env or .env.example
def load_keys():
    keys = {}
    possible_files = [".env.example", ".env"]
    for file_name in possible_files:
        path = Path(__file__).resolve().parents[1] / file_name
        if path.exists():
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        keys[k.strip().lower()] = v.strip()
            except Exception as e:
                print(f"Warning: Could not read {file_name}: {e}")
    return keys

def main():
    print("=" * 60)
    print("           AI QUESTION GENERATOR (GEMINI, OPENAI, & GROQ)      ")
    print("=" * 60)
    
    keys = load_keys()
    
    gemini_key = keys.get("gemini_api_key") or keys.get("google_api_key")
    openai_key = keys.get("openai_api_key")
    groq_key = keys.get("groq_api_key")
    
    if not gemini_key and not openai_key and not groq_key:
        print("Error: No API keys found in .env or .env.example!")
        print("Please ensure either GEMINI_API_KEY, openai_api_key, or GROQ_API_KEY is set.")
        sys.exit(1)
        
    import argparse
    parser = argparse.ArgumentParser(description="AI Question Generator")
    parser.add_argument("-t", "--topic", help="Topic for question generation")
    parser.add_argument("-p", "--provider", choices=["gemini", "openai", "groq"], help="AI Provider to use (gemini, openai, or groq)")
    args, unknown = parser.parse_known_args()
    
    topic = args.topic
    if not topic:
        if sys.stdin.isatty():
            topic = input("Enter the topic for question generation\n(e.g. 'Retrieval Augmented Generation', 'Python Programming'): ").strip()
        if not topic:
            topic = "Retrieval Augmented Generation"
            print(f"Using default topic: {topic}")
            
    provider = args.provider
    if not provider:
        if sys.stdin.isatty():
            print("\nAvailable Providers:")
            print(f"  [1] Gemini  - {'Configured' if gemini_key else 'Not configured'}")
            print(f"  [2] OpenAI  - {'Configured' if openai_key else 'Not configured'}")
            print(f"  [3] Groq    - {'Configured' if groq_key else 'Not configured'}")
            
            choice = input("\nSelect provider [default: 1]: ").strip()
            if choice == "2":
                provider = "openai"
            elif choice == "3":
                provider = "groq"
            else:
                provider = "gemini"
        else:
            # Automatic fallback to first configured key
            if groq_key:
                provider = "groq"
            elif gemini_key:
                provider = "gemini"
            else:
                provider = "openai"
            
    # Normalize provider name
    provider = provider.lower()
    if provider == "openai":
        if not openai_key:
            print("Error: OpenAI key is not configured!")
            sys.exit(1)
        provider_display = "OpenAI"
    elif provider == "groq":
        if not groq_key:
            print("Error: Groq key is not configured!")
            sys.exit(1)
        provider_display = "Groq"
    else:
        if not gemini_key:
            print("Error: Gemini key is not configured!")
            sys.exit(1)
        provider_display = "Gemini"
        
    prompt = f"""
You are an expert educator.
Generate 5 highly relevant learning/assessment multiple-choice questions (MCQs) for the topic: '{topic}'.
For each question, provide:
- The question text
- 4 options (A, B, C, D)
- The correct answer (matching one of the options exactly)
- An educational explanation of why it is correct.

Return the output ONLY as a valid JSON object matching this structure:
{{
  "topic": "{topic}",
  "questions": [
    {{
      "question": "question text",
      "options": ["option A", "option B", "option C", "option D"],
      "answer": "correct option text",
      "explanation": "educational explanation"
    }}
  ]
}}

Ensure there is no surrounding markdown, no ```json formatting, and no other conversational text. Return only the raw JSON.
"""

    print(f"\nGenerating questions using {provider_display} for topic: '{topic}'...")
    raw_response = ""
    
    try:
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model_name = keys.get("model_name") or "gemini-2.5-flash"
            if model_name.startswith("models/"):
                model_name = model_name.replace("models/", "")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            raw_response = response.text.strip()
            
        elif provider == "groq":
            import groq
            client = groq.Groq(api_key=groq_key)
            model_name = keys.get("groq_model_name") or "llama-3.3-70b-versatile"
            if model_name == "llama-3.1-70b-versatile":
                model_name = "llama-3.3-70b-versatile"
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a precise educational assistant. Return raw JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            raw_response = response.choices[0].message.content.strip()
            
        else: # OpenAI
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a precise educational assistant. Return raw JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                raw_response = res_data["choices"][0]["message"]["content"].strip()
                
        # Clean potential markdown wrapping
        if raw_response.startswith("```"):
            lines = raw_response.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_response = "\n".join(lines).strip()
            
        data = json.loads(raw_response)
        
        print("\n" + "=" * 60)
        print(f" GENERATED QUESTIONS FOR TOPIC: {data.get('topic', topic)}")
        print("=" * 60)
        
        questions = data.get("questions", [])
        for i, q in enumerate(questions, 1):
            print(f"\nQ{i}: {q.get('question')}")
            options = q.get("options", [])
            for j, opt in enumerate(options):
                print(f"  [{chr(65+j)}] {opt}")
            print(f"  *Correct Answer:* {q.get('answer')}")
            print(f"  *Explanation:* {q.get('explanation')}")
            
        # Save output to file
        output_file = Path(__file__).resolve().parent / "generated_questions.json"
        output_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print("\n" + "=" * 60)
        print(f"Success! Saved questions to {output_file}")
        print("=" * 60)
        
    except json.JSONDecodeError:
        print("\nError: Failed to parse API response as JSON.")
        print("Raw response from API was:")
        print(raw_response)
    except Exception as e:
        if isinstance(e, urllib.error.HTTPError):
            error_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(error_body)
                err_msg = err_json.get("error", {}).get("message", error_body)
            except Exception:
                err_msg = error_body
            print(f"\nAn API error occurred: HTTP {e.code} - {err_msg}")
        else:
            print(f"\nAn error occurred during generation: {e}")

if __name__ == "__main__":
    main()
