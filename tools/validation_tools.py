import re

def validate_pr_title(title: str):
    """
    Validates PR title follows conventional commit style.
    """
    pattern = r"^(feat|fix|refactor|chore|docs|test): .+"
    return bool(re.match(pattern, title))