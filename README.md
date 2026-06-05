# 🎬 Movie Knowledge Graph Chatbot

## 🚀 Live Demo
👉 [Try it here]
https://movie-kg-chatbot-tlo2a33qe5eckfka2s6s9l.streamlit.app/

A **GraphRAG-powered** movie chatbot that answers questions using a 
Neo4j knowledge graph and Groq LLaMA3. Built as a portfolio project 
to demonstrate knowledge graph + LLM integration.

![Demo](assets/demo.gif)

## ✨ Features

- 💬 **Natural Language Q&A** — Ask anything about movies
- 🕸️ **Live Graph Visualization** — See movie connections in real time
- 🔍 **Text-to-Cypher** — LLM auto-generates graph queries
- 🎯 **Movie Similarity** — Graph-based recommendations
- 🔄 **Hybrid Retrieval** — Text-to-Cypher + keyword fallback

## 🏗️ Architecture
User Question
│
▼
┌─────────────────────┐
│  Similarity Check   │  ← "Find movies like X"
└─────────────────────┘
│ No
▼
┌─────────────────────┐
│   Text-to-Cypher    │  ← LLM generates Cypher query
│   (LLaMA3 + Groq)   │
└─────────────────────┘
│ No results
▼
┌─────────────────────┐
│  Keyword Retriever  │  ← Fallback keyword search
└─────────────────────┘
│
▼
┌─────────────────────┐
│     Neo4j Graph     │  ← Runs query, returns context
└─────────────────────┘
│
▼
┌─────────────────────┐
│   Groq LLaMA3 LLM   │  ← Generates final answer
└─────────────────────┘
│
▼
💬 Answer + 🕸️ Graph

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Graph Database | Neo4j 2026.04 |
| LLM | Groq (LLaMA 3.3 70b) |
| Graph Querying | Cypher + Text-to-Cypher |
| Similarity | Graph traversal scoring |
| Visualization | Pyvis |
| UI | Streamlit |
| Dataset | TMDB 5000 Movies |
| Language | Python 3.13 |

## 📁 Project Structure
movie_kg_chatbot/
│
├── graph/
│   ├── load_graph.py      # Loads TMDB data into Neo4j
│   ├── visualize.py       # Pyvis graph visualization
│   └── similarity.py      # Graph-based movie similarity
│
├── rag/
│   ├── retriever.py       # Keyword-based Cypher retriever
│   ├── text_to_cypher.py  # LLM-generated Cypher queries
│   └── chain.py           # RAG chain combining all retrievers
│
├── app.py                 # Streamlit UI
├── requirements.txt       # Dependencies
└── README.md

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/movie-kg-chatbot.git
cd movie-kg-chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up `.env` file
GROQ_API_KEY=your_groq_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

### 4. Download dataset
Download [TMDB 5000 Movies](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
and place both CSV files in the `data/` folder.

### 5. Load graph
```bash
python graph/load_graph.py
```

### 6. Run the app
```bash
streamlit run app.py
```

## 💡 Example Questions

- *"Tell me about Inception"*
- *"What did Christopher Nolan direct?"*
- *"Find movies similar to The Dark Knight"*
- *"Which actors have worked in both action and comedy movies?"*
- *"Which director has made the most movies?"*
- *"What are the highest rated sci-fi movies?"*

## 🧠 Key Concepts

**GraphRAG** — Retrieval Augmented Generation using a knowledge graph
instead of a vector store, enabling structured and explainable retrieval.

**Text-to-Cypher** — Natural language is converted to Cypher graph 
queries by an LLM, allowing flexible querying without hardcoded templates.

**Graph Similarity** — Movies are scored by counting shared nodes 
(actors, directors, genres, keywords) with weighted importance.