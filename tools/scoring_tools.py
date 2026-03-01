def score_pr_structured(title_valid: bool,
                        has_tests: bool,
                        hardcoded_issues: list):
    """
    Simple governance scoring system.
    """

    score = 10
    reasons = []

    if not title_valid:
        score -= 2
        reasons.append("PR title does not follow conventional format.")

    if not has_tests:
        score -= 3
        reasons.append("No unit tests detected.")

    if hardcoded_issues:
        score -= 2
        reasons.append("Hardcoded values detected.")

    if score < 0:
        score = 0

    recommendation = "Approve" if score >= 7 else "Changes Required"

    return {
        "score": score,
        "reasons": reasons,
        "recommendation": recommendation
    }