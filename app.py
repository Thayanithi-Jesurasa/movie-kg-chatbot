import sys
import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import streamlit.components.v1 as components
from rag.chain import ask
from graph.visualize import get_movie_graph

# Page config
st.set_page_config(
    page_title="🎬 Movie Knowledge Graph Chatbot",
    page_icon="🎬",
    layout="wide"
)

# Header
st.title("🎬 Movie Knowledge Graph Chatbot")
st.caption("Powered by Neo4j Knowledge Graph + Groq LLaMA3")

# Layout — chat on left, graph on right
chat_col, graph_col = st.columns([1.2, 1])

with chat_col:
    st.subheader("💬 Chat")

    # Initialize state
    if "messages" not in st.session_state:
        st.session_state.messages   = []
        st.session_state.history    = []
        st.session_state.last_movie = None

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested questions
    if len(st.session_state.messages) == 0:
        st.markdown("#### 💡 Try asking:")
        cols = st.columns(2)
        suggestions = [
            "Tell me about Inception",
            "What did Christopher Nolan direct?",
            "Recommend top action movies",
            "Who acted in Avatar?",
        ]
        for i, suggestion in enumerate(suggestions):
            if cols[i % 2].button(suggestion):
                st.session_state.pending = suggestion
                st.rerun()

    # Handle suggested question
    if "pending" in st.session_state:
        prompt = st.session_state.pop("pending")
    else:
        prompt = st.chat_input("Ask anything about movies...")

    # Process input
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge graph..."):
                response = ask(prompt, st.session_state.history)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.history.append({"role": "user",      "content": prompt})
        st.session_state.history.append({"role": "assistant", "content": response})

        # Extract movie name using LLM
        extract_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        extract_response = extract_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Extract just ONE movie title from this text.
Reply with ONLY the movie title, nothing else, no punctuation.

Text: {response}

Movie title:"""
            }],
            max_tokens=20,
            temperature=0
        )
        movie_name = extract_response.choices[0].message.content.strip()
        st.session_state.last_movie = movie_name
        st.rerun()

with graph_col:
    st.subheader("🕸️ Knowledge Graph")

    if st.session_state.get("last_movie"):
        st.caption(f"Showing graph for: **{st.session_state.last_movie}**")
        with st.spinner("Building graph..."):
            html_path = get_movie_graph(st.session_state.last_movie)

        if html_path and os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            components.html(html_content, height=500)
        else:
            st.info("No graph found. Try asking about a specific movie!")
    else:
        st.info("💡 Ask about a movie to see its knowledge graph here!")