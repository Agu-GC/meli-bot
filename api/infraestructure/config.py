import os
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    app_name: str = "Chatbot RAG"
    description: str = "Chatbot"
    log_level: str = "INFO"
    
    folder_path: str = "./documents"
    
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int =  int(os.getenv("REDIS_DB", 0))

    chroma_host: str = os.getenv("CHROMA_HOST", "chroma-db")
    chroma_port: int = int(os.getenv("CHROMA_PORT", 8000))
    chroma_auth_token: str = os.getenv("CHROMA_AUTH_TOKEN", "")
    chroma_collection: str = "documents"
    
    chunk_size: int = 700
    chunk_overlap: int = 50
    
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    ollama_host: str = os.getenv("OLLAMA_HOST", "localhost")
    ollama_port: str = int(os.getenv("OLLAMA_PORT", "11434"))
    ollama_model: str = os.getenv("OLLAMA_MODEL", "phi3:instruct")
    ollama_model_prompt_format: str = os.getenv("OLLAMA_MODEL_PROMPT_FORMAT", "<|user|>\n{prompt}<|end|>\n<|assistant|>")
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", 240))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def load_settings() -> AppSettings:
    """Load application settings from environment variables or .env file."""
    return AppSettings()