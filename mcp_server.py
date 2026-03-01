from mcp.server.fastmcp import FastMCP
from tools.github_tools import (
    get_pr_details,
    get_pr_files,
    post_pr_comment
)
from tools.review_tools import (
    extract_csharp_changes,
    check_unit_tests,
    detect_hardcoded_values
)
from tools.validation_tools import validate_pr_title
from tools.scoring_tools import score_pr_structured

mcp = FastMCP("enterprise-pr-reviewer")


@mcp.tool()
def analyze_pr(repo: str, pr_number: int):
    """
    Full structured PR analysis.
    """

    pr = get_pr_details(repo, pr_number)
    files = get_pr_files(repo, pr_number)

    title = pr.get("title", "")
    title_valid = validate_pr_title(title)

    code = extract_csharp_changes(files)
    has_tests = check_unit_tests(files)
    hardcoded_issues = detect_hardcoded_values(code)

    scoring = score_pr_structured(
        title_valid=title_valid,
        has_tests=has_tests,
        hardcoded_issues=hardcoded_issues
    )

    return {
        "title_valid": title_valid,
        "has_tests": has_tests,
        "hardcoded_issues": hardcoded_issues,
        "score": scoring["score"],
        "recommendation": scoring["recommendation"],
        "scoring_reasons": scoring["reasons"],
        "code_patch": code
    }


@mcp.tool()
def publish_review(repo: str, pr_number: int, review: str):
    post_pr_comment(repo, pr_number, review)
    return "Review published successfully."


if __name__ == "__main__":
    mcp.run()