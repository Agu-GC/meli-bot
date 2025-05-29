import chromadb
import logging
from typing import Any
from chromadb.config import Settings
from chromadb.errors import ChromaError
from api.application.interfaces.database_repository import IDatabaseRepository
from api.domain.entities import DocumentChunk

logger = logging.getLogger(__name__)

class DatabaseRepository(IDatabaseRepository):
    _instance = None

    def __init__(self, host: str = "chroma-db", port: int = "8000", collection_name: str = "documents", auth_token: str = ""):
        if not DatabaseRepository._instance:
            self._initialize(host, port, collection_name, auth_token)
            DatabaseRepository._instance = self


    def _initialize(self, host: str = "chroma-db", port: int = "8000", collection_name: str = "documents", auth_token: str = ""):
        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(
                    chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                    chroma_client_auth_credentials=auth_token
                )
            )
            self.client.heartbeat()
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Métrica de similitud - coseno recomendada para embeddings de texto
            )
        except ChromaError as e:
            raise RuntimeError(f"Chroma connection failed: {str(e)}") from e


    def add_chunk(self, chunk: DocumentChunk) -> None:
        """Adds a document chunk to the database."""
        try:
            self.collection.add(
                ids=[chunk.chunk_id],
                embeddings=[chunk.embedding],
                documents=[chunk.text],
                metadatas=[{"source": chunk.source}] if chunk.source else None
            )
        except ChromaError as e:
            raise ValueError(f"Failed to add document: {str(e)}") from e


    def search_similar(self, query_embedding: list[float], n_results: int = 5, filter: dict = None) -> dict[str, list[list[Any]]]:
        """Searches for similar document chunks based on the query embedding."""
        try:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter
            )
        except ChromaError as e:
            raise ValueError(f"Search failed: {str(e)}") from e

    def is_empty(self) -> bool:
        """Verifies if the database is empty."""
        try:
            return self.collection.count() == 0
        except ChromaError as e:
            raise ValueError(f"Failed to check if database is empty: {str(e)}") from e
        
    def has_source(self, file_name: str) -> bool:
        """Verifies if a document with the given source exists in the database."""
        try:
            if not file_name:
                return False
            results = self.collection.get(
                where={"source": file_name},
                limit=1
            )
            return len(results["ids"]) > 0
        except ChromaError as e:
            raise ValueError(f"Failed to check sources: {str(e)}") from e