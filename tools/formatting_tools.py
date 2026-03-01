"""
Code formatting analysis and metrics.
"""
import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class FormattingMetrics:
    """Data model for formatting analysis results."""
    line_lengths: List[int]
    average_line_length: float
    max_line_length: int
    indentation_issues: List[Dict[str, Any]]
    naming_style_violations: List[Dict[str, str]]
    whitespace_issues: List[Dict[str, Any]]
    

def analyze_line_lengths(code: str, max_length: int = 120) -> Dict[str, Any]:
    """
    Analyze line length distribution in code.
    
    Args:
        code: Source code string
        max_length: Maximum recommended line length
        
    Returns:
        Dictionary with line length metrics
    """
    lines = code.split('\n')
    line_lengths = [len(line.rstrip()) for line in lines]
    violations = [(i+1, len_, len_) for i, len_ in enumerate(line_lengths) if len_ > max_length]
    
    return {
        "total_lines": len(lines),
        "average_length": sum(line_lengths) / len(line_lengths) if line_lengths else 0,
        "max_length": max(line_lengths) if line_lengths else 0,
        "violations": violations,
        "violation_count": len(violations),
        "compliance_percentage": ((len(lines) - len(violations)) / len(lines) * 100) if lines else 0
    }


def check_indentation_consistency(code: str) -> Dict[str, Any]:
    """
    Check for consistent indentation patterns.
    
    Args:
        code: Source code string
        
    Returns:
        Dictionary with indentation analysis
    """
    lines = code.split('\n')
    indentation_patterns = {}
    issues = []
    
    for i, line in enumerate(lines, 1):
        if not line or line.isspace():
            continue
            
        # Count leading spaces
        leading_spaces = len(line) - len(line.lstrip())
        
        # Check if indentation is multiple of 4 (standard)
        if leading_spaces % 4 != 0:
            issues.append({
                "line": i,
                "spaces": leading_spaces,
                "issue": f"Indentation not multiple of 4: {leading_spaces} spaces"
            })
    
    return {
        "total_checked": len([l for l in lines if l and not l.isspace()]),
        "issues": issues,
        "issue_count": len(issues),
        "consistency_score": 100 - (len(issues) / len(lines) * 100) if lines else 0
    }


def analyze_naming_conventions(code: str, language: str = "csharp") -> Dict[str, Any]:
    """
    Check for consistent naming conventions.
    
    Args:
        code: Source code string
        language: Programming language ('csharp', 'python', 'javascript')
        
    Returns:
        Dictionary with naming convention analysis
    """
    violations = []
    
    if language.lower() == "csharp":
        # PascalCase for class names, methods
        pascal_case_pattern = r'(class|interface|struct|record)\s+([a-z_][a-zA-Z0-9_]*)'
        for match in re.finditer(pascal_case_pattern, code):
            name = match.group(2)
            if not name[0].isupper():
                violations.append({
                    "type": match.group(1),
                    "name": name,
                    "issue": f"{match.group(1)} name should be PascalCase: {name}",
                    "suggestion": name.replace('_', ' ').title().replace(' ', '')
                })
        
        # camelCase for private fields/variables
        private_field_pattern = r'private\s+\w+\s+([A-Z][a-zA-Z0-9_]*)'
        for match in re.finditer(private_field_pattern, code):
            name = match.group(1)
            violations.append({
                "type": "private field",
                "name": name,
                "issue": f"Private field should be camelCase: {name}",
                "suggestion": f"_{name[0].lower()}{name[1:]}"
            })
    
    return {
        "language": language,
        "violations": violations,
        "violation_count": len(violations),
        "quality_score": 100 - (len(violations) * 5)
    }


def detect_code_duplication(code: str, min_length: int = 3) -> Dict[str, Any]:
    """
    Detect duplicate code lines/blocks.
    
    Args:
        code: Source code string
        min_length: Minimum line count to consider as duplicate
        
    Returns:
        Dictionary with duplication analysis
    """
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    line_counts = {}
    duplicates = []
    
    for i, line in enumerate(lines):
        if len(line) > 10:  # Skip very short lines
            if line in line_counts:
                line_counts[line].append(i)
            else:
                line_counts[line] = [i]
    
    for line, occurrences in line_counts.items():
        if len(occurrences) > 1:
            duplicates.append({
                "line": line,
                "occurrences": len(occurrences),
                "locations": occurrences
            })
    
    return {
        "total_unique_lines": len([l for l in lines if l]),
        "duplicates_found": len(duplicates),
        "duplicate_lines": duplicates,
        "duplication_percentage": (len(duplicates) / len(lines) * 100) if lines else 0
    }


def format_metrics_report(metrics: Dict[str, Any]) -> str:
    """
    Generate human-readable formatting report.
    
    Args:
        metrics: Dictionary of formatting analysis results
        
    Returns:
        Formatted report string
    """
    report = "📋 CODE FORMATTING ANALYSIS REPORT\n"
    report += "=" * 50 + "\n\n"
    
    for metric_name, metric_data in metrics.items():
        report += f"📊 {metric_name.upper()}\n"
        if isinstance(metric_data, dict):
            for key, value in metric_data.items():
                if key not in ['violations', 'issues', 'duplicates_found', 'duplicate_lines', 'locations']:
                    if isinstance(value, float):
                        report += f"  {key}: {value:.2f}\n"
                    else:
                        report += f"  {key}: {value}\n"
        report += "\n"
    
    return report
