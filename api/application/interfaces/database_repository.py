from abc import ABC, abstractmethod
from api.domain.entities import DocumentChunk

class IDatabaseRepository(ABC):
    @abstractmethod
    def add_chunk(self, chunk: DocumentChunk) -> None:
        """add a conversation chunk to the database."""
        pass

    @abstractmethod
    def search_similar(self, query_embedding: list[float], n_results: int = 5, filter: dict = None) -> list[dict]:
        """search for similar conversation chunks based on the query embedding."""
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        """Check if the database collection is empty."""
        pass
    
    @abstractmethod
    def has_source(self, file_name: str) -> bool:
        """Check if a document with the given source already exists in the database."""
        pass
