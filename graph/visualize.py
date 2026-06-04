import os
from neo4j import GraphDatabase
from pyvis.network import Network
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

def get_movie_graph(movie_title: str) -> str:
    """
    Query Neo4j for a movie and its connections,
    build an interactive HTML graph and return the path.
    """
    net = Network(height="500px", width="100%",
                  bgcolor="#222222", font_color="white")
    net.barnes_hut()

    with driver.session() as session:
        result = session.run("""
            MATCH (m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($title)
            OPTIONAL MATCH (a:Actor)-[:ACTED_IN]->(m)
            OPTIONAL MATCH (d:Director)-[:DIRECTED]->(m)
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
            RETURN m, collect(DISTINCT a) AS actors,
                   collect(DISTINCT d) AS directors,
                   collect(DISTINCT g) AS genres
            LIMIT 1
        """, title=movie_title)

        record = result.single()
        if not record:
            return None

        movie = record["m"]
        movie_id = f"movie_{movie['id']}"

        # Add movie node
        net.add_node(movie_id,
                     label=movie["title"],
                     color="#e74c3c",
                     size=30,
                     title=f"Rating: {movie['rating']}\nYear: {movie['year']}")

        # Add actor nodes
        for actor in record["actors"]:
            if actor:
                actor_id = f"actor_{actor['name']}"
                net.add_node(actor_id,
                             label=actor["name"],
                             color="#3498db",
                             size=20,
                             title="Actor")
                net.add_edge(actor_id, movie_id, label="ACTED_IN")

        # Add director nodes
        for director in record["directors"]:
            if director:
                dir_id = f"dir_{director['name']}"
                net.add_node(dir_id,
                             label=director["name"],
                             color="#2ecc71",
                             size=25,
                             title="Director")
                net.add_edge(dir_id, movie_id, label="DIRECTED")

        # Add genre nodes
        for genre in record["genres"]:
            if genre:
                genre_id = f"genre_{genre['name']}"
                net.add_node(genre_id,
                             label=genre["name"],
                             color="#f39c12",
                             size=15,
                             title="Genre")
                net.add_edge(movie_id, genre_id, label="IN_GENRE")

    # Save to HTML file
    output_path = "graph_output.html"
    net.save_graph(output_path)
    return output_path