"""
Comprehensive PR scoring and quality assessment tools.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class RecommendationType(Enum):
    """PR merge recommendation types."""
    APPROVE = "APPROVE"
    APPROVE_WITH_MINOR_CHANGES = "APPROVE_WITH_MINOR_CHANGES"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    CHANGES_REQUIRED = "CHANGES_REQUIRED"


@dataclass
class ScoreMetric:
    """Individual scoring metric."""
    name: str
    weight: float
    score: float
    max_score: float
    reason: str


@dataclass
class PrScore:
    """Complete PR scoring result."""
    overall_score: float
    max_score: float
    recommendation: RecommendationType
    metrics: List[ScoreMetric]
    blockers: List[str]
    improvements: List[str]
    nice_to_haves: List[str]


def score_pr_structured(
    title_valid: bool,
    has_tests: bool,
    hardcoded_issues: int,
    critical_issues: int = 0,
    high_issues: int = 0,
    medium_issues: int = 0,
    architecture_score: float = 8.0,
    code_quality_score: float = 7.0,
    security_score: float = 7.0,
    documentation_quality: bool = True,
    pr_size_lines: int = 100
) -> PrScore:
    """
    Comprehensive PR governance scoring system with weighted metrics.
    
    Args:
        title_valid: PR title follows conventional format
        has_tests: Test files present in PR
        hardcoded_issues: Count of hardcoded values found
        critical_issues: Count of critical severity issues
        high_issues: Count of high severity issues
        medium_issues: Count of medium severity issues
        architecture_score: Architecture assessment (0-10)
        code_quality_score: Code quality assessment (0-10)
        security_score: Security assessment (0-10)
        documentation_quality: PR description is comprehensive
        pr_size_lines: Number of lines added
        
    Returns:
        PrScore object with detailed metrics
    """
    
    metrics = []
    blockers = []
    improvements = []
    nice_to_haves = []
    
    # 1. PR Title Validation (5% weight)
    title_score = 10 if title_valid else 0
    metrics.append(ScoreMetric(
        name="PR Title Format",
        weight=0.05,
        score=title_score,
        max_score=10,
        reason="Follows conventional commit format (feat/fix/refactor/etc)" if title_valid else "Does not follow conventional commit format"
    ))
    if not title_valid:
        blockers.append("❌ PR title must follow conventional commit format (feat/fix/refactor/docs/test/chore)")
    
    # 2. Testing Coverage (15% weight)
    test_score = 10 if has_tests else 2
    metrics.append(ScoreMetric(
        name="Test Coverage",
        weight=0.15,
        score=test_score,
        max_score=10,
        reason="Unit tests present" if has_tests else "No test files detected in PR"
    ))
    if not has_tests:
        blockers.append("❌ CRITICAL: No unit tests detected. All code changes must have corresponding tests.")
    
    # 3. Code Quality (20% weight)
    quality_score = code_quality_score
    metrics.append(ScoreMetric(
        name="Code Quality",
        weight=0.20,
        score=quality_score,
        max_score=10,
        reason=f"Code quality assessed at {quality_score}/10"
    ))
    
    # 4. Architecture & Design (20% weight)
    arch_score = architecture_score
    metrics.append(ScoreMetric(
        name="Architecture & Design",
        weight=0.20,
        score=arch_score,
        max_score=10,
        reason=f"Architecture assessment: {arch_score}/10 - SOLID principles compliance"
    ))
    
    # 5. Security (20% weight)
    security_penalty = min(critical_issues * 3 + hardcoded_issues * 2, 10)
    sec_score = max(0, security_score - security_penalty)
    metrics.append(ScoreMetric(
        name="Security",
        weight=0.20,
        score=sec_score,
        max_score=10,
        reason=f"Security: {sec_score}/10 - {critical_issues} critical issues found"
    ))
    if critical_issues > 0:
        blockers.append(f"❌ BLOCKER: {critical_issues} critical security issue(s) detected")
    
    # 6. Documentation (10% weight)
    doc_score = 10 if documentation_quality else 3
    metrics.append(ScoreMetric(
        name="Documentation",
        weight=0.10,
        score=doc_score,
        max_score=10,
        reason="PR description is comprehensive" if documentation_quality else "PR description needs more detail"
    ))
    if not documentation_quality:
        improvements.append("Add more comprehensive PR description with rationale and testing instructions")
    
    # 7. Issue Severity Summary
    issue_penalty = (
        critical_issues * 3 +  # Each critical = -3 points
        high_issues * 2 +      # Each high = -2 points
        medium_issues * 1      # Each medium = -1 point
    )
    
    if critical_issues > 0:
        blockers.append(f"❌ {critical_issues} critical issue(s) must be resolved")
    
    if high_issues > 0:
        improvements.append(f"⚠️ {high_issues} high severity issue(s) should be addressed")
    
    if medium_issues > 0:
        improvements.append(f"💡 {medium_issues} medium severity issue(s) for improvement")
    
    # 8. PR Size Assessment
    if pr_size_lines > 500:
        improvements.append(f"⚠️ Large PR ({pr_size_lines} lines): Consider splitting into smaller, focused PRs")
    
    # Calculate weighted score
    weighted_score = sum(m.score * m.weight for m in metrics)
    max_possible_score = sum(m.max_score * m.weight for m in metrics) if metrics else 10
    
    # Normalize to 0-10 scale
    overall_score = (weighted_score / max_possible_score) * 10 if max_possible_score > 0 else 0
    
    # Determine recommendation based on blockers and score
    if critical_issues > 0 or not has_tests or not title_valid:
        recommendation = RecommendationType.CHANGES_REQUIRED
    elif high_issues > 0 or overall_score < 6:
        recommendation = RecommendationType.REVIEW_REQUIRED
    elif len(improvements) > 0 or overall_score < 8:
        recommendation = RecommendationType.APPROVE_WITH_MINOR_CHANGES
    else:
        recommendation = RecommendationType.APPROVE
    
    # Add nice-to-haves
    if recommendation != RecommendationType.APPROVE:
        nice_to_haves.append("Consider adding integration tests")
        nice_to_haves.append("Add architectural diagrams in PR description")
        nice_to_haves.append("Include performance test results for large changes")
    
    return PrScore(
        overall_score=round(overall_score, 1),
        max_score=10,
        recommendation=recommendation,
        metrics=metrics,
        blockers=blockers,
        improvements=improvements,
        nice_to_haves=nice_to_haves
    )


def format_score_report(pr_score: PrScore) -> str:
    """
    Generate human-readable PR scoring report.
    
    Args:
        pr_score: PrScore object from scoring function
        
    Returns:
        Formatted report string
    """
    report = f"""
