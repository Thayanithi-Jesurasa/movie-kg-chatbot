import os
import json
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI      = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def load_data():
    movies_df  = pd.read_csv("data/tmdb_5000_movies.csv")
    credits_df = pd.read_csv("data/tmdb_5000_credits.csv")

    # merge on title
    df = movies_df.merge(credits_df, on="title")
    df = df.head(200)  # load first 200 movies to keep it light
    return df

def create_graph(tx, row):
    # parse JSON columns
    genres   = json.loads(row["genres"])
    cast     = json.loads(row["cast"])[:5]      # top 5 actors
    crew     = json.loads(row["crew"])
    keywords = json.loads(row["keywords"])[:5]  # top 5 keywords

    director = next((c["name"] for c in crew if c["job"] == "Director"), None)

    # Create Movie node
    tx.run("""
        MERGE (m:Movie {id: $id})
        SET m.title    = $title,
            m.overview = $overview,
            m.rating   = $rating,
            m.year     = $year
    """, id=row["id"], title=row["title"],
         overview=row["overview"],
         rating=row["vote_average"],
         year=str(row["release_date"])[:4])

    # Create Genre nodes + relationships
    for g in genres:
        tx.run("""
            MERGE (g:Genre {name: $name})
            MERGE (m:Movie {id: $id})
            MERGE (m)-[:IN_GENRE]->(g)
        """, name=g["name"], id=row["id"])

    # Create Actor nodes + relationships
    for actor in cast:
        tx.run("""
            MERGE (a:Actor {name: $name})
            MERGE (m:Movie {id: $id})
            MERGE (a)-[:ACTED_IN]->(m)
        """, name=actor["name"], id=row["id"])

    # Create Director node + relationship
    if director:
        tx.run("""
            MERGE (d:Director {name: $name})
            MERGE (m:Movie {id: $id})
            MERGE (d)-[:DIRECTED]->(m)
        """, name=director, id=row["id"])

    # Create Keyword nodes + relationships
    for kw in keywords:
        tx.run("""
            MERGE (k:Keyword {name: $name})
            MERGE (m:Movie {id: $id})
            MERGE (m)-[:HAS_KEYWORD]->(k)
        """, name=kw["name"], id=row["id"])

def main():
    df = load_data()
    print(f"Loading {len(df)} movies into Neo4j...")

    with driver.session() as session:
        for i, row in df.iterrows():
            session.execute_write(create_graph, row)
            if i % 20 == 0:
                print(f"  {i} movies loaded...")

    print("✅ Done! Graph loaded successfully.")
    driver.close()

if __name__ == "__main__":
    main()