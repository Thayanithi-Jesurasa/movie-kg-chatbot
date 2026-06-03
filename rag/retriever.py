import os
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI      = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Words to ignore when searching
STOP_WORDS = {
    "who", "what", "when", "where", "which", "how", "tell", "about",
    "movie", "movies", "film", "films", "acted", "action", "actor",
    "actress", "director", "directed", "starring", "recommend", "some",
    "give", "list", "best", "top", "good", "great", "watched", "seen",
    "with", "that", "this", "from", "have", "been", "were", "they",
    "their", "there", "into", "more", "also", "than", "then", "does"
}

def extract_keywords(question: str) -> list:
    words = re.findall(r'\b\w+\b', question.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def get_movie_context(question: str) -> str:
    question_lower = question.lower()
    keywords       = extract_keywords(question)
    context_parts  = []

    with driver.session() as session:

        # 1. Movie search by title
        for word in keywords:
            result = session.run("""
                MATCH (m:Movie)
                WHERE toLower(m.title) CONTAINS $word
                OPTIONAL MATCH (a:Actor)-[:ACTED_IN]->(m)
                OPTIONAL MATCH (d:Director)-[:DIRECTED]->(m)
                OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
                RETURN m.title AS title,
                       m.overview AS overview,
                       m.rating AS rating,
                       m.year AS year,
                       collect(DISTINCT a.name) AS actors,
                       collect(DISTINCT d.name) AS directors,
                       collect(DISTINCT g.name) AS genres
                LIMIT 3
            """, word=word)

            for r in result:
                context_parts.append(
                    f"Movie: {r['title']} ({r['year']}) | "
                    f"Rating: {r['rating']} | "
                    f"Genres: {', '.join(r['genres'])} | "
                    f"Director: {', '.join(r['directors'])} | "
                    f"Actors: {', '.join(r['actors'])} | "
                    f"Overview: {r['overview']}"
                )

        # 2. Actor search
        for word in keywords:
            result = session.run("""
                MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)
                WHERE toLower(a.name) CONTAINS $word
                RETURN a.name AS actor,
                       collect(m.title) AS movies
                LIMIT 3
            """, word=word)

            for r in result:
                context_parts.append(
                    f"Actor: {r['actor']} appeared in: "
                    f"{', '.join(r['movies'])}"
                )

        # 3. Director search
        for word in keywords:
            result = session.run("""
                MATCH (d:Director)-[:DIRECTED]->(m:Movie)
                WHERE toLower(d.name) CONTAINS $word
                RETURN d.name AS director,
                       collect(m.title) AS movies
                LIMIT 3
            """, word=word)

            for r in result:
                context_parts.append(
                    f"Director: {r['director']} directed: "
                    f"{', '.join(r['movies'])}"
                )

        # 4. Genre search
        genres = ["action", "comedy", "drama", "horror", "romance",
                  "thriller", "animation", "sci-fi", "science fiction",
                  "adventure", "crime", "fantasy"]
        for genre in genres:
            if genre in question_lower:
                result = session.run("""
                    MATCH (m:Movie)-[:IN_GENRE]->(g:Genre)
                    WHERE toLower(g.name) CONTAINS $genre
                    RETURN m.title AS title,
                           m.rating AS rating,
                           m.year AS year
                    ORDER BY m.rating DESC
                    LIMIT 5
                """, genre=genre)

                movies = [f"{r['title']} ({r['year']}, rating: {r['rating']})"
                          for r in result]
                if movies:
                    context_parts.append(
                        f"Top {genre} movies: {', '.join(movies)}"
                    )

    if not context_parts:
        return "No specific movie information found for this query."

    return "\n".join(context_parts)