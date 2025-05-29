from abc import ABC, abstractmethod
from api.domain.entities import DocumentChunk

class IEmbeddingService(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> list[float]:
        """Generate an embedding for the given text."""
        pass

    @abstractmethod
    def embed(self, chunk: DocumentChunk) -> None:
        """Generate an embedding for the given text."""
        pass

    @abstractmethod
    def embed_all(self, chunks: list[DocumentChunk]) -> None:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    def get_dimensions(self) -> int:
        """Return the dimensions of the embeddings."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the name of the embedding model."""
        pass
