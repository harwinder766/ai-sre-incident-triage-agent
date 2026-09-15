from pathlib import Path

from langchain_core.documents import Document

from app.rag.ingest import DocumentLoader
from app.rag.ingest import DocumentSplitter
from app.rag.ingest import ChromaStore


def test_document_discovery(tmp_path: Path):
    """
    Test that supported files are discovered recursively.
    """

    corpus = tmp_path / "corpus"
    corpus.mkdir()

    (corpus / "runbook.md").write_text(
        "# Database Runbook\n\n"
        "Database connection pool exhausted.",
        encoding="utf-8",
    )

    (corpus / "notes.txt").write_text(
        "Payment API notes.",
        encoding="utf-8",
    )

    (corpus / "ignored.py").write_text(
        "print('ignored')",
        encoding="utf-8",
    )

    loader = DocumentLoader(corpus)

    files = loader.discover_files()

    assert len(files) == 2

    assert files[0].suffix in {".md", ".txt"}
    assert files[1].suffix in {".md", ".txt"}


def test_document_loading(tmp_path: Path):
    """
    Test that files are converted into LangChain Documents.
    """

    corpus = tmp_path / "corpus"
    corpus.mkdir()

    file = corpus / "database.md"

    file.write_text(
        "# Database Runbook\n\n"
        "Connection pool exhaustion can cause "
        "payment failures.",
        encoding="utf-8",
    )

    loader = DocumentLoader(corpus)

    documents = list(loader.load_all())

    assert len(documents) == 1

    document = documents[0]

    assert isinstance(document, Document)

    assert "Database Runbook" in document.page_content

    assert document.metadata["filename"] == "database.md"

    assert document.metadata["file_type"] == ".md"

    assert "source" in document.metadata


def test_document_splitting(tmp_path: Path):
    """
    Test that documents are split into chunks.
    """

    document = Document(
        page_content="Database failure. " * 200,
        metadata={
            "source": "database.md",
        },
    )

    splitter = DocumentSplitter(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = splitter.split([document])

    assert len(chunks) > 1

    for chunk in chunks:
        assert isinstance(chunk, Document)

        assert "chunk_id" in chunk.metadata

        assert "chunk_index" in chunk.metadata


def test_chunk_ids_are_deterministic():
    """
    Test that chunks from the same source receive
    sequential chunk IDs.
    """

    document = Document(
        page_content="Database failure. " * 100,
        metadata={
            "source": "database.md",
        },
    )

    splitter = DocumentSplitter(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = splitter.split([document])

    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[1].metadata["chunk_index"] == 1

    assert (
        chunks[0].metadata["chunk_id"]
        == "database.md::chunk_0"
    )

    assert (
        chunks[1].metadata["chunk_id"]
        == "database.md::chunk_1"
    )


def test_chroma_store(tmp_path: Path):
    """
    Test embedding and persistence in ChromaDB.
    """

    documents = [
        Document(
            page_content=(
                "Database connection pool "
                "exhausted in payment API."
            ),
            metadata={
                "source": "database.md",
                "chunk_id": "database.md::chunk_0",
                "chunk_index": 0,
                "service": "payment-api",
                "category": "database",
            },
        ),
        Document(
            page_content=(
                "Payment API latency increased "
                "because of slow requests."
            ),
            metadata={
                "source": "latency.md",
                "chunk_id": "latency.md::chunk_0",
                "chunk_index": 0,
                "service": "payment-api",
                "category": "performance",
            },
        ),
    ]

    store = ChromaStore(
        persist_directory=str(
            tmp_path / "chroma"
        ),
        collection_name="test_sre_documents",
    )

    store.add_documents(documents)

    assert store.count() == 2