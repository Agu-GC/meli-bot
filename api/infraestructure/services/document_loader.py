import os
import pdfplumber
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from api.domain.entities import Document, DocumentChunk
from api.application.interfaces.document_loader import IDocumentLoader

logger = logging.getLogger(__name__)

class DocumentLoader(IDocumentLoader):
    """A service for loading and split pdf documents from a folder."""

    def __init__(self, chunk_size=700, chunk_overlap=50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def load_pdfs(self, folder_path: str) -> list[Document]:
        documents = []
        logging.info(f"Loading PDFs from folder: {folder_path}")
        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):
                path = os.path.join(folder_path, filename)
                try:
                    text = ""
                    with pdfplumber.open(path) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                    
                    documents.append(
                        Document(content=text, name=filename)
                    )
                except Exception as e:
                    logger.error(f"Error loading {filename}: {str(e)}")
                    print(f"Error loading {filename}: {str(e)}")
        return documents

    def split_text(self, document: Document) -> list[DocumentChunk]:
        """Splits the content of a document into smaller chunks."""
        logger.info(f"Splitting document: {document.name}")
        chunks = self.splitter.split_text(document.content)
        return [
            DocumentChunk(
                text=chunk,
                source=document.name,
                chunk_id=f"{document.name}_chunk_{i}",
                metadata={"source": document.name}
            )
            for i, chunk in enumerate(chunks)
        ]