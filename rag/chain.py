import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Handle imports whether running from root or rag/ folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from retriever import get_movie_context
from text_to_cypher import text_to_cypher_context
load_dotenv()

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
"""

def ask(question: str, chat_history: list = []) -> str:
    # Step 1: Try Text-to-Cypher first (more powerful)
    context = text_to_cypher_context(question)

    # Step 2: Fall back to keyword retriever if no results
    if not context:
        print("[Chain] Text-to-Cypher returned no results, falling back to keyword retriever")
        context = get_movie_context(question)

    # Step 3: Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add chat history for multi-turn conversation
    for msg in chat_history[-6:]:
        messages.append(msg)

    # Add context + question
    messages.append({
        "role": "user",
        "content": f"""
Context from movie knowledge graph:
{context}

User question: {question}
"""
    })

    # Step 4: Call Groq LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )

    return response.choices[0].message.content


# Quick test
if __name__ == "__main__":
    print("Testing RAG chain with Text-to-Cypher...\n")

    questions = [
        "Which actors have worked with both action and comedy movies?",
        "What are the highest rated movies directed by Christopher Nolan?",
        "Which director has made the most movies?",
    ]

    history = []
    for q in questions:
        print(f"Q: {q}")
        answer = ask(q, history)
        print(f"A: {answer}\n")
        print("-" * 60)
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": answer})