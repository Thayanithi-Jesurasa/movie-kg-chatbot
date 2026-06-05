import os
from groq import Groq
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Tell the LLM about your graph structure
SCHEMA = """
You are an expert in Neo4j Cypher queries.
Here is the graph schema:

Nodes:
- Movie: {id, title, overview, rating, year}
- Actor: {name}
- Director: {name}
- Genre: {name}
- Keyword: {name}

Relationships:
- (Actor)-[:ACTED_IN]->(Movie)
- (Director)-[:DIRECTED]->(Movie)
- (Movie)-[:IN_GENRE]->(Genre)
- (Movie)-[:HAS_KEYWORD]->(Keyword)

Rules for generating Cypher:
- Always use OPTIONAL MATCH for relationships that might not exist
- Always use toLower() for string comparisons
- Always add LIMIT 10 at the end
- Return meaningful fields, not just IDs
- Only return the Cypher query, nothing else, no explanation, no markdown

- Important: The sci-fi genre is stored as "Science Fiction" not "sci-fi"
- Important: Genre names are case sensitive, use exact names like "Action", "Comedy", "Drama", "Science Fiction", "Thriller", "Romance", "Adventure", "Crime", "Fantasy", "Horror", "Animation"
"""

def generate_cypher(question: str) -> str:
    """Use LLM to generate a Cypher query from a natural language question."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SCHEMA},
            {"role": "user",   "content": f"Generate a Cypher query for: {question}"}
        ],
        max_tokens=300,
        temperature=0
    )
    cypher = response.choices[0].message.content.strip()

    # Clean up if LLM adds markdown backticks
    cypher = cypher.replace("```cypher", "").replace("```", "").strip()
    return cypher


def run_cypher(cypher: str) -> list:
    """Run a Cypher query on Neo4j and return results."""
    try:
        with driver.session() as session:
            result = session.run(cypher)
            return [dict(r) for r in result]
    except Exception as e:
        print(f"Cypher error: {e}")
        return []


def text_to_cypher_context(question: str) -> str:
    """Full pipeline: question → Cypher → Neo4j → context string."""
    print(f"\n[Text-to-Cypher] Question: {question}")

    # Step 1: Generate Cypher
    cypher = generate_cypher(question)
    print(f"[Text-to-Cypher] Generated Cypher:\n{cypher}")

    # Step 2: Run on Neo4j
    results = run_cypher(cypher)
    print(f"[Text-to-Cypher] Results: {results}")

    if not results:
        return ""

    # Step 3: Format results as context string
    context_lines = []
    for r in results:
        line = " | ".join([f"{k}: {v}" for k, v in r.items() if v])
        context_lines.append(line)

    return "\n".join(context_lines)


# Test
if __name__ == "__main__":
    questions = [
        "Which actors have worked in both action and comedy movies?",
        "What are the highest rated movies directed by Christopher Nolan?",
        "Which director has made the most movies?",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        context = text_to_cypher_context(q)
        print(f"Context:\n{context}")
        print("-" * 60)