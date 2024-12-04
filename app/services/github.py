import requests
from app.core.config import settings

def get_pr_files(repo_url: str, pr_number: int, github_token: str = None):
    if not github_token:
        github_token = settings.GITHUB_TOKEN
    
    api_url = f"{repo_url.replace('github.com', 'api.github.com/repos')}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {github_token}"
    }
    print(f"GitHub Token: {github_token}")
    print(f"API URL: {api_url}")

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        files = []

        for file in response.json():
            try:
                file_content = requests.get(file.get("raw_url", ""), headers=headers)
                file_content.raise_for_status()
                files.append({"name": file["filename"], "content": file_content.text})
            except requests.RequestException as e:
                print(f"Failed to fetch raw file content for {file.get('filename', 'Unknown')}: {e}")
        return files

    except requests.RequestException as e:
        print(f"Error fetching PR files: {e}")
        raise
