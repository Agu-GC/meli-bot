import logging
from api.infraestructure.config import load_settings
from api.infraestructure.web.fastapi import create_application
from api.infraestructure.repositories.conversation_repository import ConversationRepository
from api.infraestructure.repositories.database_repository import DatabaseRepository
from api.infraestructure.services.document_loader import DocumentLoader
from api.infraestructure.services.embedding_service import EmbeddingService
from api.infraestructure.services.llm_service import LLMService


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.propagate = False
    app_logger = logging.getLogger(__name__)
    app_logger.setLevel(logging.INFO)


configure_logging()
logger = logging.getLogger(__name__)


def main():
    """Main function to initialize the FastAPI application and its components."""
    
    settings = load_settings()
    logger.info("Configuration loaded: %s", settings.model_dump())
    
    try:
        conversation_repo = ConversationRepository(host= settings.redis_host, port= settings.redis_port, db= settings.redis_db)
        database_repo = DatabaseRepository(host= settings.chroma_host, port= settings.chroma_port, collection_name= settings.chroma_collection, auth_token= settings.chroma_auth_token)
        document_loader = DocumentLoader(chunk_size= settings.chunk_size, chunk_overlap= settings.chunk_overlap)
        embadding_service = EmbeddingService(model_name= settings.embedding_model_name)
        llm_service = LLMService(base_url= settings.ollama_host, port= settings.ollama_port, model_name=settings.ollama_model, timeout=settings.ollama_timeout, prompt_format=settings.ollama_model_prompt_format)

        logger.info("Main components initialized successfully")
        
    except Exception as e:
        logger.exception("Error initializing main components: %s", str(e))
        raise RuntimeError("Critical error during application startup") from e

    app = create_application(
        conversation_repo= conversation_repo, 
        database_repo= database_repo, 
        llm_service= llm_service, 
        embedding_service= embadding_service, 
        document_loader= document_loader,
        settings= settings
        )

    
    return app

app = main()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )