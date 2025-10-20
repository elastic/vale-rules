[Vale](https://github.com/errata-ai/vale) is an open source prose linter that can check the content of documents in several formats against style guide rules. The goal of a prose linter is automating style guide checks in docs-as-code environments, so that style issues are detected before deploy or while editing documentation in a code editor. 

This repo contains a set of linting rules for Vale based on the Elastic style guide and recommendations.

## Get started

### Use in GitHub Actions

Add the Elastic Vale linter to your repository's CI/CD pipeline:

```yaml
# .github/workflows/vale-lint.yml
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
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: elastic/vale-rules@main
        with:
          reporter: github-pr-review
```

Refer to [ACTION_USAGE.md](ACTION_USAGE.md) for detailed documentation and examples.

### Local installation

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
.\install-windows.ps1
```

## Install the VS Code extension

Install the [Vale VSCode](https://marketplace.visualstudio.com/items?itemName=ChrisChinchilla.vale-vscode) extension to view Vale checks when saving a document.

## Folder structure

- `action.yml` - GitHub Action definition for using this as a reusable action
- `ACTION_USAGE.md` - Detailed documentation for using the GitHub Action
- `install-macos.sh` - Automated installation script for macOS
- `install-linux.sh` - Automated installation script for Linux
- `install-windows.ps1` - Automated installation script for Windows
- `styles/Elastic/` - Contains the Elastic linting rules for Vale. See [Styles](https://vale.sh/docs/topics/styles/)
- `.github/workflows/` - CI/CD workflows for testing and releases

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

## Creating releases

To create a new release of the Vale package:

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
