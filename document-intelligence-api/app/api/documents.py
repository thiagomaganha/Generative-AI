from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from datetime import datetime

from app.models.document import DocumentResponse, DocumentType, DocumentStatus
from app.services.file_handler import FileHandler
from app.core.database import get_db, Document

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    
    # Validate file
    is_valid, error_msg = FileHandler.validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Determine document type
    file_ext = os.path.splitext(file.filename)[1].lower()
    document_type = DocumentType.PDF if file_ext == '.pdf' else \
                   DocumentType.DOCX if file_ext == '.docx' else \
                   DocumentType.TXT
    
    try:
        # Save file
        file_path = await FileHandler.save_file(file, document_id)
        
        # Create database record
        db_document = Document(
            id=document_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file.size if file.size else 0,
            document_type=document_type.value,
            status=DocumentStatus.PENDING.value
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Return response
        return DocumentResponse(
            id=document_id,
            filename=file.filename,
            file_size=file.size if file.size else 0,
            document_type=document_type,
            status=DocumentStatus.PENDING,
            created_at=db_document.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get document by ID"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=db_document.id,
        filename=db_document.filename,
        file_size=db_document.file_size,
        document_type=DocumentType(db_document.document_type),
        status=DocumentStatus(db_document.status),
        created_at=db_document.created_at,
        job_id=db_document.job_id
    )

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List documents with pagination"""
    db_documents = db.query(Document).offset(skip).limit(limit).all()
    
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_size=doc.file_size,
            document_type=DocumentType(doc.document_type),
            status=DocumentStatus(doc.status),
            created_at=doc.created_at,
            job_id=doc.job_id
        )
        for doc in db_documents
    ]
