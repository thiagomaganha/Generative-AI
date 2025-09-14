from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

class DocumentAnalysis(BaseModel):
    summary: Optional[str] = None
    key_entities: List[str] = []
    topics: List[str] = []
    sentiment: Optional[str] = None
    confidence_score: Optional[float] = None

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    document_type: DocumentType
    status: DocumentStatus
    analysis: Optional[DocumentAnalysis] = None
    created_at: datetime
    job_id: Optional[str] = None

class SearchQuery(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class SearchResult(BaseModel):
    document_id: str
    filename: str
    similarity_score: float
    relevant_chunk: str

