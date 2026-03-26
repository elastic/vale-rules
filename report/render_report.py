#!/usr/bin/env python3

# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

"""
Render Report - Validate artifact JSON and render a trusted markdown report.

This script is the security boundary between the untrusted artifact produced by
the lint workflow (which runs on fork PRs) and the privileged report workflow
(which posts PR comments).  It validates vale_results.json against a strict
schema, sanitizes all string values, and renders markdown from a hardcoded
template so that an attacker who controls the artifact cannot inject arbitrary
content into a bot comment.
"""

import argparse
import hashlib
import json
import os
import re
import sys


# --- constants ---------------------------------------------------------------

MAX_FILE_SIZE = 100 * 1024  # 100 KB
MAX_PATH_LEN = 256
MAX_MESSAGE_LEN = 512
MAX_RULE_LEN = 128
MAX_ISSUES = 1000
ALLOWED_SEVERITIES = frozenset({"error", "warning", "suggestion"})
RULE_PATTERN = re.compile(r'^[A-Za-z0-9_.]+$')

REPORT_FOOTER = """
---

The Vale linter checks documentation changes against the [Elastic Docs style guide](https://www.elastic.co/docs/contribute-docs/style-guide).

To use Vale locally or report issues, refer to [Elastic style guide for Vale](https://www.elastic.co/docs/contribute-docs/vale-linter).
"""

# --- validation / sanitisation -----------------------------------------------


def sanitize_text(text: str) -> str:
    """Strip HTML tags, markdown links, bare URLs, and injection characters."""
    text = re.sub(r'<[^>]+>', '', text)                        # HTML tags
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)      # [text](url) -> text
    text = re.sub(r'https?://\S+', '', text)                   # bare URLs
    text = re.sub(r'[<>\[\]()!]', '', text)                    # remaining injection chars
    text = text.replace('|', '\\|')                            # escape table pipe
    return text.strip()


def sanitize_path(path: str) -> str:
    """Sanitize a file path value - similar to sanitize_text but preserves path chars."""
    path = re.sub(r'<[^>]+>', '', path)
    path = re.sub(r'[<>\[\]()!]', '', path)
    path = path.replace('|', '\\|')
    return path.strip()


