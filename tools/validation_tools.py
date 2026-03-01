"""
Comprehensive PR validation tools with detailed metrics.
"""
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool
    score: float
    message: str
    violations: List[str]
    suggestions: List[str]


def validate_pr_title(title: str) -> ValidationResult:
    """
    Validates PR title follows conventional commit style.
    
    Conventional Commits Format:
    <type>(<optional scope>): <description>
    
    Where type is one of: feat, fix, refactor, chore, docs, test, perf, ci, build
    
    Args:
        title: PR title string
        
    Returns:
        ValidationResult with validation details
    """
    violations = []
    suggestions = []
    
    pattern = r"^(feat|fix|refactor|chore|docs|test|perf|ci|build)(\(.+\))?: .+"
    is_valid = bool(re.match(pattern, title))
    
    if not is_valid:
        violations.append(f"Title '{title}' does not follow conventional commit format")
        suggestions.append("Use format: feat(scope): description")
        suggestions.append("Valid types: feat, fix, refactor, chore, docs, test, perf, ci, build")
    
    # Additional checks
    if len(title) < 10:
        violations.append("Title is too short (minimum 10 characters)")
        suggestions.append("Provide more descriptive title")
    
    if len(title) > 72:
        violations.append("Title exceeds 72 characters (Git best practice)")
        suggestions.append(f"Current length: {len(title)} characters. Keep titles concise.")
    
    if not title[0].isupper() and title[0].isalpha():
        violations.append("Title should start with uppercase letter after type prefix")
    
    # Calculate score
    score = 10 if is_valid else 0
    if len(title) >= 10 and len(title) <= 72:
        score = max(score - 2, 5) if not is_valid else 10
    
    return ValidationResult(
        is_valid=is_valid,
        score=score,
        message=f"PR title validation: {'✅ PASS' if is_valid else '❌ FAIL'}",
        violations=violations,
        suggestions=suggestions
    )


def validate_pr_description(description: str) -> ValidationResult:
    """
    Validates PR description completeness and quality.
    
    Args:
        description: PR description body text
        
    Returns:
        ValidationResult with validation details
    """
    violations = []
    suggestions = []
    score = 10
    
    if not description or len(description.strip()) < 20:
        violations.append("PR description is empty or too short")
        suggestions.append("Provide comprehensive description of changes")
        score -= 5
    
    required_sections = {
        "what": r"(?i)(what|changes?|implemented?|modified|added)",
        "why": r"(?i)(why|reason|rationale|because|motivation)",
        "testing": r"(?i)(test|validation|how to test|testing instructions)"
    }
    
    missing_sections = []
    for section, pattern in required_sections.items():
        if not re.search(pattern, description):
            missing_sections.append(section)
            score -= 2
    
    if missing_sections:
        violations.append(f"Missing sections: {', '.join(missing_sections.upper())}")
        suggestions.append("Include 'What', 'Why', and 'Testing' sections in description")
    
    # Check for breaking changes notation
    if "breaking" not in description.lower() and "//!" not in description and "BREAKING" not in description:
        if any(keyword in description.lower() for keyword in ["major change", "api change", "db migration"]):
            violations.append("Potential breaking change not documented")
            suggestions.append("Add '# BREAKING CHANGE:' section if applicable")
            score -= 1
    
    return ValidationResult(
        is_valid=len(violations) == 0,
        score=max(score, 2),
        message=f"PR description validation: {'✅ PASS' if len(violations) == 0 else '⚠️ NEEDS IMPROVEMENT'}",
        violations=violations,
        suggestions=suggestions
    )


