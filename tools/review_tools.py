import re

def extract_csharp_changes(files):
    code = ""
    for f in files:
        if f["filename"].endswith(".cs"):
            code += f"\nFile: {f['filename']}\n"
            code += f.get("patch", "")
    return code


def check_unit_tests(files):
    """
    Checks whether test files exist in PR.
    """
    for f in files:
        if "test" in f["filename"].lower():
            return True
    return False


def detect_hardcoded_values(code: str):
    """
    Detects common hardcoded values like connection strings, URLs, magic numbers.
    """
    issues = []

    # Hardcoded URLs
    if re.search(r"http[s]?://", code):
        issues.append("Hardcoded URL detected.")

    # Magic numbers (simple heuristic)
    if re.search(r"\b\d{3,}\b", code):
        issues.append("Possible magic number detected.")

    # Connection strings
    if "Server=" in code or "Password=" in code:
        issues.append("Possible hardcoded connection string detected.")

    return issues