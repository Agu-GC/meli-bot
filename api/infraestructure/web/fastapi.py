import logging
from fastapi import FastAPI
from api.infraestructure.config import AppSettings
from api.infraestructure.web import chat_router, health_router
from api.application.services.rag_service import RAGService
from api.application.services.train_service import TrainService
from api.application.interfaces.llm_service import ILLMService
from api.application.interfaces.embedding_service import IEmbeddingService  
from api.application.interfaces.conversation_repository import IConversationRepository
from api.application.interfaces.database_repository import IDatabaseRepository
from api.application.interfaces.document_loader import IDocumentLoader

logger = logging.getLogger(__name__)

def create_application(
        conversation_repo: IConversationRepository, 
        database_repo: IDatabaseRepository, 
        embedding_service:IEmbeddingService, 
        llm_service: ILLMService, 
        document_loader: IDocumentLoader, 
        settings: AppSettings
        ):
    """Create Chat bot FastAPI"""
    
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version="1.0.0"
    )

    logger.info("Starting application with settings: %s", settings.model_dump())
    rag_service = RAGService(
        conversation_repo=conversation_repo,
        database_repo=database_repo,
        embedding_service=embedding_service,
        llm_service=llm_service
    )
    
    train_service = TrainService(
        folder_path=settings.folder_path,
        document_loader=document_loader,
        database_repo=database_repo,
        embedding_service=embedding_service,
    )
    train_service.train()

    app.include_router(
        chat_router.create_router(rag_service=rag_service),
        prefix="/api/v1",
        tags=["chat"]
    )
    app.include_router(
        health_router.create_router(),
        prefix="/health"
    )
    
    return app