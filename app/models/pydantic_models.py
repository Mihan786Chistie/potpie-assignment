from pydantic import BaseModel

class PRAnalysisRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str = None
