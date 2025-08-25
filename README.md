[Vale](https://github.com/errata-ai/vale) is an open source prose linter that can check the content of documents in several formats against style guide rules. The goal of a prose linter is automating style guide checks in docs-as-code environments, so that style issues are detected before deploy or while editing documentation in a code editor. 

This repo contains a set of linting rules for Vale based on the Elastic style guide and recommendations.

## Get started

### Quick installation for macOS

Clone the repository and run the automated installation script:

```bash
git clone https://github.com/elastic/elastic-style-guide.git
cd elastic-style-guide
./install-macos.sh
```

The script ensures you always get the latest version of the style guide by updating the repository and performing a clean installation each time it's run.

### Install the VS Code extension

Install the [Vale VSCode](https://marketplace.visualstudio.com/items?itemName=ChrisChinchilla.vale-vscode) extension to see Vale checks when saving a document.

## Folder structure

- `install-macos.sh` - Automated installation script for macOS
- `styles/Elastic/` - Contains the Elastic linting rules for Vale. See [Styles](https://vale.sh/docs/topics/styles/)
- `.github/workflows/` - CI/CD workflows for testing and releases

The installation script creates:
- `~/.vale.ini` - Vale configuration file pointing to the Elastic styles
- `~/Library/Application Support/vale/styles/Elastic/` - Copy of the Elastic style rules

## Updating

To update to the latest style guide rules, re-run the installation script:

```bash
cd elastic-style-guide
./install-macos.sh
```

The script pulls the latest changes and reinstalls everything fresh.

## Creating releases

To create a new release of the Vale package:

1. Update the version and make your changes.
2. Commit and push your changes to the main branch.
3. Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The GitHub workflow automatically:

- Packages the `.vale.ini` file and `styles` folder into `elastic-vale.zip`.
- Creates a new GitHub release with the version tag.
- Uploads the package as a release asset.

## Resources

- [Vale's official documentation](https://vale.sh/docs/vale-cli/overview/)
- [Regex101, a web-based regular expressions editor](https://regex101.com/)

## License

This software is licensed under the Apache License 2.0. Refer to the LICENSE file for details.
