import os
import sys
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retriever import get_movie_context
from text_to_cypher import text_to_cypher_context
from graph.similarity import get_similarity_context

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a helpful movie expert chatbot. You answer questions about movies
using the context retrieved from a movie knowledge graph.

Rules:
- Only answer based on the provided context
- If the context doesn't have enough info, say so honestly
- Keep answers concise and friendly
- When recommending movies, mention the rating and year
- If asked about actors or directors, list their movies
- When showing similar movies, explain why they are similar
"""

SIMILARITY_KEYWORDS = [
    "similar", "like", "recommend", "related",
    "same", "also", "watch next", "suggestions"
]

def is_similarity_question(question: str) -> bool:
    """Check if the question is asking for similar movies."""
    question_lower = question.lower()
    return any(kw in question_lower for kw in SIMILARITY_KEYWORDS)

def extract_movie_from_question(question: str) -> str:
    """Use LLM to extract movie name from similarity question."""
    client_temp = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client_temp.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Extract the movie title from this question.
Reply with ONLY the movie title, nothing else.

Question: {question}
Movie title:"""
        }],
        max_tokens=20,
        temperature=0
    )
    return response.choices[0].message.content.strip()

def ask(question: str, chat_history: list = []) -> str:
    context = ""

    # Step 1: Check if similarity question
    if is_similarity_question(question):
        movie = extract_movie_from_question(question)
        print(f"[Chain] Similarity question detected for: {movie}")
        context = get_similarity_context(movie)

    # Step 2: Try Text-to-Cypher
    if not context:
        context = text_to_cypher_context(question)

    # Step 3: Fall back to keyword retriever
    if not context:
        print("[Chain] Falling back to keyword retriever")
        context = get_movie_context(question)

    # Step 4: Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in chat_history[-6:]:
        messages.append(msg)

    messages.append({
        "role": "user",
        "content": f"""
Context from movie knowledge graph:
{context}

User question: {question}
"""
    })

    # Step 5: Call Groq LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )

    return response.choices[0].message.content


# Quick test
if __name__ == "__main__":
    questions = [
        "Find movies similar to Inception",
        "What movies are like Avatar?",
        "Which director has made the most movies?",
    ]

    history = []
    for q in questions:
        print(f"\nQ: {q}")
        answer = ask(q, history)
        print(f"A: {answer}\n")
        print("-" * 60)
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": answer})