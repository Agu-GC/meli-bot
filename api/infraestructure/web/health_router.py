from fastapi import APIRouter

def create_router() -> APIRouter:
    router = APIRouter()
    
    @router.get("/health", include_in_schema=False)
    async def health_check():
        return {"status": "ok"}
    
    return router