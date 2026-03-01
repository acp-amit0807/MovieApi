"""
MCP Orchestrator for automated code review and PR analysis.

Orchestrates GitHub API interactions with local analysis tools to provide
comprehensive PR reviews and quality assessments.
"""
import os
import json
import sys
from dataclasses import asdict
from typing import Dict, Any, Optional

# GitHub API
import requests

# Local analysis tools
from tools.github_tools import (
    get_pr_details, get_pr_files, post_pr_comment, create_pull_request
)
from tools.review_tools import (
    extract_csharp_changes, check_unit_tests, analyze_pr_files, generate_review_summary
)
from tools.validation_tools import validate_pr_title, validate_pr_description, validate_all_pr_aspects
from tools.scoring_tools import score_pr_structured, format_score_report
from tools.formatting_tools import (
    analyze_line_lengths, check_indentation_consistency, 
    analyze_naming_conventions, detect_code_duplication
)


class PrAnalysisOrchestrator:
    """Orchestrates comprehensive PR analysis and review."""
    
    def __init__(self, repo: str, pr_number: int):
        """
        Initialize orchestrator.
        
        Args:
            repo: Repository in format 'owner/repo'
            pr_number: Pull request number
        """
        self.repo = repo
        self.pr_number = pr_number
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
    
    def fetch_pr_data(self) -> Dict[str, Any]:
        """
        Fetch all PR data from GitHub.
        
        Returns:
            Dictionary with PR details and file changes
        """
        try:
            pr_details = get_pr_details(self.repo, self.pr_number)
            pr_files = get_pr_files(self.repo, self.pr_number)
            
            return {
                "details": pr_details,
                "files": pr_files
            }
        except Exception as e:
            print(f"❌ Error fetching PR data: {e}")
            raise
    
    def analyze_codebase(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive code analysis using all available tools.
        
        Args:
            pr_data: PR data from GitHub API
            
        Returns:
            Dictionary with all analysis results
        """
        analysis_results = {}
        
        # 1. File Analysis
        print("📊 Analyzing files...")
        file_analysis = analyze_pr_files(pr_data["files"])
        analysis_results["files"] = file_analysis
        
        # 2. PR Validation
        print("✔️ Validating PR...")
        pr_title = pr_data["details"].get("title", "")
        pr_description = pr_data["details"].get("body", "")
        
        title_validation = validate_pr_title(pr_title)
        desc_validation = validate_pr_description(pr_description)
        
        analysis_results["validation"] = {
            "title": asdict(title_validation),
            "description": asdict(desc_validation)
        }
        
        # 3. Code Quality Metrics
        print("📈 Computing quality metrics...")
        csharp_code = "\n".join([
            f["patch"] for f in pr_data["files"]
            if f["filename"].endswith(".cs")
        ])
        
        line_metrics = analyze_line_lengths(csharp_code)
        indent_metrics = check_indentation_consistency(csharp_code)
        naming_metrics = analyze_naming_conventions(csharp_code)
        duplication = detect_code_duplication(csharp_code)
        
        analysis_results["formatting"] = {
            "line_length": line_metrics,
            "indentation": indent_metrics,
            "naming": naming_metrics,
            "duplication": duplication
        }
        
        # 4. PR Scoring
        print("🎯 Calculating PR score...")
        test_info = file_analysis.get("test_analysis", {})
        severity = analysis_results["files"].get("severity_breakdown", {})
        
        pr_score = score_pr_structured(
            title_valid=title_validation.is_valid,
            has_tests=test_info.get("has_tests", False),
            hardcoded_issues=severity.get("CRITICAL", 0),
            critical_issues=severity.get("CRITICAL", 0),
            high_issues=severity.get("HIGH", 0),
            medium_issues=severity.get("MEDIUM", 0),
            architecture_score=8.0 if indent_metrics["consistency_score"] > 80 else 6.0,
            code_quality_score=naming_metrics["quality_score"] / 10,
            security_score=10.0 if severity.get("CRITICAL", 0) == 0 else 5.0,
            documentation_quality=desc_validation.is_valid,
            pr_size_lines=pr_data["details"].get("additions", 0)
        )
        
        analysis_results["scoring"] = asdict(pr_score)
        
        return analysis_results
    
    def generate_review_comment(self, analysis: Dict[str, Any]) -> str:
        """
        Generate comprehensive review comment from analysis.
        
        Args:
            analysis: Analysis results from analyze_codebase
            
        Returns:
            Formatted review comment string
        """
        scoring = analysis["scoring"]
        files = analysis["files"]
        validation = analysis["validation"]
        formatting = analysis["formatting"]
        
        comment = f"""# 🔍 Automated PR Review - Comprehensive Analysis

## 📊 Overall Assessment
- **Quality Score**: {scoring['overall_score']}/10
- **Recommendation**: {scoring['recommendation']}
- **Files Analyzed**: {files['stats']['csharp_files']} C# files
- **Issues Found**: {files['issue_count']}

---

## 📋 Validation Summary

### PR Title: {'✅ VALID' if validation['title']['is_valid'] else '❌ INVALID'}
{validation['title']['message']}

### PR Description: {'✅ COMPREHENSIVE' if validation['description']['is_valid'] else '⚠️ NEEDS IMPROVEMENT'}
{validation['description']['message']}

---

## 📈 Quality Metrics

### Code Formatting
- **Average Line Length**: {formatting['line_length']['average_length']:.0f} chars
- **Line Length Violations**: {formatting['line_length']['violation_count']}
- **Indentation Consistency**: {formatting['indentation']['consistency_score']:.1f}%
- **Naming Violations**: {formatting['naming']['violation_count']}

### File Statistics
- **Total Files**: {files['stats']['total_files']}
- **C# Files**: {files['stats']['csharp_files']}
- **Test Files**: {files['stats']['test_files']}
- **Lines Added**: {files['stats']['total_additions']}
- **Lines Deleted**: {files['stats']['total_deletions']}

### Test Coverage
- **Has Tests**: {'✅ YES' if files['test_analysis']['has_tests'] else '❌ NO'}
- **Test Files**: {files['test_analysis']['test_file_count']}
- **Estimated Coverage**: {files['test_analysis']['estimated_coverage']:.1f}%

---

## 🎯 Issue Breakdown

"""
        
        severity = files.get("severity_breakdown", {})
        comment += f"- **Critical**: {severity.get('CRITICAL', 0)}\n"
        comment += f"- **High**: {severity.get('HIGH', 0)}\n"
        comment += f"- **Medium**: {severity.get('MEDIUM', 0)}\n"
        comment += f"- **Low**: {severity.get('LOW', 0)}\n"
        
        # Detailed issues
        if files.get("issues"):
            comment += "\n## 🔎 Detailed Issues\n\n"
            for i, issue in enumerate(files["issues"][:10], 1):  # Top 10 issues
                comment += f"**{i}. {issue.category} - {issue.severity.value}**\n"
                comment += f"   - **File**: {issue.file}:{issue.line_number}\n" if issue.line_number else ""
                comment += f"   - **Issue**: {issue.description}\n"
                comment += f"   - **Suggestion**: {issue.suggestion}\n"
                if issue.code_snippet:
                    comment += f"   - **Code**: `{issue.code_snippet}`\n"
                comment += "\n"
        
        # Recommendations
        if scoring.get("blockers"):
            comment += "## ❌ Blockers\n"
            for blocker in scoring["blockers"]:
                comment += f"- {blocker}\n"
            comment += "\n"
        
        if scoring.get("improvements"):
            comment += "## ⚠️ Required Improvements\n"
            for improvement in scoring["improvements"]:
                comment += f"- {improvement}\n"
            comment += "\n"
        
        if scoring.get("nice_to_haves"):
            comment += "## 💡 Nice-to-Haves\n"
            for nice in scoring["nice_to_haves"]:
                comment += f"- {nice}\n"
        
        comment += f"\n---\n**Generated by MCP Orchestrator** | {scoring['recommendation']}"
        
        return comment
    
    def post_review(self, review_comment: str) -> bool:
        """
        Post review comment to PR.
        
        Args:
            review_comment: Review comment text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            post_pr_comment(self.repo, self.pr_number, review_comment)
            print(f"✅ Review posted to PR #{self.pr_number}")
            return True
        except Exception as e:
            print(f"❌ Error posting review: {e}")
            return False
    
    def run_full_analysis(self, post_comment: bool = True) -> Dict[str, Any]:
        """
        Run complete analysis pipeline.
        
        Args:
            post_comment: Whether to post review as comment
            
        Returns:
            Dictionary with analysis results
        """
        try:
            print(f"🚀 Starting PR analysis for {self.repo}#{self.pr_number}")
            
            # Fetch data
            pr_data = self.fetch_pr_data()
            
            # Analyze
            analysis = self.analyze_codebase(pr_data)
            
            # Generate review
            review_comment = self.generate_review_comment(analysis)
            
            # Post if requested
            if post_comment:
                self.post_review(review_comment)
            
            print("✅ Analysis complete!")
            
            return {
                "success": True,
                "analysis": analysis,
                "review_comment": review_comment
            }
        
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Main entry point for orchestrator."""
    # Get environment
    github_token = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY")
    github_event_path = os.getenv("GITHUB_EVENT_PATH")
    
    if not all([github_token, github_repository]):
        print("❌ Missing required environment variables:")
        print("   - GITHUB_TOKEN")
        print("   - GITHUB_REPOSITORY")
        return 1
    
    # Get PR number from event
    try:
        if github_event_path and os.path.exists(github_event_path):
            with open(github_event_path) as f:
                event = json.load(f)
                pr_number = event.get("pull_request", {}).get("number")
        else:
            pr_number = int(os.getenv("GITHUB_REF", "").split("/")[-1])
    except (ValueError, KeyError, json.JSONDecodeError):
        print("❌ Could not determine PR number from GitHub context")
        return 1
    
    # Run analysis
    orchestrator = PrAnalysisOrchestrator(github_repository, pr_number)
    result = orchestrator.run_full_analysis(post_comment=True)
    
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())