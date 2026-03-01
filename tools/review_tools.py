"""
Comprehensive PR review analysis tools.
"""
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum

class SeverityLevel(Enum):
    """Severity levels for issues found."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class ReviewIssue:
    """Data model for a single review issue."""
    file: str
    line_number: Optional[int]
    severity: SeverityLevel
    category: str
    description: str
    suggestion: str
    code_snippet: Optional[str] = None


@dataclass
class ReviewResult:
    """Complete review analysis result."""
    issues: List[ReviewIssue]
    summary: Dict[str, Any]
    has_tests: bool
    test_coverage_estimated: float


def extract_csharp_changes(files: List[Dict]) -> Dict[str, str]:
    """
    Extract C# code changes with file organization.
    
    Args:
        files: List of file objects from GitHub API
        
    Returns:
        Dictionary mapping filename to patch content
    """
    changes = {}
    for f in files:
        if f["filename"].endswith(".cs"):
            changes[f["filename"]] = f.get("patch", "")
    return changes


def check_unit_tests(files: List[Dict]) -> Dict[str, Any]:
    """
    Analyze test presence and structure.
    
    Args:
        files: List of file objects from GitHub API
        
    Returns:
        Dictionary with test analysis metrics
    """
    test_files = []
    test_patterns = [
        "*.Tests.cs",
        "*Test.cs",
        "*Tests/*",
        "test-*.cs"
    ]
    
    for f in files:
        filename = f["filename"].lower()
        if any(pattern.lower().replace("*", "") in filename for pattern in test_patterns):
            test_files.append({
                "file": f["filename"],
                "status": f.get("status", "unknown"),
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0)
            })
    
    return {
        "has_tests": len(test_files) > 0,
        "test_files": test_files,
        "test_file_count": len(test_files),
        "estimated_coverage": (len(test_files) / max(len(files), 1)) * 100
    }


def detect_hardcoded_values(code: str, filename: str = "") -> List[ReviewIssue]:
    """
    Detect hardcoded values (URLs, connection strings, magic numbers, credentials).
    
    Args:
        code: Source code to analyze
        filename: File being analyzed
        
    Returns:
        List of ReviewIssue objects for found violations
    """
    issues = []
    lines = code.split('\n')
    
    # Hardcoded credentials (simple patterns)
    credential_patterns = [
        (r'password\s*=\s*["\']([^"\']+)["\']', "Hardcoded password detected", SeverityLevel.CRITICAL),
        (r'apikey\s*=\s*["\']([^"\']+)["\']', "Hardcoded API key detected", SeverityLevel.CRITICAL),
        (r'token\s*=\s*["\']([^"\']+)["\']', "Hardcoded token detected", SeverityLevel.CRITICAL),
        (r'secret\s*=\s*["\']([^"\']+)["\']', "Hardcoded secret detected", SeverityLevel.CRITICAL),
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern, description, severity in credential_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(ReviewIssue(
                    file=filename,
                    line_number=i,
                    severity=severity,
                    category="Security",
                    description=description,
                    suggestion="Use environment variables, secrets management (Azure KeyVault, AWS Secrets Manager)",
                    code_snippet=line.strip()
                ))
    
    # Hardcoded URLs
    url_pattern = r'(https?://[^\s"\'<>]+)'
    for i, line in enumerate(lines, 1):
        if re.search(url_pattern, line) and "http" in line:
            issues.append(ReviewIssue(
                file=filename,
                line_number=i,
                severity=SeverityLevel.MEDIUM,
                category="Configuration",
                description="Hardcoded URL detected",
                suggestion="Extract to configuration (appsettings.json, environment variable)",
                code_snippet=line.strip()
            ))
    
    # Magic numbers (but exclude comment lines)
    for i, line in enumerate(lines, 1):
        if not line.strip().startswith("//") and not line.strip().startswith("*"):
            if re.search(r'\b\d{2,}(?:\.\d+)?\b', line) and "version" not in line.lower():
                # Heuristic: numbers >= 10 or decimals
                issues.append(ReviewIssue(
                    file=filename,
                    line_number=i,
                    severity=SeverityLevel.LOW,
                    category="Code Quality",
                    description="Possible magic number detected",
                    suggestion="Extract to named constant: const int MaxRetries = 3;",
                    code_snippet=line.strip()
                ))
    
    return issues


def check_error_handling(code: str, filename: str = "") -> List[ReviewIssue]:
    """
    Detect missing or poor error handling patterns.
    
    Args:
        code: Source code to analyze
        filename: File being analyzed
        
    Returns:
        List of ReviewIssue objects for error handling gaps
    """
    issues = []
    lines = code.split('\n')
    
    # Check for try-catch blocks
    has_try_catch = "try" in code and "catch" in code
    
    # Check for unsafe operations without validation
    unsafe_patterns = [
        (r'\.First\(\)', "Unsafe First() without check", SeverityLevel.HIGH),
        (r'\.FirstOrDefault\(\)', "FirstOrDefault() used but may be null", SeverityLevel.MEDIUM),
        (r'[\w\.]+\[[\w\s\+\-\*\/]+\]', "Direct array/list access without bounds check", SeverityLevel.MEDIUM),
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern, description, severity in unsafe_patterns:
            if re.search(pattern, line):
                issues.append(ReviewIssue(
                    file=filename,
                    line_number=i,
                    severity=severity,
                    category="Error Handling",
                    description=description,
                    suggestion="Add null/bounds validation before access",
                    code_snippet=line.strip()
                ))
    
    # Check for swallowed exceptions
    swallow_pattern = r'catch\s*\([^)]*\)\s*\{\s*\}'
    for i, line in enumerate(lines, 1):
        if re.search(swallow_pattern, line):
            issues.append(ReviewIssue(
                file=filename,
                line_number=i,
                severity=SeverityLevel.HIGH,
                category="Error Handling",
                description="Empty catch block - exception swallowed",
                suggestion="Add logging: logger.Error('Operation failed', ex); and/or add rethrow statement",
                code_snippet=line.strip()
            ))
    
    return issues


def check_architecture_issues(code: str, filename: str = "") -> List[ReviewIssue]:
    """
    Detect architectural and design issues.
    
    Args:
        code: Source code to analyze
        filename: File being analyzed
        
    Returns:
        List of ReviewIssue objects for architecture issues
    """
    issues = []
    
    # Check for tight coupling (new keyword for dependencies)
    if "new " in code and "DbContext" in code:
        issues.append(ReviewIssue(
            file=filename,
            line_number=None,
            severity=SeverityLevel.HIGH,
            category="Architecture",
            description="Tight coupling: DbContext instantiated directly",
            suggestion="Use Dependency Injection: inject IRepository or DbContext via constructor",
            code_snippet=None
        ))
    
    # Check for god classes (file > 500 lines)
    if code.count('\n') > 500:
        issues.append(ReviewIssue(
            file=filename,
            line_number=None,
            severity=SeverityLevel.MEDIUM,
            category="Architecture",
            description="File exceeds recommended size (500+ lines)",
            suggestion="Consider splitting into multiple focused classes (Single Responsibility Principle)",
            code_snippet=None
        ))
    
    # Check for duplicate code blocks
    if code.count("public ") > 20:
        issues.append(ReviewIssue(
            file=filename,
            line_number=None,
            severity=SeverityLevel.MEDIUM,
            category="Code Quality",
            description="File contains many public members (possible duplication)",
            suggestion="Review for duplicate functionality; extract common code to base class or utility",
            code_snippet=None
        ))
    
    return issues


def analyze_pr_files(files: List[Dict]) -> Dict[str, Any]:
    """
    Comprehensive analysis of all PR files.
    
    Args:
        files: List of file objects from GitHub API
        
    Returns:
        Dictionary with comprehensive file metrics
    """
    all_issues = []
    file_stats = {
        # total_files will reflect the number of source files considered for review (C# files)
        "total_files": 0,
        "csharp_files": 0,
        "test_files": 0,
        "total_additions": 0,
        "total_deletions": 0,
        "files_analyzed": []
    }
    
    test_analysis = check_unit_tests(files)
    file_stats["test_files"] = test_analysis["test_file_count"]
    
    for file in files:
        if file["filename"].endswith(".cs"):
            file_stats["csharp_files"] += 1
            file_stats["total_additions"] += file.get("additions", 0)
            file_stats["total_deletions"] += file.get("deletions", 0)
            
            patch = file.get("patch", "")
            
            # Analyze for issues
            hardcode_issues = detect_hardcoded_values(patch, file["filename"])
            error_issues = check_error_handling(patch, file["filename"])
            arch_issues = check_architecture_issues(patch, file["filename"])
            
            all_issues.extend(hardcode_issues + error_issues + arch_issues)
            
            file_stats["files_analyzed"].append({
                "name": file["filename"],
                "status": file.get("status"),
                "additions": file.get("additions", 0),
                "deletions": file.get("deletions", 0),
                "issues_found": len(hardcode_issues + error_issues + arch_issues)
            })
    
    # Make total_files reflect the number of C# files analyzed (ignore non-C# files)
    file_stats["total_files"] = file_stats["csharp_files"]

    # Recompute estimated coverage relative to analyzed C# files
    test_analysis["estimated_coverage"] = (
        (test_analysis.get("test_file_count", 0) / max(file_stats["csharp_files"], 1)) * 100
    )

    return {
        "stats": file_stats,
        "issues": all_issues,
        "test_analysis": test_analysis,
        "issue_count": len(all_issues),
        "severity_breakdown": {
            s.name: len([i for i in all_issues if i.severity == s])
            for s in SeverityLevel
        }
    }


def generate_review_summary(analysis: Dict[str, Any]) -> str:
    """
    Generate human-readable review summary.
    
    Args:
        analysis: Result from analyze_pr_files
        
    Returns:
        Formatted summary string
    """
    stats = analysis.get("stats", {})
    issues = analysis.get("issues", [])
    test_analysis = analysis.get("test_analysis", {})
    severity_breakdown = analysis.get("severity_breakdown", {})
    
    summary = "📋 AUTOMATED CODE REVIEW SUMMARY\n"
    summary += "=" * 60 + "\n\n"
    
    summary += f"📊 File Statistics:\n"
    summary += f"  Total Files: {stats.get('total_files', 0)}\n"
    summary += f"  C# Files: {stats.get('csharp_files', 0)}\n"
    summary += f"  Total Lines Added: {stats.get('total_additions', 0)}\n"
    summary += f"  Total Lines Deleted: {stats.get('total_deletions', 0)}\n\n"
    
    summary += f"🧪 Test Coverage:\n"
    summary += f"  Test Files Found: {test_analysis.get('test_file_count', 0)}\n"
    summary += f"  Estimated Coverage: {test_analysis.get('estimated_coverage', 0):.1f}%\n\n"
    
    summary += f"🔍 Issues Found: {len(issues)}\n"
    for severity, count in severity_breakdown.items():
        summary += f"  {severity}: {count}\n"
    
    return summary