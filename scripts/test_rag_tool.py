from app.dependencies import rag_tool


def main() -> None:

    query = (
        "payment API database connection "
        "pool exhausted"
    )

    print("🔹 Searching RAG...")

    results = rag_tool.search(query)

    print(
        f"\nRetrieved {len(results)} documents:\n"
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print(f"\n--- Result {rank} ---")

        print(
            "Chunk ID:",
            result["chunk_id"],
        )

        print(
            "Source:",
            result["source"],
        )

        print(
            "RRF Score:",
            result["rrf_score"],
        )

        print(
            "Content:",
            result["content"][:500],
        )


if __name__ == "__main__":
    main()