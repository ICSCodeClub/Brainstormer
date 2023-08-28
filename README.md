# Brainstormer
Finds further research areas into a topic!
<br>
<br>
## Installation
To install, first, ensure [Poetry](python-poetry.org) is installed. You can install it with
```
pip install poetry
```

Then, run
```
poetry install
```

Register for an Azure Cognitive Search API key <a href="https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/">Here</a>. Save this key in `key.txt` at the root of the repository. An Azure Cognitive Search API key is required to find answers and branching topics, but is free for low-use scenarios.

You can now run the program with
```
poetry run python3 webapp.py
```
