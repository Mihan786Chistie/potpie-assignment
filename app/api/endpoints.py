import logging
from fastapi import APIRouter, HTTPException
from app.core.celery_app import celery_app
from app.models.pydantic_models import PRAnalysisRequest
from celery.result import AsyncResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze-pr")
async def analyze_pr(request: PRAnalysisRequest):
    """
    Create a Celery task to analyze a PR.
    """
    logger.info(f"Received request to analyze PR: {request.pr_number}")
    task = celery_app.send_task("app.services.ai_agent.analyze_pr", args=[request.model_dump()])
    logger.info(f"Task created with ID: {task.id}")
    return {"task_id": task.id}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """
    Get the current status of a task.
    """
    logger.info(f"Checking status for task: {task_id}")
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
    }

@router.get("/results/{task_id}")
async def get_results(task_id: str):
    """
    Get the results of a completed task or return an error if the task failed.
    """
    logger.info(f"Fetching results for task: {task_id}")
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.status == 'SUCCESS':
        return task_result.result
    elif task_result.status == 'PENDING':
        return {"status": "pending"}
    else:
        logger.error(f"Task failed: {task_id}")
        raise HTTPException(status_code=400, detail=f"Task failed: {str(task_result.info)}")
