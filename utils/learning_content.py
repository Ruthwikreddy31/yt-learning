from __future__ import annotations

import re
import random
from collections import Counter


STOPWORDS = {
    "about", "after", "again", "also", "because", "before", "being", "between", "could", "every",
    "from", "have", "into", "just", "like", "more", "most", "only", "other", "should", "some",
    "such", "than", "that", "their", "them", "then", "there", "these", "they", "this", "through",
    "using", "very", "what", "when", "where", "which", "while", "with", "would", "your",
}


def sentences_from_text(text: str) -> list[str]:
    clean = re.sub(r"\s+", " ", text or "").strip()
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", clean) if len(item.split()) >= 6]
    if not sentences and clean:
        words = clean.split()
        sentences = [" ".join(words[index:index + 28]) for index in range(0, min(len(words), 180), 28)]
    return sentences


def keywords_from_text(text: str, limit: int = 10) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+\-]{3,}", text or "")
    counts = Counter(word.lower() for word in words if word.lower() not in STOPWORDS)
    return [word.title() for word, _ in counts.most_common(limit)]


def _sentence_keyword(sentence: str, keywords: list[str]) -> str | None:
    sentence_lower = sentence.lower()
    for keyword in keywords:
        if keyword.lower() in sentence_lower:
            return keyword
    words = re.findall(r"[A-Za-z][A-Za-z0-9+\-]{4,}", sentence)
    ranked = [word for word in words if word.lower() not in STOPWORDS]
    return ranked[0].title() if ranked else None


def _build_options(answer: str, keywords: list[str], count: int = 4) -> list[str]:
    distractors = [keyword for keyword in keywords if keyword.lower() != answer.lower()]
    fallback = ["Main Idea", "Supporting Detail", "Example", "Definition", "Process", "Result"]
    distractors.extend(item for item in fallback if item.lower() != answer.lower())
    options = [answer] + distractors[: count - 1]
    random.Random(answer).shuffle(options)
    return options


def _statement_options(correct: str, concept: str, topic: str) -> list[str]:
    options = [
        correct,
        f"{concept} is unrelated to {topic} and can usually be ignored.",
        f"{concept} only describes the visual style of the uploaded material.",
        f"{concept} is mainly a random external fact outside the uploaded topic.",
    ]
    random.Random(concept + topic).shuffle(options)
    return options


def local_summary(text: str, title: str = "") -> dict:
    sentences = sentences_from_text(text)
    keywords = keywords_from_text(text, 8)
    if not sentences:
        return {
            "short_summary": "No readable learning content was found.",
            "detailed_summary": "No readable learning content was found in the uploaded source.",
            "beginner_summary": "No readable text was available to explain.",
            "technical_summary": "No technical details were available.",
            "key_insights": [],
            "tags": [],
        }
    lead = sentences[:5]
    topic = title or (", ".join(keywords[:3]) if keywords else "this topic")
    return {
        "short_summary": " ".join(lead[:2]),
        "detailed_summary": "\n\n".join(
            [
                f"This source focuses on {topic}.",
                " ".join(lead[:4]),
                "The main learning value is understanding the terms, relationships, and examples presented in the source material.",
            ]
        ),
        "beginner_summary": f"In simple terms, {topic} is explained through these core ideas: {' '.join(lead[:2])}",
        "technical_summary": f"Technical view: the material emphasizes {', '.join(keywords[:6]) or 'the core concepts'} and explains them through the uploaded content.",
        "key_insights": lead[:6],
        "tags": keywords[:8],
    }


def local_quiz(text: str, title: str = "", limit: int = 10) -> dict:
    sentences = sentences_from_text(text)
    keywords = keywords_from_text(f"{title} {text}", 18)
    topic = title or (", ".join(keywords[:2]) if keywords else "the uploaded topic")
    questions = []
    used_answers: set[str] = set()
    for sentence in sentences:
        if len(questions) >= limit:
            break
        concept = _sentence_keyword(sentence, keywords)
        if not concept or concept.lower() in used_answers:
            continue
        used_answers.add(concept.lower())
        index = len(questions)
        question_templates = [
            f"Which statement best explains the role of {concept} in {topic}?",
            f"Why is {concept} important for understanding {topic}?",
            f"Which description of {concept} is most accurate in the context of {topic}?",
            f"How does {concept} connect to the main idea of {topic}?",
        ]
        questions.append(
            {
                "question": question_templates[index % len(question_templates)],
                "type": "mcq",
                "difficulty": "easy" if index < 4 else "medium" if index < 8 else "hard",
                "options": _statement_options(sentence[:220], concept, topic),
                "answer": sentence[:220],
                "explanation": f"This answer is grounded in the uploaded content: {sentence}",
                "topic": concept,
            }
        )
    for index, concept in enumerate(keywords):
        if len(questions) >= limit:
            break
        if concept.lower() in used_answers:
            continue
        related_sentence = next((s for s in sentences if concept.lower() in s.lower()), sentences[index % len(sentences)] if sentences else title)
        questions.append(
            {
                "question": f"Which concept is most directly connected to {topic}?",
                "type": "mcq",
                "difficulty": "medium",
                "options": _build_options(concept, keywords),
                "answer": concept,
                "explanation": f"{concept} appears as a key concept in the uploaded learning source.",
                "topic": concept,
            }
        )
    if not questions:
        questions.append(
            {
                "question": "What is the uploaded content mainly about?",
                "type": "conceptual",
                "difficulty": "easy",
                "options": [],
                "answer": title or "The uploaded topic",
                "explanation": "Generated from the available title because no readable text was found.",
                "topic": title or "general",
            }
        )
    return {"questions": questions}


def local_flashcards(text: str, title: str = "", limit: int = 12) -> dict:
    sentences = sentences_from_text(text)
    keywords = keywords_from_text(text, limit)
    cards = []
    for index, concept in enumerate(keywords[:limit]):
        back = sentences[index % len(sentences)] if sentences else f"{concept} appears as an important topic in {title or 'the uploaded source'}."
        cards.append({"front": concept, "back": back, "topic": concept})
    if not cards:
        cards.append({"front": title or "Uploaded topic", "back": "No readable text was found for this card.", "topic": "overview"})
    return {"flashcards": cards}


def local_notes(text: str, title: str = "") -> dict:
    summary = local_summary(text, title)
    return {
        "outline": summary["tags"][:6],
        "sections": [
            {"heading": "Overview", "bullets": summary["key_insights"][:3]},
            {"heading": "Important Concepts", "bullets": summary["tags"][:6]},
        ],
        "action_items": ["Review the summary", "Practice the quiz", "Revise the flashcards"],
    }
