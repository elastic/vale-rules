#!/usr/bin/env python3
"""
Filter files by include-paths patterns.

Filters a list of files to only include those matching the specified glob patterns.
Supports both glob patterns (*, **, ?) and simple prefix matching.
"""

import fnmatch
import os
import sys


def parse_patterns(include_paths: str) -> list[str]:
    """Parse include-paths input (handles multi-line and space-separated)."""
    patterns = []
    for line in include_paths.split('\n'):
        for pattern in line.split():
            pattern = pattern.strip().rstrip('/')
            if pattern:
                patterns.append(pattern)
    return patterns


def matches_pattern(file: str, pattern: str) -> bool:
    """Check if a file matches a pattern (glob or prefix)."""
    # Try glob matching first
    if fnmatch.fnmatch(file, pattern):
        return True
    
    # For patterns with **, use fnmatch with the pattern as-is
    if '**' in pattern:
        # Convert ** to match any path segments
        glob_pattern = pattern.replace('**', '*')
        if fnmatch.fnmatch(file, glob_pattern):
            return True
    
    # Simple prefix matching for directory patterns
    if file.startswith(pattern + '/'):
        return True
    
    return False


def filter_files(files: list[str], patterns: list[str], debug: bool = False) -> list[str]:
    """Filter files to only those matching any pattern."""
    filtered = []
    
    for file in files:
        for pattern in patterns:
            if matches_pattern(file, pattern):
                if debug:
                    print(f"::debug::File '{file}' matched pattern '{pattern}'", file=sys.stderr)
                filtered.append(file)
                break
        else:
            if debug:
                print(f"::debug::File '{file}' excluded (no match)", file=sys.stderr)
    
    return filtered


def main():
    include_paths = os.environ.get('INCLUDE_PATHS', '')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    patterns = parse_patterns(include_paths)
    
    if not patterns:
        print('No patterns provided')
        return
    
    if debug:
        print(f'::debug::Patterns: {patterns}', file=sys.stderr)
    
    # Read files to lint
    try:
        with open('files_to_lint.txt', 'r') as f:
            files = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('No files_to_lint.txt found')
        return
    
    print(f'Filtering {len(files)} files against {len(patterns)} patterns...')
    
    # Filter files
    filtered = filter_files(files, patterns, debug)
    
    # Write results and set outputs
    if filtered:
        with open('files_to_lint.txt', 'w') as f:
            f.write('\n'.join(filtered) + '\n')
        print(f'Files after filtering ({len(filtered)}):')
        for file in filtered:
            print(f'  {file}')
        # Set GitHub Actions output
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write('has_files=true\n')
    else:
        print('No files matched include-paths patterns')
        if os.path.exists('files_to_lint.txt'):
            os.remove('files_to_lint.txt')
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write('has_files=false\n')


if __name__ == '__main__':
    main()
