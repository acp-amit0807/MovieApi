#!/usr/bin/env python3
import os
import requests

os.environ['GITHUB_TOKEN'] = open('.env').read().split('GITHUB_TOKEN=')[1].split('\n')[0].strip()
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

pr_number = 1
repo = 'acp-amit0807/MovieApi'

# Get all comments on the PR
url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comments = requests.get(url, headers=headers).json()

print(f"Found {len(comments)} comments on PR #{pr_number}\n")

# Display comments with their IDs and preview
for i, comment in enumerate(comments):
    preview = comment['body'][:80].replace('\n', ' ')
    print(f"{i+1}. Comment ID: {comment['id']}")
    print(f"   Author: {comment['user']['login']}")
    print(f"   Preview: {preview}...")
    print()

# Keep only the last comment (most recent = comprehensive description)
# Delete all others
if len(comments) > 1:
    print(f"\n⏳ Deleting {len(comments)-1} older comments...\n")
    for comment in comments[:-1]:
        delete_url = f"https://api.github.com/repos/{repo}/issues/comments/{comment['id']}"
        response = requests.delete(delete_url, headers=headers)
        
        if response.status_code == 204:
            preview = comment['body'][:50].replace('\n', ' ')
            print(f"✅ Deleted: {preview}...")
        else:
            print(f"❌ Failed to delete comment {comment['id']}: {response.status_code}")
    
    print(f"\n✅ Cleanup complete! Kept only the latest comprehensive description.")
else:
    print("✅ PR already has only 1 comment (nothing to delete)")
