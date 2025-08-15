import os
import json
from typing import Optional

from academia_mcp.utils import post_with_retries


EXA_SEARCH_URL = "https://api.exa.ai/search"
TAVILY_SEARCH_URL = "https://api.tavily.com/search"
EXCLUDE_DOMAINS = ["chatpaper.com"]


def web_search(
    query: str,
    limit: Optional[int] = 20,
    provider: Optional[str] = "tavily",
) -> str:
    """
    Search the web using Exa Search or Tavily and return normalized results.

    Returns a JSON object serialized to a string. The structure is: {"results": [...]}
    Every item in the "results" has at least the following fields: ("title", "url")
    Use `json.loads` to deserialize the result if you want to get specific fields.

    Args:
        query: The search query, required.
        limit: The maximum number of items to return. 20 by default, maximum 25.
        provider: The provider to use. "exa" or "tavily". "tavily" by default.
    """

    assert isinstance(query, str), "Error: Your search query must be a string"
    assert query.strip(), "Error: Your query should not be empty"
    assert isinstance(limit, int), "Error: limit should be an integer"
    assert 0 < limit <= 25, "Error: limit should be between 1 and 25"
    assert provider in ("exa", "tavily"), "Error: provider must be either 'exa' or 'tavily'"

    if provider == "exa":
        key = os.getenv("EXA_API_KEY", "")
        assert key, "Error: EXA_API_KEY is not set and no api_key was provided"
        payload = {
            "query": query,
            "type": "auto",
            "numResults": limit,
            "context": False,
            "excludeDomains": EXCLUDE_DOMAINS,
            "contents": {
                "text": False,
                "highlights": {
                    "numSentences": 5,
                },
                "context": False,
            },
        }

        response = post_with_retries(EXA_SEARCH_URL, payload, key)
        results = response.json()["results"]

    elif provider == "tavily":
        key = os.getenv("TAVILY_API_KEY", "")
        assert key, "Error: TAVILY_API_KEY is not set and no api_key was provided"
        payload = {
            "query": query,
            "max_results": limit,
            "auto_parameters": True,
            "exclude_domains": EXCLUDE_DOMAINS,
        }
        response = post_with_retries(TAVILY_SEARCH_URL, payload, key)
        results = response.json()["results"]

    return json.dumps({"results": results}, ensure_ascii=False)
