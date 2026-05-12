"""Tests for the ChromaDB wrapper.

We don't run a real ChromaDB server in unit tests — instead we verify that:
- construction is lazy (no connection until first use),
- the result parser correctly flattens Chroma's nested-list response format.
"""

from __future__ import annotations

from src.rag.chroma_client import ChromaClient, _parse_query_result


def test_construction_does_not_connect() -> None:
    client = ChromaClient(host="nonexistent.invalid", port=1)
    # If construction tried to connect, this would have raised already.
    assert client._client is None


def test_parse_query_result_flattens_nested_lists() -> None:
    raw = {
        "ids": [["a", "b"]],
        "documents": [["doc-a", "doc-b"]],
        "metadatas": [[{"src": "x"}, {"src": "y"}]],
        "distances": [[0.1, 0.4]],
    }
    hits = _parse_query_result(raw)
    assert len(hits) == 2
    assert hits[0].id == "a"
    assert hits[0].document == "doc-a"
    assert hits[0].metadata == {"src": "x"}
    assert hits[0].distance == 0.1
    assert hits[1].id == "b"


def test_parse_query_result_empty() -> None:
    assert _parse_query_result({"ids": [[]]}) == []
    assert _parse_query_result({}) == []


def test_parse_query_result_handles_missing_optional_fields() -> None:
    raw = {"ids": [["only-id"]]}
    hits = _parse_query_result(raw)
    assert len(hits) == 1
    assert hits[0].id == "only-id"
    assert hits[0].document == ""
    assert hits[0].metadata == {}
    assert hits[0].distance == 0.0
