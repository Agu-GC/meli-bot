import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from application.interfaces.rag_service import IRAGService

logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

def create_router(rag_service: IRAGService) -> APIRouter:
    router = APIRouter()
    
    @router.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        try:
            logger.info(f"Received chat request from user {request.user_id}: {request.message}")
            response = rag_service.generate_response(
                user_id=request.user_id,
                user_query=request.message
            )
            return {"response": response}
        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing request: {str(e)}"
            )
    
    return router