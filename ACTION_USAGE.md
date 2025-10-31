# Using the Elastic Vale Action

This repository provides a reusable GitHub Action that can be used by any Elastic repository to lint documentation files with Vale using the Elastic style guide.

## Quick start linting

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
| `reporter` | Reviewdog reporter type for inline annotations (github-pr-review, github-pr-check, github-check) | `github-pr-review` |
| `vale_version` | Vale version to install | `latest` |

**Note:** The action always fails if Vale finds errors. Warnings and suggestions do not cause the action to fail, but are reported in the summary and as inline annotations.

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

### Use different reviewdog reporter for inline annotations

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
5. Identifies files to lint:
   - **When PR is opened/reopened**: Checks all changed files in the PR
   - **When new commits are pushed**: Only checks files changed in the new commit (prevents duplicate comments)
   - **When files specified manually**: Uses the provided files
6. Runs Vale on the files with the Elastic configuration
7. Posts results in three ways:
   - **GitHub Actions Summary**: Detailed report with issue counts by severity and file
   - **Inline annotations**: Errors and warnings shown via reviewdog on the relevant lines
   - **PR comment**: Single summary comment with issue counts and link to full report
8. Fails the action if any errors are found (warnings and suggestions don't fail the build)

## Permissions required

The action requires the following permissions:

```yaml
permissions:
  contents: read           # To checkout code
  pull-requests: write     # To post summary comment and inline annotations
  checks: write            # To create check runs (for github-pr-check reporter)
```

**Note:** The `pull-requests: write` permission is required for posting the summary comment on PRs and for inline annotations via reviewdog.

## Troubleshooting

### No summary comment or annotations appearing on PR

1. Ensure `pull-requests: write` permission is set
2. Check that files were actually changed in the PR
3. Check the Actions Summary tab for the detailed report

### Action fails to install Vale

- For self-hosted runners, pre-install Vale or ensure package managers (snap/brew) are available
- Check runner logs for specific installation errors

### Vale finds no issues but you expect some

1. Verify the files match the patterns (`.md`, `.adoc`)
2. Check that the files are included in the `files` input or are part of the PR diff
3. If you pushed a new commit, the action only checks files changed in that commit (not all PR changes)
4. Check the Actions Summary for the full report

### Action failed due to errors

This is expected behavior. The action fails when Vale finds errors (not warnings or suggestions). To resolve:

1. Review the inline annotations on the PR
2. Check the summary comment for error counts
3. Fix the errors and push a new commit
4. The action will re-run and pass if no errors remain

### Summary comment is not updating on new commits

The action uses a "sticky" comment that updates in place. If you don't see updates:

1. Check that the PR comment exists (look for "Vale Linting Results")
2. The comment updates automatically on each run
3. If missing, ensure `pull-requests: write` permission is set

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