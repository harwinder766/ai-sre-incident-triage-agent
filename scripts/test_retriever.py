from app.rag.ingest import DocumentLoader, DocumentSplitter, ChromaStore
from app.rag.retriever import HybridRetriever


def main() -> None:
    # -----------------------------------------
    # 1. Load documents
    # -----------------------------------------

    loader = DocumentLoader("app/rag/corpus")

    print("🔹 Loading documents...")

    documents = loader.load_all()

    # -----------------------------------------
    # 2. Split documents
    # -----------------------------------------

    splitter = DocumentSplitter()

    print("🔹 Splitting documents...")

    chunks = splitter.split(documents)

    print(f"Created {len(chunks)} chunks.")

    # -----------------------------------------
    # 3. Create/load Chroma store
    # -----------------------------------------

    print("🔹 Loading ChromaDB...")

    vector_store = ChromaStore(
        persist_directory="data/chroma",
        collection_name="sre_documents",
    )

    print(
        f"Chroma contains "
        f"{vector_store.count()} chunks."
    )

    # -----------------------------------------
    # 4. Create Hybrid Retriever
    # -----------------------------------------

    print("🔹 Creating hybrid retriever...")

    retriever = HybridRetriever(
        documents=chunks,
        vector_store=vector_store,
        bm25_k=10,
        vector_k=10,
        final_k=5,
        rrf_k=60,
    )

    # -----------------------------------------
    # 5. Test queries
    # -----------------------------------------

    queries = [
        "database connection pool exhausted",
        "payment API high latency",
        "out of memory error",
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)

        results = retriever.invoke(query)

        print(
            f"\nRetrieved {len(results)} documents:\n"
        )

        for rank, document in enumerate(
            results,
            start=1,
        ):
            print(f"\n--- Result {rank} ---")

            print(
                "Chunk ID:",
                document.metadata.get(
                    "chunk_id"
                ),
            )

            print(
                "RRF Score:",
                document.metadata.get(
                    "rrf_score"
                ),
            )

            print(
                "Source:",
                document.metadata.get(
                    "source_path"
                ),
            )

            print(
                "Content:",
                document.page_content[:500],
            )


if __name__ == "__main__":
    main()