import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

def get_similar_movies(movie_title: str, limit: int = 5) -> list:
    """
    Find similar movies based on shared actors, directors,
    genres and keywords using graph traversal.
    """
    with driver.session() as session:
        result = session.run("""
            // Find the target movie
            MATCH (m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($title)
            WITH m LIMIT 1

            // Find similar movies through shared connections
            MATCH (m)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(other:Movie)
            WHERE other <> m
            WITH m, other, COUNT(DISTINCT g) AS shared_genres

            OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(other)
            WITH m, other, shared_genres, COUNT(DISTINCT a) AS shared_actors

            OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Director)-[:DIRECTED]->(other)
            WITH m, other, shared_genres, shared_actors,
                 COUNT(DISTINCT d) AS shared_directors

            OPTIONAL MATCH (m)-[:HAS_KEYWORD]->(k:Keyword)<-[:HAS_KEYWORD]-(other)
            WITH m, other, shared_genres, shared_actors,
                 shared_directors, COUNT(DISTINCT k) AS shared_keywords

            // Calculate similarity score
            WITH other,
                 (shared_genres * 2 +
                  shared_actors * 3 +
                  shared_directors * 4 +
                  shared_keywords * 1) AS similarity_score,
                 shared_genres,
                 shared_actors,
                 shared_directors,
                 shared_keywords

            WHERE similarity_score > 0
            RETURN other.title      AS title,
                   other.rating     AS rating,
                   other.year       AS year,
                   similarity_score  AS score,
                   shared_genres    AS genres,
                   shared_actors    AS actors,
                   shared_directors AS directors,
                   shared_keywords  AS keywords
            ORDER BY similarity_score DESC
            LIMIT $limit
        """, title=movie_title, limit=limit)

        return [dict(r) for r in result]


def get_similarity_context(movie_title: str) -> str:
    """Format similar movies as context string for LLM."""
    similar = get_similar_movies(movie_title)

    if not similar:
        return ""

    lines = [f"Movies similar to '{movie_title}':"]
    for m in similar:
        reasons = []
        if m["actors"] > 0:
            reasons.append(f"{m['actors']} shared actor(s)")
        if m["directors"] > 0:
            reasons.append(f"same director")
        if m["genres"] > 0:
            reasons.append(f"{m['genres']} shared genre(s)")
        if m["keywords"] > 0:
            reasons.append(f"{m['keywords']} shared keyword(s)")

        lines.append(
            f"- {m['title']} ({m['year']}) | "
            f"Rating: {m['rating']} | "
            f"Similarity score: {m['score']} | "
            f"Reasons: {', '.join(reasons)}"
        )

    return "\n".join(lines)


# Test
if __name__ == "__main__":
    movies = ["Inception", "Avatar", "The Dark Knight"]
    for movie in movies:
        print(f"\nMovies similar to '{movie}':")
        print(get_similarity_context(movie))
        print("-" * 60)