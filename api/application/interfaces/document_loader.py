from abc import ABC, abstractmethod
from api.domain.entities import Document, DocumentChunk

class IDocumentLoader(ABC):
    @abstractmethod
    def load_pdfs(self, folder_path: str) -> list[Document]:
        """Load a PDF file and return its text content."""
        pass
    
    @abstractmethod
    def split_text(self, document: Document) -> list[DocumentChunk]:
        """Split text into chunks of a specified size."""
        pass
