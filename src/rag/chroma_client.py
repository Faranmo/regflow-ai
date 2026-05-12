"""ChromaDB client wrapper.

A thin layer over `chromadb.HttpClient` that:
- defers the connection until first use (so importing this module doesn't
  require Chroma to be running),
- exposes a small surface (`get_or_create_collection`, `add`, `query`) so the
  rest of the app does not depend on the chromadb API directly,
- normalises results into a typed dataclass so call sites get IDE help.

Phase 2 will plug a real embedding function in here; for now the wrapper accepts
pre-computed embeddings so it can be unit-tested without a model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from src.core.config import settings

if TYPE_CHECKING:
    from chromadb import ClientAPI
    from chromadb.api.models.Collection import Collection


@dataclass(frozen=True)
class QueryHit:
    id: str
    document: str
    metadata: dict[str, Any]
    distance: float


class ChromaClient:
    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        self._host = host or settings.chroma_host
        self._port = port or settings.chroma_port
        self._client: ClientAPI | None = None

    def _connect(self) -> ClientAPI:
        if self._client is None:
            import chromadb

            self._client = chromadb.HttpClient(host=self._host, port=self._port)
        return self._client

    def get_or_create_collection(self, name: str) -> Collection:
        return self._connect().get_or_create_collection(name=name)

    def add(
        self,
        collection_name: str,
        *,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(
        self,
        collection_name: str,
        *,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[QueryHit]:
        collection = self.get_or_create_collection(collection_name)
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )
        return _parse_query_result(result)

    def reset(self) -> None:
        """Drop the cached client (useful in tests)."""
        self._client = None


def _parse_query_result(result: dict[str, Any]) -> list[QueryHit]:
    """Chroma returns parallel lists nested one level deep per query. Flatten."""
    if not result.get("ids") or not result["ids"][0]:
        return []
    ids = result["ids"][0]
    documents = result.get("documents", [[]])[0] or [""] * len(ids)
    metadatas = result.get("metadatas", [[]])[0] or [{}] * len(ids)
    distances = result.get("distances", [[]])[0] or [0.0] * len(ids)
    return [
        QueryHit(
            id=ids[i],
            document=documents[i] or "",
            metadata=metadatas[i] or {},
            distance=float(distances[i]),
        )
        for i in range(len(ids))
    ]


_default_client: ChromaClient | None = None


def get_chroma_client() -> ChromaClient:
    """Return a process-wide ChromaClient instance (lazy)."""
    global _default_client
    if _default_client is None:
        _default_client = ChromaClient()
    return _default_client
