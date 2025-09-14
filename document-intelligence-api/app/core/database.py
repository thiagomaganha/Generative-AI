from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import uuid

from app.core.config import settings

# Database setup
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    document_type = Column(String, nullable=False)
    status = Column(String, default="pending")
    
    # Analysis results
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    key_entities = Column(JSON, nullable=True)
    topics = Column(JSON, nullable=True)
    sentiment = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Processing info
    job_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)