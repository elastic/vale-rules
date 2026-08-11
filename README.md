[Vale](https://github.com/errata-ai/vale) is an open source prose linter that can check the content of documents in several formats against style guide rules. The goal of a prose linter is automating style guide checks in docs-as-code environments, so that style issues are detected before deploy or while editing documentation in a code editor. 

This repo contains a set of linting rules for Vale based on the Elastic style guide and recommendations.

## Get started

Run these commands to install the Elastic style guide locally:

**macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/elastic/vale-rules/main/install-macos.sh | bash
```

**Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/elastic/vale-rules/main/install-linux.sh | bash
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/elastic/vale-rules/main/install-windows.ps1 -OutFile install-windows.ps1
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1
```

### Installer options

The macOS installer supports the following flags:

| Flag | Description |
|------|-------------|
| `--enable-spelling` | Enable the experimental `Elastic.Spelling` rule. |
| `--help` | Show usage information. |

For example, to install with spelling checks enabled:

```bash
curl -fsSL https://raw.githubusercontent.com/elastic/vale-rules/main/install-macos.sh | bash -s -- --enable-spelling
```

## Install the VS Code extension

Install the [Vale VSCode](https://marketplace.visualstudio.com/items?itemName=ChrisChinchilla.vale-vscode) extension to view Vale checks when saving a document.

## Use Vale in GitHub Actions

The reusable GitHub Actions for running Vale and posting pull request comments live in [`elastic/docs-actions`](https://github.com/elastic/docs-actions):

```yaml
- uses: elastic/docs-actions/vale/lint@v1
```

```yaml
- uses: elastic/docs-actions/vale/report@v1
```

This repository only publishes the Vale rules package that those actions download and use. The packaged configuration applies Elastic rules to Markdown and MDX files by default.

### Per-repo rule overrides

You can customize which Vale rules are enabled, disabled, or set to a different severity on a per-repo basis. Add a `.vale-overrides.ini` file to your repository root (or `.github/.vale-overrides.ini`):

```ini
Elastic.Spelling = YES
Elastic.We = suggestion
```

The lint action automatically detects this file and merges it into the Vale configuration. For existing keys, values are replaced in place. For new keys, they are inserted into the first file-type section. Section headers are ignored, except for constrained YAML sections such as `[*.{yml,yaml}]`, which can opt a repository into linting YAML files with the packaged Elastic rules.

### Filtering specific paths

Use `vale-paths` to limit linting to specific directories. This is useful when multiple teams share a docs folder:

```yaml
- name: Run Vale Linter
  uses: elastic/docs-actions/vale/lint@v1
  with:
    vale-paths: |
      docs/team-a
      docs/team-b
```

With glob patterns:

```yaml
- name: Run Vale Linter
  uses: elastic/docs-actions/vale/lint@v1
  with:
    vale-paths: |
      docs/guides/**
      docs/reference/**
```

With negation patterns to exclude specific subdirectories:

```yaml
- name: Run Vale Linter
  uses: elastic/docs-actions/vale/lint@v1
  with:
    vale-paths: |
      docs/reference/**
      !docs/reference/query-languages/esql/**
```

Space-separated format is also supported: `vale-paths: "docs/team-a docs/team-b"`

> **Note:** The `include-paths` input still works but is deprecated. Use `vale-paths` instead for consistency with `docs-actions` workflows.

## Spelling rule (experimental)

The `Elastic.Spelling` rule checks documentation for misspellings using Vale's built-in Hunspell-based spell checker with the American English dictionary. It is **disabled by default** and can be enabled per repo or per local installation.

The rule includes regex filters to reduce false positives common in technical documentation (camelCase identifiers, uppercase acronyms, CLI flags, file extensions, underscore-prefixed Elasticsearch fields, and more). Three vocabulary files provide additional accepted terms:

- **ElasticTerms** — Elastic product names, features, and abbreviations.
- **ThirdPartyProducts** — Vendor names, third-party tools, and integrations.
- **TechJargon** — Generic computing, networking, and development terms.

### Enable spelling in CI

Add a `.vale-overrides.ini` to your repository root:

```ini
Elastic.Spelling = YES
```

The lint action picks this up automatically. No workflow changes are needed.

### Enable spelling locally

Pass the `--enable-spelling` flag when installing or updating:

```bash
# macOS
curl -fsSL https://raw.githubusercontent.com/elastic/vale-rules/main/install-macos.sh | bash -s -- --enable-spelling
```

Or add the override manually to your local Vale config:

```ini
[*.{md,mdx}]
Elastic.Spelling = YES
```

## Folder structure

- `install-macos.sh` - Automated installation script for macOS.
- `install-linux.sh` - Automated installation script for Linux.
- `install-windows.ps1` - Automated installation script for Windows.
- `styles/Elastic/` - Elastic linting rules for Vale. See [Styles](https://vale.sh/docs/topics/styles/).
- `styles/config/vocabularies/` - Vocabulary files for accepted terms (ElasticTerms, ThirdPartyProducts, and TechJargon).
- `.github/workflows/` - CI/CD workflows for testing and releases.

The installation scripts create Vale configurations at platform-specific locations:

**macOS:**
- `~/Library/Application Support/vale/.vale.ini` - Vale configuration file
- `~/Library/Application Support/vale/styles/Elastic/` - Elastic style rules

**Linux:**
- `~/.config/vale/.vale.ini` - Vale configuration file
- `~/.local/share/vale/styles/Elastic/` - Elastic style rules

**Windows:**
- `%LOCALAPPDATA%\vale\.vale.ini` - Vale configuration file
- `%LOCALAPPDATA%\vale\styles\Elastic\` - Elastic style rules

## Updating

To update to the latest style guide rules, rerun the installation script.

## Testing locally

You can test Vale rules locally without creating a release. This is useful for developing and testing new rules or modifications to existing ones.

### Prerequisites

1. Install Vale on your system (use the installation scripts above, or install directly from [Vale's installation guide](https://vale.sh/docs/vale-cli/installation/)).
2. Clone this repository.

### Testing workflow

The repository includes a `.vale.ini` configuration file at the root that points to the local `styles/` directory:

```bash
# Navigate to the repository
cd /path/to/elastic-style-guide

# Create a test Markdown file
echo "This uses eg, instead of for example." > test.md

# Run Vale using the local configuration
vale --config=.vale.ini --no-global test.md
```

Vale immediately uses the rules from the local `styles/Elastic/` directory. Any changes you make to rule files are reflected instantly without needing to create a release.

### Testing rule changes

1. Edit any rule file in `styles/Elastic/`:

```bash
# Example: modify the Latinisms rule
vim styles/Elastic/Latinisms.yml
```

2. Run Vale against a test file:

```bash
vale --config=.vale.ini --no-global your-test-file.md
```

3. Iterate on your changes until the rule works as expected.

The local `.vale.ini` configuration uses `StylesPath = styles`, which points directly to the local directory, so there's no need for releases or package syncing during development.

### Running regression tests

Run the focused regression tests before changing rule matching behavior:

```bash
python3 rule-tests/run_rule_tests.py
```

These tests assert exact matches for rules with known false-positive risks.

### Rule authoring guidance

Use rule messages to explain the issue and the next action. Prefer messages that name the matched term with `%s`, suggest a replacement when one is available, and explain context for rules that require judgment.

Use severity levels consistently:

- Use `error` only for content that is structurally broken or unsafe to ship, such as conflict markers.
- Use `warning` for high-confidence issues with a clear fix, such as spelling, accessibility terms, or blocked word choices.
- Use `suggestion` for style guidance, tone guidance, or context-dependent advice.

## Creating releases

To create a new release of the Vale package, you have two options:

### Option 1: manual workflow dispatch (recommended)

1. Go to the [Actions tab](https://github.com/elastic/vale-rules/actions/workflows/release.yml) in GitHub
2. Click "Run workflow"
3. Enter the version number (e.g., `v1.0.1`)
4. Click "Run workflow"

The GitHub workflow will automatically:
- Create and push a git tag with the specified version
- Add a VERSION file to the Elastic style directory
- Package the `.vale.ini` and `styles/` folder into `elastic-vale.zip` (a Vale complete package)
- Create a new GitHub release with the version tag
- Upload the package as a release asset

### Option 2: push a tag manually

1. Update the version and make your changes.
2. Commit and push your changes to the main branch.
3. Create and push a version tag:

```bash
git tag v1.0.1
git push origin v1.0.1
```

The GitHub workflow automatically:

- Adds a VERSION file to the Elastic style directory.
- Packages the `.vale.ini` and `styles/` folder into `elastic-vale.zip` (a Vale complete package).
- Creates a new GitHub release with the version tag.
- Uploads the package as a release asset.

Users can then install or update to this version using the installation scripts or by running `vale sync`. The packaged `.vale.ini` ensures everyone gets the same configuration settings (SkippedScopes, IgnoredScopes, TokenIgnores, etc.).

## Resources

- [Vale's official documentation](https://vale.sh/docs/vale-cli/overview/)
- [Regex101, a web-based regular expressions editor](https://regex101.com/)

## License

This software is licensed under the Apache License 2.0. Refer to the LICENSE file for details.
