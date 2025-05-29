from sentence_transformers import SentenceTransformer
from api.application.interfaces.embedding_service import IEmbeddingService
from api.domain.entities import DocumentChunk


class EmbeddingService(IEmbeddingService):
    def __init__(self, model_name: str="sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the embedding service with a specific model."""
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.dimensions = self.model.get_sentence_embedding_dimension()
        
    def get_embedding(self, text: str) -> list[float]:
        """Generate an embedding for the given text."""
        return self.model.encode(text).tolist()

    def embed(self, chunk: DocumentChunk) -> None:
        """Generate and assign embedding for a single DocumentChunk"""
        embedding = self.model.encode(chunk.text).tolist()
        chunk.embedding = embedding
        
    def embed_all(self, chunks: list[DocumentChunk]) -> None:
        """Generate and assign embeddings for a list of DocumentChunks"""
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts).tolist()
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]

    def get_dimensions(self) -> int:
        """Return the dimensions of the embeddings."""
        return self.dimensions
    
    def get_model_name(self) -> str:
        """Return the name of the embedding model."""
        return self.model_name