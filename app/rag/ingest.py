from __future__ import annotations

from pathlib import Path
from typing import Iterable
from functools import cached_property
import chromadb

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from langchain_huggingface import HuggingFaceEmbeddings


class DocumentLoader:
    """
    Responsible only for:
    - discovering supported files
    - loading files
    - normalizing metadata
    - returning LangChain Documents
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt",
        ".md",
    }

    def __init__(
        self,
        source_dir: str | Path,
    ):
        self.source_dir = Path(source_dir)

        if not self.source_dir.exists():
            raise FileNotFoundError(
                f"Source directory does not exist: "
                f"{self.source_dir}"
            )

        if not self.source_dir.is_dir():
            raise NotADirectoryError(
                f"Expected directory: "
                f"{self.source_dir}"
            )

    def discover_files(self) -> list[Path]:
        """
        Find all supported files recursively.
        """

        files = [
            path
            for path in self.source_dir.rglob("*")
            if path.is_file()
            and path.suffix.lower()
            in self.SUPPORTED_EXTENSIONS
        ]

        return sorted(files)

    def load_file(
        self,
        path: Path,
    ) -> list[Document]:
        """
        Load one file using the appropriate
        LangChain loader.
        """

        extension = path.suffix.lower()

        if extension == ".pdf":
            loader = PyPDFLoader(
                str(path)
            )

        elif extension in {".txt", ".md"}:
            loader = TextLoader(
                str(path),
                encoding="utf-8",
            )

        else:
            raise ValueError(
                f"Unsupported file type: "
                f"{extension}"
            )

        documents = loader.lazy_load()

        return self._normalize_metadata(
            documents,
            path,
        )

    def load_all(self) -> Iterable[Document]:
        """
        Load every supported document in
        the source directory.
        """

        for path in self.discover_files():

            for document in self.load_file(path):

                yield document

    def _normalize_metadata(
        self,
        documents: Iterable[Document],
        path: Path,
    ) -> list[Document]:
        """
        Add consistent application-level metadata.
        """

        normalized = []

        for document in documents:

            document.metadata.update(
                {
                    "source": str(path),
                    "source_path": str(
                        path.relative_to(
                            self.source_dir
                        )
                    ),
                    "filename": path.name,
                    "file_type": path.suffix.lower(),
                }
            )

            normalized.append(document)

        return normalized


class DocumentSplitter:
    """
    Responsible for splitting documents into
    smaller chunks for embedding and retrieval.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be a positive integer."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap must be a "
                "non-negative integer."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be less "
                "than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self._splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=[
                    "\n\n",
                    "\n",
                    ". ",
                    ",",
                    " ",
                    "",
                ],
                length_function=len,
            )
        )

    def split(
        self,
        documents: Iterable[Document],
    ) -> list[Document]:
        """
        Split documents into smaller chunks.
        """

        chunks = self._splitter.split_documents(
            list(documents)
        )

        self._add_chunk_metadata(chunks)

        return chunks

    @staticmethod
    def _add_chunk_metadata(
        chunks: list[Document],
    ) -> None:
        """
        Add deterministic chunk metadata based
        on document source.
        """

        source_counts: dict[str, int] = {}

        for chunk in chunks:

            source = chunk.metadata.get(
                "source_path",
                chunk.metadata.get(
                    "source",
                    "doc",
                ),
            )

            chunk_idx = source_counts.get(
                source,
                0,
            )

            chunk.metadata["chunk_id"] = (
                f"{source}::chunk_{chunk_idx}"
            )

            chunk.metadata["chunk_index"] = (
                chunk_idx
            )

            source_counts[source] = (
                chunk_idx + 1
            )

class ChromaStore:
    """
    ChromaDB vector store for storing and retrieving
    document chunks.
    """

    def __init__(
        self,
        persist_directory: str = "data/chroma",
        collection_name: str = "sre_documents",
        embedding_model: str = (
            "sentence-transformers/all-MiniLM-L6-v2"
        ),
    ) -> None:

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={
                "device": "cpu",
            },
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": "cosine",
                },
            )
        )

    def add_documents(
        self,
        documents: Iterable[Document],
    ) -> None:
        """
        Embed and store document chunks.
        """

        documents = list(documents)

        if not documents:
            return

        texts = [
            document.page_content
            for document in documents
        ]

        metadatas = [
            document.metadata
            for document in documents
        ]

        ids = [
            document.metadata["chunk_id"]
            for document in documents
        ]

        embeddings = (
            self.embedding_model.embed_documents(
                texts
            )
        )

        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def search(
        self,
        query: str,
        k: int = 5,
        service: str | None = None,
        category: str | None = None,
    ) -> list[Document]:
        """
        Perform semantic similarity search.
        """

        if not query.strip():
            return []

        if k <= 0:
            raise ValueError(
                "k must be a positive integer."
            )

        total_documents = (
            self.collection.count()
        )

        if total_documents == 0:
            return []

        k = min(k, total_documents)

        query_embedding = (
            self.embedding_model.embed_query(
                query
            )
        )

        where = {}

        if service is not None:
            where["service"] = service

        if category is not None:
            where["category"] = category

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=k,
            where=where if where else None,
        )

        documents = []

        for text, metadata in zip(
            results["documents"][0],
            results["metadatas"][0],
        ):
            documents.append(
                Document(
                    page_content=text,
                    metadata=metadata,
                )
            )

        return documents

    def count(self) -> int:
        """
        Return the number of stored chunks.
        """

        return self.collection.count()

    