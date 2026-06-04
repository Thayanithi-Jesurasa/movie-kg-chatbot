import re

response = """Here are the top action movie recommendations:

1. **The Dark Knight** (2008, rating: 8.2)
2. **Inception** (2010, rating: 8.1)
"""

# Test regex
movie_match = re.search(r'\*\*(.+?)\*\*', response)
if movie_match:
    print("Found:", movie_match.group(1))
else:
    print("No match found")

# Test graph
from graph.visualize import get_movie_graph
result = get_movie_graph("The Dark Knight")
print("Graph result:", result)