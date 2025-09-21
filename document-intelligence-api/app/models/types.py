from pydantic import BaseModel
from typing import List

class DocumentAnalysis(BaseModel):
    summary: str
    key_entities: List[str]
    topics: List[str]
    sentiment: str
    confidence_score: float
