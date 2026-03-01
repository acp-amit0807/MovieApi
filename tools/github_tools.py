import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_pr_details(repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    return requests.get(url, headers=_headers()).json()

def get_pr_files(repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    return requests.get(url, headers=_headers()).json()

def post_pr_comment(repo: str, pr_number: int, comment: str):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    requests.post(url, headers=_headers(), json={"body": comment})