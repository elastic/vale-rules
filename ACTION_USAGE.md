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
```

**Note:** Using `@main` ensures you always get the latest style rules. For stability, you can pin to a specific version tag once releases are available (e.g., `@v1.0.0`).

## Inputs

All inputs are optional:

| Input | Description | Default |
|-------|-------------|---------|
| `files` | Files or directories to lint (space-separated). If not provided, lints changed files in PR. | `''` (empty, uses changed files) |
| `fail_on_error` | Fail the action if Vale finds error-level issues | `false` |
| `vale_version` | Vale version to install | `latest` |
| `debug` | Enable debug output for troubleshooting | `false` |

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

### Fail on error-level issues

```yaml
- uses: elastic/vale-rules@main
  with:
    fail_on_error: true
```

### Enable debug mode

```yaml
- uses: elastic/vale-rules@main
  with:
    debug: true
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
          fail_on_error: false
```

## Supported platforms

The action automatically detects the runner OS and installs Vale accordingly:

- **Ubuntu/Linux**: Uses snap
- **macOS**: Uses Homebrew
- **Self-hosted runners**: Ensure Vale is pre-installed or accessible via package manager

## How it works

1. Validates that required dependencies are available (jq, python3, git)
2. Detects the operating system
3. Installs Vale if not already present
4. Downloads the latest Elastic style guide package from this repository (includes `.vale.ini` configuration and styles)
5. Vale automatically merges the packaged configuration settings (SkippedScopes, IgnoredScopes, TokenIgnores, etc.)
6. Identifies files to lint (changed files in PR or specified files)
7. Creates a temporary directory for intermediate files
8. Gets modified line ranges from git diff
9. Runs Vale on the files with JSON output
10. Filters issues to only those on modified lines using the Python reporter script
11. Generates GitHub Actions annotations for inline diff display
12. Generates a markdown report with collapsible sections organized by severity
13. Posts or updates a sticky comment on the PR with the results
14. Cleans up all temporary files

## Comment format

The action posts a sticky comment on your PR with collapsible sections and clickable line numbers:

```markdown
## Vale Linting Results

**Summary:** 2 errors, 5 warnings, 3 suggestions found

<details>
<summary>❌ Errors (2)</summary>

| File | Line | Rule | Message |
|------|------|------|---------|
| docs/api.md | [45](link) | Elastic.Passive | Use active voice... |
| README.md | [12](link) | Elastic.DontUse | Avoid using... |
</details>

<details>
<summary>⚠️ Warnings (5)</summary>

| File | Line | Rule | Message |
|------|------|------|---------|
| ... | ... | ... | ... |
</details>
```

**Features:**
- Line numbers are clickable links that navigate directly to the issue location in the **PR diff view**
- Links open the Files Changed tab showing the exact line in context
- The comment is automatically updated when you push new commits, so you won't get multiple comments cluttering your PR
- Issues also appear as inline annotations in the Files Changed tab for quick identification
- Error, warning, and suggestion issues are color-coded (red, yellow, blue)

## Permissions required

The action requires the following permissions:

```yaml
permissions:
  contents: read           # To checkout code and read git history
  pull-requests: write     # To post/update PR comments
```

## Troubleshooting

### No comment appearing on PR

1. Ensure `pull-requests: write` permission is set
2. Check that files were actually changed in the PR
3. Verify the changed files are `.md` or `.adoc` files
4. Check the action logs for any errors

### Action fails to install Vale

- For self-hosted runners, pre-install Vale or ensure package managers (snap/brew) are available
- Check runner logs for specific installation errors

### Vale finds no issues but you expect some

1. Verify the files match the patterns (`.md`, `.adoc`)
2. Check that the issues are on lines you actually modified (the action only reports issues on changed lines)
3. Try running Vale locally with the installation scripts to verify

### Action fails when `fail_on_error` is true

The action will fail if error-level Vale issues are found when `fail_on_error: true` is set. This is by design. To pass the check, you need to fix the error-level issues in your documentation.

### Need to debug the action?

Enable debug mode to see detailed execution information:

```yaml
- uses: elastic/vale-rules@main
  with:
    debug: true
```

This will output additional information about:
- Temporary directory creation
- Modified line ranges
- Vale execution
- Issue counts
- File operations

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