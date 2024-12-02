from fastapi import APIRouter

router = APIRouter()

@router.post("/analyze-pr")
async def analyze_pr():
    return {"message": "Analyze PR"}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    return {"task_id": task_id, "status": "completed"}

@router.get("/results/{task_id}")
async def get_results(task_id: str):
    return {"task_id": task_id, "results": "results"}