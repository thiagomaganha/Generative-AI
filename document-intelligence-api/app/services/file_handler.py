import os
import aiofiles
from typing import Optional, Tuple
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.models.document import DocumentType

class FileHandler:
    """Handle file upload, validation, and text extraction"""
    
    @staticmethod
    def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate uploaded file"""
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"File type {file_ext} not supported"
        
        return True, None
    
    @staticmethod
    async def save_file(file: UploadFile, document_id: str) -> str:
        """Save uploaded file to disk"""
        try:
            file_ext = os.path.splitext(file.filename)[1].lower()
            filename = f"{document_id}{file_ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            return file_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str, document_type: DocumentType) -> str:
        """Extract text from document based on type"""
        try:
            if document_type == DocumentType.PDF:
                return FileHandler._extract_pdf_text(file_path)
            elif document_type == DocumentType.DOCX:
                return FileHandler._extract_docx_text(file_path)
            elif document_type == DocumentType.TXT:
                return FileHandler._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
    
    @staticmethod
    def _extract_pdf_text(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    @staticmethod
    def _extract_docx_text(file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    
    @staticmethod
    def _extract_txt_text(file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()