#!/usr/bin/env python3
import os
import requests

# load token
os.environ['GITHUB_TOKEN'] = open('.env').read().split('GITHUB_TOKEN=')[1].split('\n')[0].strip()
token = os.environ['GITHUB_TOKEN']

repo = 'acp-amit0807/MovieApi'
pr_number = 2

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json'
}

new_body = '''## 📋 Updated PR Description

This PR enhances repository documentation and tooling.

### 🎯 Purpose
Add detailed architecture overview, README content, and Python automation scripts.

### 📦 Changes
- Updated `README.md` with architecture diagram and component breakdown.
- Added `cleanup_pr_comments.py`, `post_review.py`, `post_inline_reviews.py`.
- Modified senior architect prompt to include workflow enhancements.
- Ensured all scripts reside in repository and necessary README updates.

### 🔍 Scope & Metrics
- Files changed: 15
- Mainly documentation and tooling, no product code modifications.

### 👤 Reviewer
@{reviewer}

### ✅ Next Steps
- Move scripts to `tools/` or `scripts/` folder.
- Add error handling and unit tests for Python tools.

### ⚠️ Notes
This PR only affects docs and tooling; no runtime impact.
'''.replace('{reviewer}', open('.env').read().split('DEFAULT_REVIEWER=')[1].strip())

patch_url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}'
response = requests.patch(patch_url, headers=headers, json={'body': new_body})
if response.status_code == 200:
    print('✅ PR body updated successfully')
else:
    print('❌ Failed to update PR body', response.status_code, response.text)
