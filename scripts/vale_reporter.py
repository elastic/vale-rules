#!/usr/bin/env python3
"""
Vale Reporter - Parse Vale JSON output and generate GitHub-friendly reports.

This script filters Vale issues to only modified lines, generates GitHub Actions
annotations for inline diff display, and creates a markdown report for PR comments.
"""

import json
import sys
import os
import hashlib
from typing import Dict, List, Tuple, Optional


def load_vale_output(file_path: str) -> Dict:
    """Load and parse Vale JSON output."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("::warning::Vale output file not found", file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(f"::warning::Failed to parse Vale JSON output: {e}", file=sys.stderr)
        return {}


def load_modified_ranges(file_path: str) -> Dict[str, List[Tuple[int, int]]]:
    """Load modified line ranges from git diff output."""
    modified_ranges = {}
    
    if not os.path.exists(file_path):
        return modified_ranges
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    file, start, count = parts
                    if file not in modified_ranges:
                        modified_ranges[file] = []
                    start_line = int(start)
                    end_line = start_line + int(count)
                    modified_ranges[file].append((start_line, end_line))
    except (IOError, ValueError) as e:
        print(f"::warning::Failed to load modified line ranges: {e}", file=sys.stderr)
    
    return modified_ranges


def filter_issues_to_modified_lines(
    vale_data: Dict,
    modified_ranges: Dict[str, List[Tuple[int, int]]]
) -> Dict[str, List[Dict]]:
    """Filter Vale issues to only those on modified lines."""
    filtered_issues = {'error': [], 'warning': [], 'suggestion': []}
    
    for file, issues in vale_data.items():
        for issue in issues:
            line_num = issue.get('Line', 0)
            
            # If we have modified ranges, check if this line is modified
            if modified_ranges:
                if file in modified_ranges:
                    is_modified = any(start <= line_num < end for start, end in modified_ranges[file])
                    if not is_modified:
                        continue
                else:
                    # File not in modified ranges, skip
                    continue
            
            # Categorize by severity
            severity = issue.get('Severity', 'suggestion').lower()
            if severity not in filtered_issues:
                severity = 'suggestion'
            
            filtered_issues[severity].append({
                'file': file,
                'line': line_num,
                'rule': issue.get('Check', 'Unknown'),
                'message': issue.get('Message', '')
            })
    
    return filtered_issues


def generate_github_annotations(filtered_issues: Dict[str, List[Dict]]) -> None:
    """Output GitHub Actions annotations for inline diff view."""
    for severity, issues in filtered_issues.items():
        for issue in issues:
            # Map Vale severity to GitHub annotation level
            if severity == 'error':
                annotation_level = 'error'
            elif severity == 'warning':
                annotation_level = 'warning'
            else:
                annotation_level = 'notice'
            
            # Output GitHub Actions annotation
            print(f"::{annotation_level} file={issue['file']},line={issue['line']}::{issue['rule']}: {issue['message']}")


def generate_diff_hash(file_path: str) -> str:
    """
    Generate a GitHub-style diff hash for file anchors.
    GitHub uses a hash based on the file path for diff anchors.
    """
    # GitHub uses SHA256 of "a/{path}" and "b/{path}" combined
    hash_input = f"diff --git a/{file_path} b/{file_path}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()


def format_line_link(
    file_path: str,
    line_num: int,
    github_repo: str,
    pr_number: str
) -> str:
    """Create a clickable link to the specific line in the PR diff."""
    if github_repo and pr_number:
        diff_hash = generate_diff_hash(file_path)
        url = f"https://github.com/{github_repo}/pull/{pr_number}/files#diff-{diff_hash}R{line_num}"
        return f"[{line_num}]({url})"
    return str(line_num)


def generate_markdown_report(
    filtered_issues: Dict[str, List[Dict]],
    github_repo: str,
    pr_number: str,
    output_file: str
) -> Tuple[int, int, int]:
    """Generate markdown report with clickable line links."""
    error_count = len(filtered_issues['error'])
    warning_count = len(filtered_issues['warning'])
    suggestion_count = len(filtered_issues['suggestion'])
    total_count = error_count + warning_count + suggestion_count
    
    if total_count == 0:
        report = "## ✅ Vale Linting Results\n\n**No issues found on modified lines!**\n"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        return 0, 0, 0
    
    # Build summary
    summary_parts = []
    if error_count > 0:
        summary_parts.append(f"{error_count} error{'s' if error_count != 1 else ''}")
    if warning_count > 0:
        summary_parts.append(f"{warning_count} warning{'s' if warning_count != 1 else ''}")
    if suggestion_count > 0:
        summary_parts.append(f"{suggestion_count} suggestion{'s' if suggestion_count != 1 else ''}")
    
    summary = ", ".join(summary_parts)
    
    report = f"## Vale Linting Results\n\n**Summary:** {summary} found\n\n"
    
    # Add sections for each severity
    if error_count > 0:
        report += f"<details>\n<summary>❌ Errors ({error_count})</summary>\n\n"
        report += "| File | Line | Rule | Message |\n"
        report += "|------|------|------|----------|\n"
        for issue in filtered_issues['error']:
            line_link = format_line_link(issue['file'], issue['line'], github_repo, pr_number)
            report += f"| {issue['file']} | {line_link} | {issue['rule']} | {issue['message']} |\n"
        report += "\n</details>\n\n"
    
    if warning_count > 0:
        report += f"<details>\n<summary>⚠️ Warnings ({warning_count})</summary>\n\n"
        report += "| File | Line | Rule | Message |\n"
        report += "|------|------|------|----------|\n"
        for issue in filtered_issues['warning']:
            line_link = format_line_link(issue['file'], issue['line'], github_repo, pr_number)
            report += f"| {issue['file']} | {line_link} | {issue['rule']} | {issue['message']} |\n"
        report += "\n</details>\n\n"
    
    if suggestion_count > 0:
        report += f"<details>\n<summary>💡 Suggestions ({suggestion_count})</summary>\n\n"
        report += "| File | Line | Rule | Message |\n"
        report += "|------|------|------|----------|\n"
        for issue in filtered_issues['suggestion']:
            line_link = format_line_link(issue['file'], issue['line'], github_repo, pr_number)
            report += f"| {issue['file']} | {issue['line']} | {issue['rule']} | {issue['message']} |\n"
        report += "\n</details>\n\n"
    
    # Write report
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    except IOError as e:
        print(f"::error::Failed to write report: {e}", file=sys.stderr)
        sys.exit(1)
    
    return error_count, warning_count, suggestion_count


def main():
    """Main entry point."""
    # Get GitHub context
    github_repo = os.environ.get('GITHUB_REPOSITORY', '')
    pr_number = os.environ.get('PR_NUMBER', '')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    if debug:
        print("::debug::Vale Reporter starting", file=sys.stderr)
        print(f"::debug::Repository: {github_repo}", file=sys.stderr)
        print(f"::debug::PR Number: {pr_number}", file=sys.stderr)
    
    # Load Vale output
    vale_data = load_vale_output('vale_output.json')
    if not vale_data:
        print("No Vale issues found or empty output")
        # Create empty report
        with open('vale_report.md', 'w', encoding='utf-8') as f:
            f.write("## ✅ Vale Linting Results\n\n**No issues found on modified lines!**\n")
        with open('issue_counts.txt', 'w', encoding='utf-8') as f:
            f.write("errors=0\nwarnings=0\nsuggestions=0\n")
        return
    
    # Load modified line ranges
    modified_ranges = load_modified_ranges('line_ranges.txt')
    
    if debug and modified_ranges:
        print(f"::debug::Loaded {len(modified_ranges)} files with modified ranges", file=sys.stderr)
    
    # Filter issues to modified lines only
    filtered_issues = filter_issues_to_modified_lines(vale_data, modified_ranges)
    
    # Generate GitHub Actions annotations
    generate_github_annotations(filtered_issues)
    
    # Generate markdown report
    error_count, warning_count, suggestion_count = generate_markdown_report(
        filtered_issues,
        github_repo,
        pr_number,
        'vale_report.md'
    )
    
    # Write counts for shell script
    with open('issue_counts.txt', 'w', encoding='utf-8') as f:
        f.write(f"errors={error_count}\n")
        f.write(f"warnings={warning_count}\n")
        f.write(f"suggestions={suggestion_count}\n")
    
    total_count = error_count + warning_count + suggestion_count
    print(f"Generated report with {total_count} issue(s): {error_count} errors, {warning_count} warnings, {suggestion_count} suggestions")


if __name__ == '__main__':
    main()

