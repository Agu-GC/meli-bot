from datetime import datetime
from pydantic import BaseModel

class Conversation(BaseModel):
    user_id: str
    user_msg: str
    bot_msg: str
    timestamp: datetime = datetime.now()

class Document(BaseModel):
    content: str
    name: str

class DocumentChunk(BaseModel):
    text: str
    source: str
    chunk_id: str = None
    embedding: list[float] = None
