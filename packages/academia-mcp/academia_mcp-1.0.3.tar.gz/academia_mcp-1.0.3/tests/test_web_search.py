import json

from academia_mcp.tools import web_search


def test_web_search() -> None:
    result = web_search("autoregressive models path-star graphs", provider="tavily", limit=20)
    assert "The Mystery of the Pathological" in result
    assert "The Pitfalls of Next-Token Prediction" in result
    results = json.loads(result)
    assert len(results["results"]) == 20


def test_web_search_exa() -> None:
    result = web_search("autoregressive models path-star graphs", provider="exa", limit=10)
    assert result
    results = json.loads(result)
    assert len(results["results"]) == 10


def test_web_search_brave() -> None:
    result = web_search("autoregressive models path-star graphs", provider="brave", limit=10)
    assert "The Mystery of the Pathological" in result
    results = json.loads(result)
    assert len(results["results"]) == 10