def validate_csharp_file_structure(filename: str, content: str) -> ValidationResult:
    """
    Validates C# file structure and conventions.
    
    Args:
        filename: C# filename
        content: File content
        
    Returns:
        ValidationResult with validation details
    """
    violations = []
    suggestions = []
    score = 10
    
    # Check filename matches class name (for single-class files)
    classes = re.findall(r'public class (\w+)', content)
    if len(classes) == 1:
        expected_filename = f"{classes[0]}.cs"
        if not filename.endswith(expected_filename):
            violations.append(f"Filename should be '{expected_filename}'")
            suggestions.append("Follow C# naming convention: filename matches public class name")
            score -= 3
    
    # Check for using statements
    if not content.startswith("using ") and "using " not in content[:200]:
        violations.append("Missing using statements at top of file")
        suggestions.append("Add necessary using statements and organize them")
        score -= 2
    
    # Check for namespace
    if "namespace " not in content:
        violations.append("File missing namespace declaration")
        suggestions.append("All C# classes should be in a namespace")
        score -= 3
    
    # Check for excessive lines
    line_count = len(content.split('\n'))
    if line_count > 500:
        violations.append(f"File exceeds recommended size ({line_count} lines)")
        suggestions.append("Consider splitting into multiple focused classes")
        score -= 2
    
    # Check for TODO comments
    todos = re.findall(r'//\s*TODO', content, re.IGNORECASE)
    if todos:
        violations.append(f"Found {len(todos)} TODO comments in code")
        suggestions.append("Resolve or create GitHub issues for TODO items before merging")
        score -= 1
    
    return ValidationResult(
        is_valid=len(violations) == 0,
        score=max(score, 2),
        message=f"File structure validation: {'✅ PASS' if len(violations) == 0 else '⚠️ NEEDS IMPROVEMENT'}",
        violations=violations,
        suggestions=suggestions
    )


def validate_test_structure(test_filename: str, content: str) -> ValidationResult:
    """
    Validates test file structure and conventions.
    
    Args:
        test_filename: Test class filename
        content: Test file content
        
    Returns:
        ValidationResult with validation details
    """
    violations = []
    suggestions = []
    score = 10
    
    # Check for xUnit attributes
    has_xunit = "[Fact]" in content or "[Theory]" in content
    if not has_xunit:
        violations.append("No xUnit test attributes ([Fact] or [Theory]) found")
        suggestions.append("Use xUnit for test discovery: [Fact] for single case, [Theory] for parameterized")
        score -= 3
    
    # Check for test methods
    arrange_act_assert = content.count("//Act") + content.count("// Act") + content.count("//Act") >= 1
    test_method_count = len(re.findall(r'public\s+void\s+\w+Test', content, re.IGNORECASE))
    
    if test_method_count == 0:
        violations.append("No test methods found in test class")
        suggestions.append("Test methods should be public and follow naming: [MethodName]_[Condition]_[ExpectedResult]")
        score -= 5
    
    # Check for AAA pattern (Arrange, Act, Assert)
    if not arrange_act_assert and test_method_count > 0:
        violations.append("Tests don't follow Arrange-Act-Assert pattern")
        suggestions.append("Structure tests: // Arrange, // Act, // Assert sections")
        score -= 2
    
    # Check for assertions
    has_assertions = "Assert." in content or "Should()" in content
    if not has_assertions:
        violations.append("No assertions found in test file")
        suggestions.append("Add assertions: Assert.True(), Assert.Equal(), or FluentAssertions Should()")
        score -= 3
    
    return ValidationResult(
        is_valid=len(violations) == 0,
        score=max(score, 2),
        message=f"Test structure validation: {'✅ PASS' if len(violations) == 0 else '⚠️ NEEDS IMPROVEMENT'}",
        violations=violations,
        suggestions=suggestions
    )


def validate_all_pr_aspects(
    title: str,
    description: str,
    files: List[Dict[str, Any]]
) -> Dict[str, ValidationResult]:
    """
    Comprehensive PR validation across all aspects.
    
    Args:
        title: PR title
        description: PR description
        files: List of file objects from GitHub API
        
    Returns:
        Dictionary of all validation results
    """
    results = {
        "title": validate_pr_title(title),
        "description": validate_pr_description(description)
    }
    
    # Validate individual files
    results["files"] = {}
    for file in files:
        filename = file.get("filename", "")
        content = file.get("patch", "")
        
        if filename.endswith(".cs"):
            if "Test" in filename or "Tests" in filename:
                results["files"][filename] = validate_test_structure(filename, content)
            else:
                results["files"][filename] = validate_csharp_file_structure(filename, content)
    
    return results