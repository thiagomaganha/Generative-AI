from celery import Celery, current_task
import os
import asyncio
from typing import Dict, Any
from datetime import datetime
import logging

from app.core.config import settings
from app.services.file_handler import FileHandler
from app.services.ai_analyzer import AIAnalyzer
from app.services.vector_store import VectorStore
from app.models.document import DocumentType
from app.core.database import SessionLocal, Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "document_intelligence",
    broker = settings.REDIS_URL,
    backend = settings.REDIS_URL,
)

celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_pool='solo',  # Use solo pool for Windows
    task_routes={
        'app.tasks.document_tasks.process_document_task': {'queue': 'default'},
        'app.tasks.document_tasks.health_check': {'queue': 'default'}
    }
)

@celery_app.task(bind=True)
def process_document_task(self, document_id: str, file_path: str, document_type: str) -> Dict[str, Any]:
    """Async task to process uploaded document"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Starting processing...', 'document_id': document_id})

        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")
        
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': 'Extracting text...', 'document_id': document_id})
        doc_type = DocumentType(document_type)

        text_content = FileHandler.extract_text(file_path, doc_type)
        
        if not text_content.strip():
            raise Exception("No text content found in document")
        
        logger.info(f"Extracted {len(text_content)} characters from {document_id}")
        
        ai_analyzer = AIAnalyzer()
        vector_store = VectorStore()
        
        self.update_state(state='PROGRESS', meta={'progress': 40, 'status': 'Analyzing document...', 'document_id': document_id})
        
        analysis = asyncio.run(
            ai_analyzer.analyze_document(text_content, os.path.basename(file_path))
        )
        
        self.update_state(state='PROGRESS', meta={'progress': 60, 'status': 'Generating embeddings...', 'document_id': document_id})
        
        # Generate embeddings
        embeddings = asyncio.run(
            ai_analyzer.generate_embeddings(text_content)
        )
        
        self.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Storing in vector database...', 'document_id': document_id})
        
        # Initialize and store in vector database
        asyncio.run(vector_store.initialize())
        
        metadata = {
            'filename': os.path.basename(file_path),
            'document_type': document_type,
            'file_size': os.path.getsize(file_path),
            'summary': analysis.summary,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        asyncio.run(
            vector_store.add_document(document_id, text_content, embeddings, metadata)
        )

        logger.info(f"Stored {document_id} in vector database")
        
        self.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Updating database...'})
        
        db = SessionLocal()
        try:
            db_document = db.query(Document).filter(Document.id == document_id).first()
            if db_document:
                db_document.status = "completed"
                db_document.content = text_content[:1000]  # Store preview
                db_document.summary = analysis.summary
                db_document.key_entities = analysis.key_entities
                db_document.topics = analysis.topics
                db_document.sentiment = analysis.sentiment
                db_document.confidence_score = analysis.confidence_score
                db_document.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Updated database record for {document_id}")
        finally:
            db.close()
        
        result = {
            'document_id': document_id,
            'status': 'completed',
            'analysis': {
                'summary': analysis.summary,
                'key_entities': analysis.key_entities,
                'topics': analysis.topics,
                'sentiment': analysis.sentiment,
                'confidence_score': analysis.confidence_score
            },
            'text_preview': text_content[:500],
            'processed_at': datetime.utcnow().isoformat()
        }

        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': 'Completed'})

        logger.info(f"Document processing completed successfully for {document_id}")
        return result
        
    except Exception as e:
        # Update database record with error
        db = SessionLocal()
        try:
            db_document = db.query(Document).filter(Document.id == document_id).first()
            if db_document:
                db_document.status = "failed"
                db_document.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        raise Exception(f"Document processing failed: {str(e)}")

@celery_app.task
def health_check():
    """Simple health check task"""
    logger.info("Health check task executed")
    return {
        'status': 'healthy', 
        'timestamp': datetime.utcnow().isoformat(),
        'worker': 'active',
        'task_id': health_check.request.id if hasattr(health_check, 'request') else 'unknown'
    }