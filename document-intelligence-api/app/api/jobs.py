from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.models.job import JobResponse, JobStatus
from app.tasks.document_tasks import celery_app
from datetime import datetime

router = APIRouter()

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Get job status by ID"""
    try:
        # Get Celery task result
        task_result = AsyncResult(job_id, app=celery_app)
        
        if task_result.state == 'PENDING':
            status = JobStatus.PENDING
            progress = 0
            result = None
            error_message = None
        elif task_result.state == 'PROGRESS':
            status = JobStatus.PROCESSING
            meta = task_result.info or {}
            progress = meta.get('progress', 0)
            result = {"status": meta.get('status', 'Processing...')}
            error_message = None
        elif task_result.state == 'SUCCESS':
            status = JobStatus.COMPLETED
            progress = 100
            result = task_result.result
            error_message = None
        elif task_result.state == 'FAILURE':
            status = JobStatus.FAILED
            progress = 0
            result = None
            error_message = str(task_result.info)
        else:
            status = JobStatus.PROCESSING
            progress = 50
            result = None
            error_message = None
        
        return JobResponse(
            job_id=job_id,
            status=status,
            progress=progress,
            result=result,
            error_message=error_message,
            created_at=task_result.date_done or datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    try:
        celery_app.control.revoke(job_id, terminate=True)
        return {"message": f"Job {job_id} cancellation requested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")