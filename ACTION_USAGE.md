# Using the Elastic Vale Action

This repository provides a reusable GitHub Action that can be used by any Elastic repository to lint documentation files with Vale using the Elastic style guide.

## Quick Start Linting

Create a workflow file in your repository (e.g., `.github/workflows/vale-lint.yml`):

```yaml
name: Vale Documentation Linting

on:
  pull_request:
    paths:
      - '**.md'
      - '**.adoc'

jobs:
  vale:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Run Elastic Vale Linter
        uses: elastic/vale-rules@main
        with:
          reporter: github-pr-review
```

**Note:** Using `@main` ensures you always get the latest style rules. For stability, you can pin to a specific version tag once releases are available (e.g., `@v1.0.0`).

## Inputs

All inputs are optional:

| Input | Description | Default |
|-------|-------------|---------|
| `files` | Files or directories to lint (space-separated). If not provided, lints changed files in PR. | `''` (empty, uses changed files) |
| `fail_on_error` | Fail the action if Vale finds errors | `false` |
| `reporter` | Reviewdog reporter type | `github-pr-review` |
| `filter_mode` | Reviewdog filter mode | `added` |
| `vale_version` | Vale version to install | `latest` |

## Examples

### Basic usage (lint changed files in PR)

```yaml
- uses: elastic/vale-rules@main
```

### Lint specific files or directories

```yaml
- uses: elastic/vale-rules@main
  with:
    files: 'docs/ README.md'
```

### Fail on errors

```yaml
- uses: elastic/vale-rules@main
  with:
    fail_on_error: true
```

### Use different reviewdog reporter

```yaml
# For inline PR comments
- uses: elastic/vale-rules@main
  with:
    reporter: github-pr-review

# For check run annotations
- uses: elastic/vale-rules@main
  with:
    reporter: github-pr-check

# For both
- uses: elastic/vale-rules@main
  with:
    reporter: github-check
```

### Different filter modes

```yaml
# Only show issues on added lines (default)
- uses: elastic/vale-rules@main
  with:
    filter_mode: added

# Show issues on the entire diff context
- uses: elastic/vale-rules@main
  with:
    filter_mode: diff_context

# Show all issues in changed files
- uses: elastic/vale-rules@main
  with:
    filter_mode: file

# Show all issues (no filtering)
- uses: elastic/vale-rules@main
  with:
    filter_mode: nofilter
```

## Complete example

```yaml
name: Documentation Linting

on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - '**.md'
      - '**.adoc'
      - 'docs/**'

permissions:
  contents: read
  pull-requests: write  # Required for PR comments

jobs:
  vale-lint:
    name: Vale Documentation Linting
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for proper diff analysis
      
      - name: Run Vale with Elastic style guide
        uses: elastic/vale-rules@main
        with:
          reporter: github-pr-review
          filter_mode: added
          fail_on_error: false
```

## Supported platforms

The action automatically detects the runner OS and installs Vale accordingly:

- **Ubuntu/Linux**: Uses snap
- **macOS**: Uses Homebrew
- **Self-hosted runners**: Ensure Vale is pre-installed or accessible via package manager

## How it works

1. Detects the operating system
2. Installs Vale if not already present
3. Downloads the latest Elastic style guide package from this repository (includes `.vale.ini` configuration and styles)
4. Vale automatically merges the packaged configuration settings (SkippedScopes, IgnoredScopes, TokenIgnores, etc.)
5. Identifies files to lint (changed files in PR or specified files)
6. Runs Vale on the files with the Elastic configuration
7. Posts results as PR comments or check annotations via reviewdog

## Permissions required

The action requires the following permissions:

```yaml
permissions:
  contents: read           # To checkout code
  pull-requests: write     # To post PR comments (for github-pr-review reporter)
  checks: write            # To create check runs (for github-pr-check reporter)
```

## Troubleshooting

### No comments appearing on PR

1. Ensure `pull-requests: write` permission is set
2. Check that files were actually changed in the PR
3. Try using `filter_mode: file` to see all issues in changed files

### Action fails to install Vale

- For self-hosted runners, pre-install Vale or ensure package managers (snap/brew) are available
- Check runner logs for specific installation errors

### Vale finds no issues but you expect some

1. Verify the files match the patterns in your `.vale.ini` (`.md`, `.adoc`)
2. Check that the files are included in the `files` input or are part of the PR diff
3. Use `filter_mode: nofilter` to see all issues

## Version pinning

It's recommended to pin to a specific version:

```yaml
- uses: elastic/vale-rules@v1.0.0  # Pin to specific version
- uses: elastic/vale-rules@v1      # Pin to v1.x.x
- uses: elastic/vale-rules@main    # Use latest (not recommended for production)
```

## Local testing

To test the same rules locally, use the installation scripts:

```bash
# macOS
./install-macos.sh

# Linux  
./install-linux.sh

# Windows
.\install-windows.ps1
```

Then run Vale on your files:

```bash
vale path/to/your/docs
```