import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "rag"))

import streamlit as st
from rag.chain import ask

# Page config
st.set_page_config(
    page_title="🎬 Movie Knowledge Graph Chatbot",
    page_icon="🎬",
    layout="centered"
)

# Header
st.title("🎬 Movie Chatbot")
st.caption("Powered by Neo4j Knowledge Graph + Groq LLaMA3")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.history  = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Suggested questions
if len(st.session_state.messages) == 0:
    st.markdown("### 💡 Try asking:")
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

# Handle suggested question click
if "pending" in st.session_state:
    prompt = st.session_state.pop("pending")
else:
    prompt = st.chat_input("Ask anything about movies...")

# Process input
if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge graph..."):
            response = ask(prompt, st.session_state.history)
        st.markdown(response)

    # Save to history
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.history.append({"role": "user", "content": prompt})
    st.session_state.history.append({"role": "assistant", "content": response})