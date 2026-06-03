import os
from groq import Groq
from dotenv import load_dotenv
from rag.retriever import get_movie_context

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
    # Step 1: Get context from Neo4j graph
    context = get_movie_context(question)

    # Step 2: Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add chat history for multi-turn conversation
    for msg in chat_history[-6:]:  # keep last 6 messages
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

    # Step 3: Call Groq LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )

    return response.choices[0].message.content


# Quick test
if __name__ == "__main__":
    print("Testing RAG chain...\n")

    questions = [
        "Tell me about Inception",
        "What movies did Christopher Nolan direct?",
        "Recommend some top rated action movies",
    ]

    history = []
    for q in questions:
        print(f"Q: {q}")
        answer = ask(q, history)
        print(f"A: {answer}\n")
        print("-" * 60)

        # update history
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": answer})