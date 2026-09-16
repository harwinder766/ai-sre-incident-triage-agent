from __future__ import annotations

from app.rag.ingest import (
    DocumentLoader,
    DocumentSplitter,
    ChromaStore,
)
from app.rag.retriever import HybridRetriever
from app.tools.rag import RAGTool


def create_rag_tool() -> RAGTool:

    # -----------------------------------------
    # 1. Load documents
    # -----------------------------------------

    loader = DocumentLoader(
        "app/rag/corpus"
    )

    documents = loader.load_all()

    # -----------------------------------------
    # 2. Split documents
    # -----------------------------------------

    splitter = DocumentSplitter()

    chunks = splitter.split(
        documents
    )

    # -----------------------------------------
    # 3. Load ChromaDB
    # -----------------------------------------

    vector_store = ChromaStore(
        persist_directory="data/chroma",
        collection_name="sre_documents",
    )

    # -----------------------------------------
    # 4. Create hybrid retriever
    # -----------------------------------------

    hybrid_retriever = HybridRetriever(
        documents=chunks,
        vector_store=vector_store,
        bm25_k=10,
        vector_k=10,
        final_k=5,
        rrf_k=60,
    )

    # -----------------------------------------
    # 5. Create RAG tool
    # -----------------------------------------

    return RAGTool(
        retriever=hybrid_retriever
    )