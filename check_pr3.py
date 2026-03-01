import os
import json
from tools.github_tools import get_pr_details, get_pr_files

# Load token from .env
with open('.env') as f:
    token = f.read().split('GITHUB_TOKEN=')[1].split('\n')[0].strip()
os.environ['GITHUB_TOKEN'] = token

# Get PR #3 details
pr = get_pr_details('acp-amit0807/MovieApi', 3)
print("=== PR #3 Details ===")
print(f"Title: {pr.get('title')}")
print(f"State: {pr.get('state')}")
print(f"Additions: {pr.get('additions')}")
print(f"Deletions: {pr.get('deletions')}")
print(f"Changed files: {pr.get('changed_files')}")

# Get files changed
files = get_pr_files('acp-amit0807/MovieApi', 3)
print("\n=== Files Changed ===")
for f in files:
    print(f"  {f['filename']} ({f['status']}, +{f.get('additions', 0)}/-{f.get('deletions', 0)} lines)")
