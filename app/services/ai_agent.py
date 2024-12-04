import logging
from celery import Task
from app.core.celery_app import celery_app
from app.services.github import get_pr_files
from langchain_openai import OpenAI
from langchain_openai import AzureChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from app.core.config import settings
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyzePRTask(Task):
    abstract = True

    def __init__(self):
        super().__init__()
        self.llm = AzureChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            azure_endpoint="https://sbl-gpt-giveaway.openai.azure.com",
            api_version="2024-08-01-preview",
            azure_deployment="gpt-4",
            temperature=0  # Any other required parameters
        )
        self.agent = self._create_agent()

    def _create_agent(self):
        tools = [
            Tool(
                name="Analyze Code",
                func=self._analyze_code,
                description="Analyze Python code for style, bugs, and improvements."
            )
        ]
        return initialize_agent(tools, self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

    def _analyze_code(self, code: str) -> str:
        prompt = f"""
        Analyze the following code for:
        1. Code style and formatting issues
        2. Potential bugs or errors
        3. Performance improvements
        4. Best practices

        Code:
        {code}

        Provide your analysis in a structured JSON format:
        - Issue Type (style/bug/performance/etc.)
        - Line number
        - Description of the issue
        - Suggestion for fixing the issue
        """
        response = self.llm([prompt])
        return response
    
    def _parse_analysis(self, analysis: str) -> list:
        issues = []
        current_issue = {}
        for line in analysis.split('\n'):
            line = line.strip()
            if line.startswith("- Issue Type:"):
                if current_issue:
                    issues.append(current_issue)
                current_issue = {"type": line.split(":")[1].strip().lower()}
            elif line.startswith("- Line number:"):
                current_issue["line"] = int(line.split(":")[1].strip())
            elif line.startswith("- Description:"):
                current_issue["description"] = line.split(":")[1].strip()
            elif line.startswith("- Suggestion:"):
                current_issue["suggestion"] = line.split(":")[1].strip()
        if current_issue:
            issues.append(current_issue)
        return issues

@celery_app.task(base=AnalyzePRTask, bind=True)
def analyze_pr(self, pr_data: dict):
    logger.info(f"Starting analysis for PR: {pr_data['pr_number']}")
    try:
        repo_url = pr_data['repo_url']
        pr_number = pr_data['pr_number']
        github_token = pr_data['github_token']

        files = get_pr_files(repo_url, pr_number, github_token)
        logger.info(f"Retrieved {len(files)} files from the PR")

        result = {
            "task_id": "",
            "status": "completed",
            "results": {
                "files": [],
                "summary": {
                    "total_files": len(files),
                    "total_issues": 0,
                    "critical_issues": 0
                }
            }
        }

        for file in files:
            logger.info(f"Analyzing file: {file['name']}")
            
            # Perform code analysis
            analysis = self.agent.run(f"Analyze this code: {file['content']}")

            print(analysis)

            file_issues = self._parse_analysis(analysis)

            total_file_issues = len(file_issues)
            critical_file_issues = sum(1 for issue in file_issues if issue['type'] in ['bug', 'security'])

            result['results']['files'].append({
                "name": file['name'],
                "issues": file_issues
            })

            result['results']['summary']['total_issues'] += total_file_issues
            result['results']['summary']['critical_issues'] += critical_file_issues

        return json.dumps(result)

    except Exception as e:
        logger.error(f"Error during PR analysis: {str(e)}")
        error_result = {
            "task_id": self.request.id,
            "status": "failed",
            "error": str(e)
        }
        return json.dumps(error_result)