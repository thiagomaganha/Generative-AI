from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

from app.core.config import settings
from app.api import documents

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Intelligent document processing and analysis API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    documents.router, 
    prefix=f"{settings.API_V1_STR}/documents", 
    tags=["documents"]
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Document Intelligence API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "upload_dir_exists": os.path.exists(settings.UPLOAD_DIR)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)