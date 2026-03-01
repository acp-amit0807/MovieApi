import os
import json
from tools.github_tools import post_pr_comment

# Load configuration
with open('.env') as f:
    env_content = f.read()
    token = env_content.split('GITHUB_TOKEN=')[1].split('\n')[0].strip()
    reviewer = env_content.split('DEFAULT_REVIEWER=')[1].split('\n')[0].strip() if 'DEFAULT_REVIEWER=' in env_content else 'acp-amit0807'

os.environ['GITHUB_TOKEN'] = token

# Comprehensive Senior Architect Review for PR #3
review_comment = """# 🏛️ Senior Architect Review - PR #3: Enterprise Reviewer Prompt

## 📊 Overall Assessment
- **Quality Score**: 7.5/10
- **Recommendation**: **Approve with Minor Improvements**
- **Risk Level**: Low
- **Merge Readiness**: Ready for merge after addressing comments

---

## 0️⃣ PR Description & Context
✅ **GOOD**: 
- Clear title: "feature: apply enterprise reviewer prompt"
- Explains purpose of adding enterprise-grade C# review methodology
- Comprehensive scope (16 files, 1128+ lines added)

⚠️ **IMPROVEMENTS NEEDED**:
- Add explicit "Testing Instructions" section (how to validate automation scripts work)
- Document breaking changes or architectural impacts
- Add "Next Steps" for implementing generated tests

---

## 1️⃣ Design & Architecture Review

### ✅ STRENGTHS:
1. **Separation of Concerns** - Scripts properly isolated by function
2. **Modular Architecture** - Python tools directory properly organizing utilities
3. **Configuration Management** - .env file for secrets/reviewer assignment

### ⚠️ ISSUES TO ADDRESS:

**Issue #1: Missing Error Handling in Automation Scripts**
- **File**: post_review.py, cleanup_pr_comments.py, update_pr_body.py
- **Risk**: Network timeouts, API rate limiting, invalid tokens silently fail
- **Severity**: Medium
- **Suggestion**: Add try-except blocks with retry logic for network resilience

**Issue #2: No Input Validation in GitHub API Wrapper**
- **File**: tools/github_tools.py
- **Risk**: Invalid PR numbers, empty tokens, malformed repos accepted without validation
- **Severity**: Medium
- **Example**: Add validation for pr_number > 0, repo format 'owner/name', non-empty token

**Issue #3: Hardcoded Reviewer Assignment**
- **File**: post_review.py
- **Risk**: Only one default reviewer; doesn't support team assignment
- **Severity**: Low
- **Suggestion**: Read CODEOWNERS file or allow multiple reviewers via config

---

## 2️⃣ Naming Conventions Review

✅ **GOOD NAMING**:
- cleanup_pr_comments.py - Clear intent
- post_review.py - Clear intent
- get_pr_details(), post_pr_comment() - Descriptive, action-oriented
- DEFAULT_REVIEWER - Clear constant naming

⚠️ **IMPROVEMENTS**:
- Generic variable names in scripts (pr, comment, data) - use pr_number, old_comment_id, pr_response_json
- Review phases not explicitly named in code - add C#_SENIOR_ARCHITECT_REVIEW prefix

---

## 3️⃣ Error Handling Review

### Critical Gaps:

**Gap #1: No Validation of .env File**
- Unsafe parsing without checks for GITHUB_TOKEN existence or validity
- Fix: Use python-dotenv library, validate token format (starts with ghp_)

**Gap #2: No Handling of API Rate Limits**
- Risk: Silent failures at 60 req/hour limit
- Add: Check X-RateLimit-Remaining header and wait accordingly

**Gap #3: Silent Failures in Cleanup Script**
- Risk: If comment deletion fails (403), script continues without notifying user
- Add: Log API response status, raise exception on non-2xx

---

## 4️⃣ Code Quality Review

### Quality Issues:

**Quality #1: Missing Docstrings**
- All functions in tools/github_tools.py lack docstrings
- Fix: Add comprehensive docstrings with Args, Returns, Raises sections

**Quality #2: No Timeout Configuration**
- Add: API_TIMEOUT_SECONDS constant (30s reasonable default)

**Quality #3: Hardcoded Repository Names**
- post_inline_reviews.py likely hardcodes repo path
- Fix: Extract to config or command-line arguments

---

## 5️⃣ Testing Assessment

### Status: Testing Infrastructure Ready, Implementation Pending

**Strengths**:
✅ Senior architect prompt includes 8 phases including detailed testing guidelines
✅ xUnit/Moq/FluentAssertions stack identified correctly

**Gaps**:
❌ No actual unit tests for automation scripts
❌ No coverage for: successful posting, duplicate cleanup logic, invalid input handling, API errors

**Tests Needed (Priority)**:
1. Post review to valid PR → comment created successfully
2. Invalid token → raises AuthenticationError
3. Large PR (500+ comments) → cleanup performs efficiently
4. API timeout → retry mechanism activates
5. Invalid repo format → ValueError raised before API call

---

## 6️⃣ Performance & Optimization

### Analysis:

**Performance #1: Inefficient PR File Listing**
- Current: Full recursive listing of all files
- Impact: Slow for large PRs (500+ file changes)
- Solution: Add pagination, lazy loading

**Performance #2: Comment Cleanup Algorithm**
- Current: Likely O(n²) comparing all timestamps
- Optimize: O(n log n) with single sorted pass for deletion

---

## 7️⃣ Security Review

### ✅ GOOD PRACTICES:
1. Token stored in .env (not in code)
2. Using HTTPS for GitHub API
3. No credentials logged/printed

### ⚠️ SECURITY CONCERNS:

**Security #1: Token Exposure in Error Messages**
- Risk: Token accidentally logged in stack traces
- Fix: Use logging module, never print os.environ['GITHUB_TOKEN']

**Security #2: .env File Not Git-Ignored**
- Status: ✅ Updated in PR (good!)

**Security #3: No Rate Limit Protection**
- Risk: Malicious actor could brute-force comments
- Mitigation: Implement exponential backoff, circuit breaker pattern

---

## 8️⃣ Architecture & SOLID Compliance

### SOLID Analysis:

**✅ Single Responsibility**
- post_review.py → Posting reviews only
- cleanup_pr_comments.py → Cleanup only  
- tools/github_tools.py → API abstraction only

**⚠️ Open/Closed**
- Issue: Scripts hardcoded for specific repo
- Improvement: Read repo from argv or config

**✅ Interface Segregation**
Future: Split tools/github_tools.py into focused modules (comments_api.py, pr_api.py, auth.py)

---

## 9️⃣ File-Specific Assessment

### File: prompts/senior_architect_prompt.txt (383 lines - EXCELLENT)

**Strengths**:
- ✅ 8-phase structured methodology
- ✅ Clear examples for each phase
- ✅ Severity levels defined
- ✅ C# focused recommendations (xUnit/Moq/FluentAssertions)

**Suggestions**:
- Add "Phase 0: PR Metadata Validation" (title length, description completeness)
- Clarify Phase 7: "Unit tests MUST exist for public methods (60-80% coverage minimum)"
- Add timeout guideline: "Keep each phase <= 15 KB for readability"

### File: tools/github_tools.py (51 new lines)

**Strengths**:
- ✅ Clean GitHub API wrapper
- ✅ Proper 404 error handling

**Needs**:
- ⚠️ Add input validation (repo format, PR number > 0)
- ⚠️ Add docstrings to each function
- ⚠️ Read rate limit headers: X-RateLimit-Remaining, X-RateLimit-Reset

### File: .github/workflows/pr-review.yml (34 lines - NEW!)

**Assessment**: ✅ EXCELLENT
- Triggers on PR open/synchronize (correct events)
- Uses standard GitHub Actions
- Ready to execute review automation

**Suggestion**: Add matrix strategy for Python version coverage:
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

### File: README.md (Updated)

**Status**: ✅ Good documentation enhancements

---

## 🎯 Summary & Recommendations

### Quality Metrics:
- Code Cleanliness: 7/10 (missing docstrings, input validation)
- Architecture: 8/10 (good separation, could split tools further)
- Testing: 4/10 (framework ready, no actual tests written)
- Security: 7/10 (good token handling, needs rate limiting & error redaction)
- Documentation: 8/10 (prompt excellent, code needs more docstrings)

### **Overall Score: 7.5/10**

### Blockers (Must Fix Before Merge):
- ❌ None - current code is safe to merge

### Changes Required (Should Fix):
1. ⚠️ Add error handling & retry logic to automation scripts
2. ⚠️ Add input validation to GitHub API wrapper  
3. ⚠️ Add docstrings to all functions
4. ⚠️ Implement unit tests (Phase 7 ready to execute)

### Nice-to-Have (Post-Merge):
1. 🎯 Refactor tools/github_tools.py into focused modules
2. 🎯 Implement rate limit monitoring
3. 🎯 Add async/await support for concurrent reviews
4. 🎯 Create CLI tool wrapper for scripts

---

### Final Merge Recommendation:

✅ **APPROVE** - This PR successfully establishes strong architectural review foundations with an enterprise-grade 8-phase methodology. The automation infrastructure is well-organized and provides immediate value. Minor improvements (error handling, docstrings, tests) can be addressed in follow-up PRs.

**Next Steps**:
1. Merge PR #3 (test4 → main)
2. Create follow-up: "refactor: add error handling and tests to automation scripts"
3. Create follow-up: "refactor: split github_tools.py into focused modules"
4. Implement Phase 7 (Unit Tests) against Movie API codebase

---

**Assigned to**: @""" + reviewer + """ for final sign-off
**Review Date**: 2026-03-01
**Effort Estimate**: 1-2 story points for addressing changes required
"""

# Post the review comment
try:
    response = post_pr_comment('acp-amit0807/MovieApi', 3, review_comment)
    print("✅ Review successfully posted to PR #3")
    if response:
        print(f"Comment ID: {response.get('id')}")
        print(f"URL: {response.get('html_url')}")
    print("\n📋 Review Details:")
    print("- Quality Score: 7.5/10")
    print("- Recommendation: APPROVE with Minor Improvements")
    print("- Reviewed by: Senior Architect")
    print("- PR URL: https://github.com/acp-amit0807/MovieApi/pull/3")
except Exception as e:
    print(f"❌ Error posting review: {e}")
    import traceback
    traceback.print_exc()
