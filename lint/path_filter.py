#!/usr/bin/env python3

# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

"""
Filter files by include-paths patterns.

Filters a list of files to only include those matching the specified glob patterns.
Uses fnmatch for native glob support (*, **, ?).

Usage:
    INCLUDE_PATHS="docs/team-a docs/team-b" python3 path_filter.py

Environment variables:
    INCLUDE_PATHS: Space or newline-separated list of glob patterns
    DEBUG: Set to 'true' for verbose output
    GITHUB_OUTPUT: Path to GitHub Actions output file (optional)
"""

import fnmatch
import os
import sys


def parse_patterns(include_paths: str) -> tuple[list[str], list[str]]:
    """Parse include-paths input (handles multi-line and space-separated).

    Patterns prefixed with ``!`` are treated as exclusions. Returns a tuple
    of ``(include_patterns, exclude_patterns)`` with the ``!`` prefix stripped
    from exclusion entries.
    """
    includes = []
    excludes = []
    for line in include_paths.split('\n'):
        for pattern in line.split():
            pattern = pattern.strip().rstrip('/')
            if not pattern:
                continue
            if pattern.startswith('!'):
                negated = pattern[1:].rstrip('/')
                if negated:
                    excludes.append(negated)
            else:
                includes.append(pattern)
    return includes, excludes


def matches_pattern(file: str, pattern: str) -> bool:
    """Check if a file matches a pattern (glob or prefix)."""
    if fnmatch.fnmatch(file, pattern):
        return True
    if file.startswith(pattern + '/'):
        return True
    return False


def filter_files(
    files: list[str],
    includes: list[str],
    excludes: list[str] | None = None,
    debug: bool = False,
) -> list[str]:
    """Filter files to only those matching an include pattern and no exclude pattern."""
    if excludes is None:
        excludes = []
    filtered = []
    for file in files:
        matched = any(matches_pattern(file, p) for p in includes)
        excluded = any(matches_pattern(file, p) for p in excludes)
        if matched and not excluded:
            if debug:
                print(f"::debug::File '{file}' matched", file=sys.stderr)
            filtered.append(file)
        elif debug:
            reason = 'excluded by negation' if matched and excluded else 'no match'
            print(f"::debug::File '{file}' excluded ({reason})", file=sys.stderr)
    return filtered


def set_output(name: str, value: str) -> None:
    """Set GitHub Actions output variable."""
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f'{name}={value}\n')


def main() -> int:
    include_paths = os.environ.get('INCLUDE_PATHS', '')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    includes, excludes = parse_patterns(include_paths)
    
    if not includes:
        print('No include patterns provided')
        return 0
    
    if debug:
        print(f'::debug::Include patterns: {includes}', file=sys.stderr)
        if excludes:
            print(f'::debug::Exclude patterns: {excludes}', file=sys.stderr)
    
    # Read files to lint
    try:
        with open('files_to_lint.txt', 'r') as f:
            files = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('No files_to_lint.txt found')
        return 0
    
    print(f'Filtering {len(files)} files against {len(includes)} include and {len(excludes)} exclude patterns...')
    
    filtered = filter_files(files, includes, excludes, debug)
    
    # Write results
    if filtered:
        with open('files_to_lint.txt', 'w') as f:
            f.write('\n'.join(filtered) + '\n')
        print(f'Files after filtering ({len(filtered)}):')
        for file in filtered:
            print(f'  {file}')
        set_output('has_files', 'true')
    else:
        print('No files matched include-paths patterns')
        if os.path.exists('files_to_lint.txt'):
            os.remove('files_to_lint.txt')
        set_output('has_files', 'false')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