def validate(data: object) -> list:
    """Validate vale_results.json against the expected schema.

    Returns a list of error strings.  An empty list means the data is valid.
    """
    errors = []

    if not isinstance(data, dict):
        return ["root must be an object"]

    allowed_keys = {"summary", "issues"}
    extra = set(data.keys()) - allowed_keys
    if extra:
        errors.append(f"unexpected top-level keys: {extra}")
    if not set(data.keys()) >= allowed_keys:
        errors.append(f"missing top-level keys: {allowed_keys - set(data.keys())}")
    if errors:
        return errors

    # --- summary ---
    summary = data["summary"]
    if not isinstance(summary, dict):
        return ["summary must be an object"]
    summary_keys = {"errors", "warnings", "suggestions"}
    if set(summary.keys()) != summary_keys:
        errors.append(f"summary keys must be exactly {summary_keys}, got {set(summary.keys())}")
        return errors
    for key in summary_keys:
        val = summary[key]
        if not isinstance(val, int) or val < 0:
            errors.append(f"summary.{key} must be a non-negative integer, got {val!r}")

    # --- issues ---
    issues = data["issues"]
    if not isinstance(issues, list):
        return ["issues must be a list"]
    if len(issues) > MAX_ISSUES:
        errors.append(f"too many issues ({len(issues)} > {MAX_ISSUES})")
        return errors

    issue_keys = {"path", "line", "rule", "severity", "message"}
    counts = {"error": 0, "warning": 0, "suggestion": 0}

    for i, issue in enumerate(issues):
        prefix = f"issues[{i}]"
        if not isinstance(issue, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if set(issue.keys()) != issue_keys:
            errors.append(f"{prefix} keys must be exactly {issue_keys}, got {set(issue.keys())}")
            continue

        # path
        path = issue["path"]
        if not isinstance(path, str) or len(path) > MAX_PATH_LEN:
            errors.append(f"{prefix}.path must be a string <= {MAX_PATH_LEN} chars")
        elif '\x00' in path:
            errors.append(f"{prefix}.path contains null byte")
        elif '..' in path.split('/'):
            errors.append(f"{prefix}.path contains '..' traversal")

        # line
        line = issue["line"]
        if not isinstance(line, int) or line < 1:
            errors.append(f"{prefix}.line must be a positive integer, got {line!r}")

        # rule
        rule = issue["rule"]
        if not isinstance(rule, str) or len(rule) > MAX_RULE_LEN:
            errors.append(f"{prefix}.rule must be a string <= {MAX_RULE_LEN} chars")
        elif not RULE_PATTERN.match(rule):
            errors.append(f"{prefix}.rule contains invalid characters: {rule!r}")

        # severity
        severity = issue["severity"]
        if severity not in ALLOWED_SEVERITIES:
            errors.append(f"{prefix}.severity must be one of {ALLOWED_SEVERITIES}, got {severity!r}")
        else:
            counts[severity] = counts.get(severity, 0) + 1

        # message
        message = issue["message"]
        if not isinstance(message, str) or len(message) > MAX_MESSAGE_LEN:
            errors.append(f"{prefix}.message must be a string <= {MAX_MESSAGE_LEN} chars")

    # summary count cross-check
    if not errors:
        if summary["errors"] != counts["error"]:
            errors.append(f"summary.errors ({summary['errors']}) != actual error count ({counts['error']})")
        if summary["warnings"] != counts["warning"]:
            errors.append(f"summary.warnings ({summary['warnings']}) != actual warning count ({counts['warning']})")
        if summary["suggestions"] != counts["suggestion"]:
            errors.append(f"summary.suggestions ({summary['suggestions']}) != actual suggestion count ({counts['suggestion']})")

    return errors


# --- rendering ---------------------------------------------------------------


def generate_diff_hash(file_path: str) -> str:
    """Generate a GitHub-style diff hash for file anchors.

    Must match the algorithm in lint/vale_reporter.py:generate_diff_hash().
    GitHub uses SHA-256 of the normalised file path (leading ./ stripped).
    """
    normalized = file_path.lstrip('./')
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def format_line_link(path: str, line: int, repo: str, pr: str) -> str:
    """Create a clickable link to the specific line in the PR diff."""
    if repo and pr:
        diff_hash = generate_diff_hash(path)
        url = f"https://github.com/{repo}/pull/{pr}/files#diff-{diff_hash}R{line}"
        return f"[{line}]({url})"
    return str(line)


def render(data: dict, repo: str, pr: str) -> str:
    """Render validated JSON data into the markdown report."""
    # Group issues by severity
    groups: dict = {"error": [], "warning": [], "suggestion": []}
    for issue in data["issues"]:
        groups[issue["severity"]].append(issue)

    error_count = len(groups["error"])
    warning_count = len(groups["warning"])
    suggestion_count = len(groups["suggestion"])
    total = error_count + warning_count + suggestion_count

    if total == 0:
        return "## " + "\u2705 Vale Linting Results\n\n**No issues found on modified lines!**\n" + REPORT_FOOTER

    # Summary line
    parts = []
    if error_count > 0:
        parts.append(f"{error_count} error{'s' if error_count != 1 else ''}")
    if warning_count > 0:
        parts.append(f"{warning_count} warning{'s' if warning_count != 1 else ''}")
    if suggestion_count > 0:
        parts.append(f"{suggestion_count} suggestion{'s' if suggestion_count != 1 else ''}")
    summary = ", ".join(parts)

    report = f"## Vale Linting Results\n\n**Summary:** {summary} found\n\n"

    section_info = [
        ("error",      groups["error"],      f"\u274c Errors ({error_count})"),
        ("warning",    groups["warning"],    f"\u26a0\ufe0f Warnings ({warning_count})"),
        ("suggestion", groups["suggestion"], f"\U0001f4a1 Suggestions ({suggestion_count})"),
    ]

    for _severity, items, heading in section_info:
        if not items:
            continue
        report += f"<details>\n<summary>{heading}</summary>\n\n"
        report += "| File | Line | Rule | Message |\n"
        report += "|------|------|------|----------|\n"
        for issue in items:
            path = sanitize_path(issue["path"])
            message = sanitize_text(issue["message"])
            rule = issue["rule"]  # already validated by regex
            line_link = format_line_link(issue["path"], issue["line"], repo, pr)
            report += f"| {path} | {line_link} | {rule} | {message} |\n"
        report += "\n</details>\n\n"

    report += REPORT_FOOTER
    return report


# --- CLI entry point ---------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and render Vale results JSON")
    parser.add_argument("--input", required=True, help="Path to vale_results.json")
    parser.add_argument("--output", required=True, help="Path to write rendered vale_report.md")
    parser.add_argument("--repo", default="", help="GitHub repository (owner/repo)")
    parser.add_argument("--pr", default="", help="PR number")
    args = parser.parse_args()

    # File size check
    try:
        size = os.path.getsize(args.input)
    except OSError as e:
        print(f"::error::Cannot read input file: {e}", file=sys.stderr)
        return 1

    if size > MAX_FILE_SIZE:
        print(f"::error::Input file too large ({size} bytes > {MAX_FILE_SIZE})", file=sys.stderr)
        return 1

    # Parse JSON
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"::error::Failed to parse JSON: {e}", file=sys.stderr)
        return 1

    # Validate schema
    errors = validate(data)
    if errors:
        for err in errors:
            print(f"::error::Validation failed: {err}", file=sys.stderr)
        return 1

    # Render
    report = render(data, args.repo, args.pr)

    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
    except OSError as e:
        print(f"::error::Failed to write output: {e}", file=sys.stderr)
        return 1

    print(f"Rendered report with {len(data['issues'])} issue(s)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
