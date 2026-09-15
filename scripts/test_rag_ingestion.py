from app.rag.ingest import DocumentLoader
from app.rag.ingest import DocumentSplitter
from app.rag.ingest import ChromaStore


CORPUS_DIR = "app/rag/corpus"


def main():

    print("🔹 Loading documents...")

    loader = DocumentLoader(CORPUS_DIR)

    documents = loader.load_all()

    print("🔹 Splitting documents...")

    splitter = DocumentSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split(documents)

    print(
        f"Created {len(chunks)} chunks."
    )

    print("🔹 Storing in ChromaDB...")

    store = ChromaStore(
        persist_directory="data/chroma",
        collection_name="sre_documents",
    )

    store.add_documents(chunks)

    print(
        f"Stored chunks: {store.count()}"
    )

    print("✅ Ingestion completed.")


if __name__ == "__main__":
    main()