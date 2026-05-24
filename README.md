# AI YouTube Learning Assistant

Production-oriented Streamlit platform for turning YouTube videos into transcript-grounded learning experiences: summaries, notes, chapters, semantic search, flashcards, adaptive quizzes, analytics, and an AI tutor that answers only from uploaded video content.

## Features

- Paste a YouTube URL and extract captions with `youtube-transcript-api`.
- Upload PDF, DOCX, TXT, or Markdown documents and use them as learning sources.
- Fall back to audio download plus Whisper when captions are unavailable.
- Chunk transcripts, embed them, and store semantic vectors in ChromaDB collections.
- Generate JSON-only summaries, detailed explanations, chapters, notes, quizzes, and flashcards.
- Chat with a transcript-aware AI tutor through a strict RAG workflow.
- Track quiz scores, weak topics, viewed videos, and progress analytics.
- Use MongoDB in production, with a local JSON fallback for development.
- No login required for local use; the app uses a built-in local learner profile.

## Architecture

```text
app.py
pages/
  dashboard.py
  upload_video.py
  summary.py
  quiz.py
  flashcards.py
  ai_chat.py
  analytics.py
agents/
  summary_agent.py
  quiz_agent.py
  tutor_agent.py
  flashcard_agent.py
  notes_agent.py
  chapter_agent.py
  semantic_search_agent.py
  difficulty_analyzer_agent.py
prompts/
  summary_prompt.txt
  quiz_prompt.txt
  tutor_prompt.txt
  flashcard_prompt.txt
  notes_prompt.txt
services/
  youtube_service.py
  transcript_service.py
  embedding_service.py
  chromadb_service.py
  groq_service.py
  gemini_service.py
  rag_service.py
  quiz_service.py
  summary_service.py
  notes_service.py
  tutor_service.py
  analytics_service.py
database/
  mongodb.py
  schemas.py
chromadb_data/
uploads/
static/
utils/
```

## RAG Workflow

1. Extract transcript from YouTube captions or Whisper.
2. Split transcript into overlapping semantic chunks.
3. Generate embeddings using Sentence Transformers.
4. Store chunks in ChromaDB collections: `transcript_embeddings`, `semantic_chunks`, and `quiz_embeddings`.
5. Embed each user question.
6. Retrieve the most relevant chunks for the selected video.
7. Send only retrieved context plus the user question to the tutor agent.
8. If context is missing, return: `I could not find this topic in the uploaded video.`

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and add:

- `OPENAI_API_KEY` for OpenAI-powered topic-based quiz generation
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `GROQ_API_KEY` if you want Groq generation
- `MONGODB_URI` for MongoDB Atlas or local MongoDB

Install FFmpeg for Whisper fallback and ensure it is available on your `PATH`.

## Run Locally

```bash
streamlit run app.py
```

Open the local Streamlit URL, paste a YouTube URL or upload a document/PDF, and generate learning materials.

## Production Notes

- Use MongoDB Atlas or a managed MongoDB deployment.
- Persist `chromadb_data/` on durable storage.
- Add network/API rate limiting at the deployment edge.
- Keep API keys only in environment variables or a secret manager.
- For high traffic, move ingestion and generation into background jobs.

## Security

The app keeps API keys in environment variables, rate-limits expensive Streamlit actions, separates data by a local learner ID, and uses transcript-only tutor prompts. The current Streamlit implementation is suitable for local and internal SaaS prototypes; a public deployment should add hardened identity management at the platform or reverse-proxy layer.
