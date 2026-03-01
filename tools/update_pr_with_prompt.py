#!/usr/bin/env python3
"""Append `prompts/senior_architect_prompt.txt` to an existing PR's body and post a comment.

Usage: run from repo root. Requires `GITHUB_TOKEN` in environment or in `.env`.
"""
import os
import sys
import requests

# Ensure project root is on sys.path when this script is executed from tools/
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

# Load token from .env if present
if os.path.exists('.env'):
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('GITHUB_TOKEN='):
                os.environ.setdefault('GITHUB_TOKEN', line.split('GITHUB_TOKEN=')[1].strip())
                break

if not os.getenv('GITHUB_TOKEN'):
    print('ERROR: GITHUB_TOKEN not found in environment or .env', file=sys.stderr)
    sys.exit(1)

from tools import github_tools

PROMPT_REL = os.environ.get('PROMPT_PATH', os.path.join('prompts', 'senior_architect_prompt.txt'))

# Require PR repository and head branch to be provided via env or CLI args (no hardcoding)
import argparse

parser = argparse.ArgumentParser(description='Append a prompt to an existing PR body and post a comment')
parser.add_argument('--repo', help='Repository in owner/name format (or set PR_REPO env var)')
parser.add_argument('--head', help='Head branch name (or set PR_HEAD env var)')
parser.add_argument('--prompt', help='Path to prompt file (or set PROMPT_PATH env var)')
args = parser.parse_args()

REPO = args.repo or os.environ.get('PR_REPO')
HEAD = args.head or os.environ.get('PR_HEAD')
if args.prompt:
    PROMPT_REL = args.prompt

if not REPO or not HEAD:
    print('ERROR: PR repository (PR_REPO or --repo) and head branch (PR_HEAD or --head) must be provided', file=sys.stderr)
    sys.exit(1)

owner = REPO.split('/')[0]

# Find existing PRs for the head
try:
    prs = github_tools.find_pull_requests_by_head(REPO, owner, HEAD)
except Exception as e:
    print('ERROR querying pull requests:', e, file=sys.stderr)
    sys.exit(1)

if not prs:
    print(f'No open pull requests found for head {HEAD} in {REPO}', file=sys.stderr)
    sys.exit(1)

pr = prs[0]
pr_number = pr.get('number')
pr_url = pr.get('html_url')
print(f'Found PR #{pr_number}: {pr_url}')

# Fetch current PR details
try:
    pr_details = github_tools.get_pr_details(REPO, pr_number)
except Exception as e:
    print('ERROR fetching PR details:', e, file=sys.stderr)
    sys.exit(1)

current_body = pr_details.get('body') or ''

# Read prompt
prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), PROMPT_REL)
if not os.path.exists(prompt_path):
    print('ERROR: prompt file not found at', prompt_path, file=sys.stderr)
    sys.exit(1)
with open(prompt_path, 'r', encoding='utf-8') as f:
    prompt_text = f.read()

marker = '\n\n---\n\n**Senior Architect Prompt (for review automation):**\n\n'

if prompt_text.strip() in current_body:
    print('Prompt already present in PR body — no update needed.')
    sys.exit(0)

new_body = current_body + marker + prompt_text

# Patch PR body
patch_url = f'https://api.github.com/repos/{REPO}/pulls/{pr_number}'
try:
    resp = requests.patch(patch_url, headers=github_tools._headers(), json={'body': new_body})
    resp.raise_for_status()
    print('PR body updated successfully.')
except Exception as e:
    print('ERROR updating PR body:', e, file=sys.stderr)
    sys.exit(1)

# Post comment indicating the update
try:
    comment = 'Appending the `senior_architect_prompt.txt` to the PR body to be used for automated review guidance.'
    github_tools.post_pr_comment(REPO, pr_number, comment)
    print('Posted a comment to the PR.')
except Exception as e:
    print('WARNING: Failed to post comment:', e, file=sys.stderr)

print('Done.')
