import re

response = """Christopher Nolan directed:
The Dark Knight Rises
The Dark Knight
Interstellar
Inception
Batman Begins
"""

# Fix - use \s* to handle different line endings
m4 = re.search(r':\s*\n\s*(.+)', response)
print("After colon match:", m4.group(1).strip() if m4 else "None")

# Alternative - just grab any capitalized line
m5 = re.search(r'\n([A-Z][a-zA-Z\s]+)', response)
print("Capital line match:", m5.group(1).strip() if m5 else "None")