╔════════════════════════════════════════════════════════════════╗
║               📊 PR QUALITY ASSESSMENT REPORT                   ║
╚════════════════════════════════════════════════════════════════╝

🎯 OVERALL SCORE: {pr_score.overall_score}/{pr_score.max_score}
📋 RECOMMENDATION: {pr_score.recommendation.value}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 METRIC BREAKDOWN:
"""
    
    for metric in pr_score.metrics:
        pct = (metric.score / metric.max_score * 100) if metric.max_score > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        report += f"\n  {metric.name}: {metric.score}/{metric.max_score} [{bar}] {pct:.0f}%"
        report += f"\n    └─ {metric.reason}\n"
    
    if pr_score.blockers:
        report += f"\n❌ BLOCKERS ({len(pr_score.blockers)}):\n"
        for blocker in pr_score.blockers:
            report += f"   {blocker}\n"
    
    if pr_score.improvements:
        report += f"\n⚠️ IMPROVEMENTS ({len(pr_score.improvements)}):\n"
        for improvement in pr_score.improvements:
            report += f"   {improvement}\n"
    
    if pr_score.nice_to_haves:
        report += f"\n💡 NICE-TO-HAVES ({len(pr_score.nice_to_haves)}):\n"
        for nice in pr_score.nice_to_haves:
            report += f"   {nice}\n"
    
    report += "\n" + "━" * 66 + "\n"
    
    return report