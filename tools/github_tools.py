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


def create_pull_request(repo: str, head_branch: str, base_branch: str = "main", title: str = None, body: str = None):
    """
    Creates a Pull Request.

    :param repo: e.g. "acp-amit0807/CalculatorApi"
    :param head_branch: branch to merge FROM (e.g. "auto/test-feature")
    :param base_branch: branch to merge INTO (default: main)
    :param title: PR title
    :param body: PR description
    """

    url = f"https://api.github.com/repos/{repo}/pulls"

    payload = {
        "title": title or f"Automated PR from {head_branch}",
        "head": head_branch,
        "base": base_branch,
        "body": body or "This PR was created automatically by MCP."
    }

    response = requests.post(url, headers=_headers(), json=payload)

    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to create PR: {response.text}")

    return response.json()

