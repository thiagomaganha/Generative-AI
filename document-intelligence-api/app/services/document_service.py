from sqlalchemy.orm import Session
from app.models.types import DocumentAnalysis
from app.models.document import DocumentResponse, DocumentType, DocumentStatus
from app.services.file_handler import FileHandler
from app.core.database import Document
from typing import List
import uuid
import os

class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    async def create_document(self, file) -> DocumentResponse:
        is_valid, error_msg = FileHandler.validate_file(file)
        if not is_valid:
            raise ValueError(error_msg)

        document_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1].lower()
        document_type = DocumentType.PDF if file_ext == '.pdf' else \
                    DocumentType.DOCX if file_ext == '.docx' else \
                    DocumentType.TXT
        
        file_path = await FileHandler.save_file(file, document_id)
        
        # Start async processing
        from app.tasks.document_tasks import process_document_task
        task = process_document_task.delay(document_id, file_path, document_type.value)
        
        db_document = Document(
            id=document_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file.size if file.size else 0,
            document_type=document_type.value,
            status=DocumentStatus.PENDING.value,
            job_id=task.id  
        )
        
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)

        return DocumentResponse(
            id=document_id,
            filename=file.filename,
            file_size=file.size if file.size else 0,
            document_type=document_type,
            status=DocumentStatus.PENDING,
            created_at=db_document.created_at,
            job_id=task.id
        )
        
    async def get_document(self, document_id) -> DocumentResponse:
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(status_code=404, detail="Document not found")
        
        analysis = None
        if doc.summary or doc.key_entities or doc.topics or doc.sentiment:
            analysis = DocumentAnalysis(
                summary=doc.summary,
                key_entities=doc.key_entities or [],
                topics=doc.topics or [],
                sentiment=doc.sentiment,
                confidence_score=doc.confidence_score or 0.0
            )
        
        return DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_size=doc.file_size,
                document_type=DocumentType(doc.document_type),
                status=DocumentStatus(doc.status),
                created_at=doc.created_at,
                job_id=doc.job_id,
                analysis=analysis
        )

    async def list_documents(self, skip, limit) -> List[DocumentResponse]:
        db_documents = self.db.query(Document).offset(skip).limit(limit).all()
        if not db_documents:
            raise ValueError(status_code=404, detail="No documents found")
    
        responses = []
        for doc in db_documents:
            analysis = None
            if doc.summary or doc.key_entities or doc.topics or doc.sentiment:
                analysis = DocumentAnalysis(
                    summary=doc.summary,
                    key_entities=doc.key_entities or [],
                    topics=doc.topics or [],
                    sentiment=doc.sentiment,
                    confidence_score=doc.confidence_score or 0.0
                )
            
            responses.append(
                DocumentResponse(
                    id=doc.id,
                    filename=doc.filename,
                    file_size=doc.file_size,
                    document_type=DocumentType(doc.document_type),
                    status=DocumentStatus(doc.status),
                    created_at=doc.created_at,
                    job_id=doc.job_id,
                    analysis=analysis
                )
            )
        
        return responses
