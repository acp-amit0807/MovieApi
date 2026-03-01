import requests
import os
from typing import Any, Dict, List


def _headers() -> Dict[str, str]:
	"""Return request headers using the current `GITHUB_TOKEN` from the environment.

	Reading the token at call-time avoids issues when callers set the env var
	after importing this module.
	"""
	token = os.getenv("GITHUB_TOKEN")
	if not token:
		raise RuntimeError("GITHUB_TOKEN environment variable is not set")
	return {
		"Authorization": f"token {token}",
		"Accept": "application/vnd.github.v3+json"
	}


def _handle_response(response: requests.Response) -> Any:
	try:
		payload = response.json()
	except ValueError:
		payload = response.text
	if not response.ok:
		if response.status_code == 401:
			raise Exception(
				"GitHub API error (401): Unauthorized.\n"
				"Possible causes: GITHUB_TOKEN is missing/invalid, expired, revoked, or lacks required scopes (repo).\n"
				"Ensure the token is set in environment or .env and has 'repo' scope for private repos."
			)
		raise Exception(f"GitHub API error ({response.status_code}): {payload}")
	return payload


def get_pr_details(repo: str, pr_number: int) -> Dict[str, Any]:
	url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
	resp = requests.get(url, headers=_headers())
	return _handle_response(resp)


def get_pr_files(repo: str, pr_number: int) -> List[Dict[str, Any]]:
	url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
	resp = requests.get(url, headers=_headers())
	return _handle_response(resp)


def post_pr_comment(repo: str, pr_number: int, comment: str) -> Dict[str, Any]:
	url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
	resp = requests.post(url, headers=_headers(), json={"body": comment})
	return _handle_response(resp)


def find_pull_requests_by_head(repo: str, owner: str, head: str) -> List[Dict[str, Any]]:
	"""Return list of PRs matching `owner:head` (open PRs by head branch).
	"""
	url = f"https://api.github.com/repos/{repo}/pulls?head={owner}:{head}"
	resp = requests.get(url, headers=_headers())
	return _handle_response(resp)


def create_pull_request(repo: str, head_branch: str, base_branch: str = "main", title: str = None, body: str = None) -> Dict[str, Any]:
	url = f"https://api.github.com/repos/{repo}/pulls"
	payload = {
		"title": title or f"Automated PR from {head_branch}",
		"head": head_branch,
		"base": base_branch,
		"body": body or "This PR was created automatically by tooling."
	}
	resp = requests.post(url, headers=_headers(), json=payload)
	return _handle_response(resp)

import os

