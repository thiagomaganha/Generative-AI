from pydantic_settings import BaseSettings
from typing import Set

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document Intelligence API"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".docx", ".txt"}
    
    # Vector Database Configuration
    FAISS_INDEX_PATH: str = "data/faiss_index"
    VECTOR_DIMENSION: int = 1536  # OpenAI embedding dimension
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./documents.db"
    
    class Config:
        env_file = ".env"

settings = Settings()