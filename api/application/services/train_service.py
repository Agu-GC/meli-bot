import logging
from api.application.interfaces.train_service import ITrainService
from api.application.interfaces.document_loader import IDocumentLoader
from api.application.interfaces.embedding_service import IEmbeddingService
from api.application.interfaces.database_repository import IDatabaseRepository

logger = logging.getLogger(__name__)

class TrainService(ITrainService):
    def __init__(self, folder_path: str, document_loader:IDocumentLoader, database_repo=IDatabaseRepository, embedding_service=IEmbeddingService):
        """Initialize the TrainService with a DocumentLoader instance."""
        self.document_loader = document_loader
        self.embeding_service = embedding_service
        self.database_repo = database_repo
        self.folder_path = folder_path

    def train(self) -> None:
        """Train the model with the company information."""
        documents = self.document_loader.load_pdfs(self.folder_path)
        for document in documents:
            if not self.database_repo.has_source(document.name):
                logger.info(f"Loading document: {document.name}")
                chunks = self.document_loader.split_text(document)
                for chunk in chunks:
                    self.embeding_service.embed(chunk)
                    self.database_repo.add_chunk(chunk)
            else:
                logger.info(f"Document {document.name} already exists in the database, skipping.")
        