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

# Get list of files changed in the PR
url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
files = requests.get(url, headers=headers).json()

print("Files in PR diff:")
for file in files:
    print(f"  - {file['filename']}")

# Get PR commit SHA
url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
pr = requests.get(url, headers=headers).json()
commit_sha = pr['head']['sha']

print(f"\nCommit SHA: {commit_sha}\n")

# File-specific review comments 
reviews = [
    {
        "path": "Controllers/MoviesController.cs",
        "line": 20,
        "comment": """⚠️ **Missing Error Handling & Validation**

This endpoint lacks input validation and exception handling.

**Issues:**
- No ModelState validation for invalid query parameters
- No try-catch for potential service failures
- Malformed requests could cause unhandled exceptions

**Suggested Fix:**
```csharp
if (!ModelState.IsValid)
    return BadRequest(ModelState);

try
{
    var movies = _movieService.GetMovies(filter);
    return Ok(movies);
}
catch (Exception ex)
{
    return StatusCode(500, "An unexpected error occurred");
}
```"""
    },
    {
        "path": "Services/MovieService.cs",
        "line": 13,
        "comment": """⚠️ **Hard-Coded Data + Missing Abstraction**

Seed data is mixed with business logic. This violates separation of concerns.

**Risks:**
- Cannot easily swap implementations (database vs in-memory)
- Difficult to test and mock
- Violates Dependency Inversion Principle

**Suggestion:** Extract `IMovieService` interface and `IMovieRepository` to handle data loading separately."""
    },
    {
        "path": "Models/MovieFilter.cs",
        "line": 5,
        "comment": """💡 **Add Data Validation Attributes**

Without validation annotations, invalid data can reach the service.

**Suggested Enhancement:**
```csharp
[Range(1900, 2100, ErrorMessage = "Year must be between 1900 and 2100")]
public int? Year { get; set; }

[StringLength(50, ErrorMessage = "Genre cannot exceed 50 characters")]
public string? Genre { get; set; }
```"""
    }
]

# Post review comments
for review in reviews:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    
    payload = {
        "body": review["comment"],
        "commit_id": commit_sha,
        "path": review["path"],
        "line": review["line"]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        print(f"✅ Comment posted on {review['path']}:{review['line']}")
    else:
        error = response.json() if response.text else {}
        print(f"❌ {review['path']}:{review['line']} - {error.get('message', 'Unknown error')}")

print("\n✅ Inline review comments complete!")
