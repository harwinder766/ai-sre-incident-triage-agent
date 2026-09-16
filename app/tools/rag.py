from __future__ import annotations

from typing import Any

from app.rag.retriever import HybridRetriever


class RAGTool:

    def __init__(
        self,
        retriever: HybridRetriever,
    ) -> None:
        self._retriever = retriever

    def search(
        self,
        query: str,
    ) -> list[dict[str, Any]]:

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        documents = self._retriever.invoke(
            query
        )

        return [
            {
                "content": document.page_content,
                "source": document.metadata.get(
                    "source_path"
                ),
                "chunk_id": document.metadata.get(
                    "chunk_id"
                ),
                "rrf_score": document.metadata.get(
                    "rrf_score"
                ),
            }
            for document in documents
        ]