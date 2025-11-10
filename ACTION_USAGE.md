# Using the Elastic Vale Action

This repository provides a reusable GitHub Action that can be used by any Elastic repository to lint documentation files with Vale using the Elastic style guide.

## Quick start linting

This action uses a two-workflow setup that supports **fork PRs** safely by separating linting from commenting. It follows the pattern recommended by [test-reporter](https://github.com/marketplace/actions/test-reporter#recommended-setup-for-public-repositories).

### Step 1: Create the linting workflow

Create `.github/workflows/vale-lint.yml`:

```yaml
name: Vale Documentation Linting

on:
  pull_request:
    paths:
      - '**.md'
      - '**.adoc'

permissions:
  contents: read

jobs:
  vale:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v5
        with:
          fetch-depth: 0
      
      - name: Run Vale Linter
        uses: elastic/vale-rules/lint@main
```

### Step 2: Create the reporting workflow

Create `.github/workflows/vale-report.yml`:

```yaml
name: Vale Report

on:
  workflow_run:
    workflows: ["Vale Documentation Linting"]
    types:
      - completed

permissions:
  pull-requests: read

jobs:
  report:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.event == 'pull_request'
    permissions:
      pull-requests: write
    
    steps:
      - name: Post Vale Results
        uses: elastic/vale-rules/report@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### Why two workflows?

- **Security**: The linting workflow runs on `pull_request` (including forks) but only reads code - it never executes untrusted code.
- **Permissions**: The reporting workflow runs on `workflow_run` in the base repository's context, so it has write permissions to post comments.
- **Fork support**: Fork contributors get the same experience as internal contributors - linting results appear as PR comments.

**Note:** Using `@main` ensures you always get the latest style rules. For stability, you can pin to a specific version tag (e.g., `@v1.0.0`).

## Inputs

### lint/action.yml (Linting workflow)

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `files` | Files or directories to lint (space-separated). If not provided, lints changed files in PR. | No | `''` (empty, uses changed files) |
| `fail_on_error` | Fail the action if Vale finds error-level issues | No | `false` |
| `vale_version` | Vale version to install | No | `latest` |
| `debug` | Enable debug output for troubleshooting | No | `false` |

### report/action.yml (Reporting workflow)

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github_token` | GitHub token for posting PR comments | **Yes** | N/A |

## Examples

### Basic usage (lint changed files in PR)

**Linting workflow:**
```yaml
- uses: elastic/vale-rules/lint@main
```

**Reporting workflow:**
```yaml
- uses: elastic/vale-rules/report@main
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

### Lint specific files or directories

```yaml
- uses: elastic/vale-rules/lint@main
  with:
    files: 'docs/ README.md'
```

### Fail on error-level issues

```yaml
- uses: elastic/vale-rules/lint@main
  with:
    fail_on_error: true
```

### Enable debug mode

```yaml
- uses: elastic/vale-rules/lint@main
  with:
    debug: true
```

## Complete example

**Linting workflow (`.github/workflows/vale-lint.yml`):**
```yaml
name: Vale Documentation Linting

on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - '**.md'
      - '**.adoc'
      - 'docs/**'

permissions:
  contents: read

jobs:
  vale-lint:
    name: Lint Documentation
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v5
        with:
          fetch-depth: 0  # Required for proper diff analysis
      
      - name: Run Vale with Elastic style guide
        uses: elastic/vale-rules/lint@main
        with:
          fail_on_error: false
          debug: false
```

**Reporting workflow (`.github/workflows/vale-report.yml`):**
```yaml
name: Vale Report

on:
  workflow_run:
    workflows: ["Vale Documentation Linting"]
    types:
      - completed

permissions:
  pull-requests: read

jobs:
  report:
    name: Post Results
    runs-on: ubuntu-latest
    if: github.event.workflow_run.event == 'pull_request'
    permissions:
      pull-requests: write
    
    steps:
      - name: Post Vale Results as PR Comment
        uses: elastic/vale-rules/report@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Supported platforms

The action automatically detects the runner OS and installs Vale accordingly:

- **Ubuntu/Linux**: Uses snap
- **macOS**: Uses Homebrew
- **Self-hosted runners**: Ensure Vale is pre-installed or accessible via package manager

## How it works

### Linting workflow (lint/action.yml)

1. Validates that required dependencies are available (jq, python3, git).
2. Detects the operating system.
3. Installs Vale if not already present.
4. Downloads the latest Elastic style guide package from this repository (includes `.vale.ini` configuration and styles).
5. Vale automatically merges the packaged configuration settings (SkippedScopes, IgnoredScopes, TokenIgnores, etc.).
6. Identifies files to lint (changed files in PR or specified files).
7. Creates a temporary directory for intermediate files.
8. Gets modified line ranges from git diff.
9. Runs Vale on the files with JSON output.
10. Filters issues to only those on modified lines using the Python reporter script.
11. Generates GitHub Actions annotations for inline diff display.
12. Generates a markdown report with collapsible sections organized by severity.
13. **Uploads the report as an artifact** (available for 1 day).
14. Cleans up all temporary files.

### Reporting workflow (report/action.yml)

1. Downloads the Vale results artifact from the linting workflow.
2. Posts or updates a sticky comment on the PR with the results.
3. Cleans up downloaded artifacts.

This separation ensures that:
- The linting workflow runs safely on fork PRs (no write permissions needed).
- The reporting workflow runs in the base repository's context (has write permissions).
- Fork contributors see the same results as internal contributors.

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

### Linting workflow

```yaml
permissions:
  contents: read  # To checkout code and read git history
```

### Reporting workflow

```yaml
permissions:
  pull-requests: read  # Workflow-level (minimal)

jobs:
  report:
    permissions:
      pull-requests: write  # Job-level (only where needed)
```

By separating permissions and granting write access only at the job level, we follow the principle of least privilege while ensuring fork PRs can be linted safely.

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
- uses: elastic/vale-rules/lint@v1.0.0  # Pin to specific version
- uses: elastic/vale-rules/lint@v1      # Pin to v1.x.x
- uses: elastic/vale-rules/lint@main    # Use latest (not recommended for production)
```

Apply the same versioning to both lint and report actions.

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