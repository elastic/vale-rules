[Vale](https://github.com/errata-ai/vale) is an open source prose linter that can check the content of documents in several formats against style guide rules. The goal of a prose linter is automating style guide checks in docs-as-code environments, so that style issues are detected before deploy or while editing documentation in a code editor. 

This repo contains a set of linting rules for Vale based on the Elastic style guide and recommendations.

## Get started

Run the automated installation script:

```bash
curl -fsSL https://raw.githubusercontent.com/elastic/vale-style-guide/main/install-macos.sh | bash
```

This script:

- Verifies you're on macOS.
- Checks for Homebrew installation.
- Installs Vale through Homebrew.
- Configures Vale with the Elastic style guide.
- Downloads the latest style guide package.

## Folder structure

- `.vale.ini` contains the Vale settings. See [Configuration](https://vale.sh/docs/topics/config/).
- `styles/Elastic` contains the Elastic rules for Vale. See [Styles](https://vale.sh/docs/topics/styles/).

## Manual installation from package

Alternatively, you can manually download and install the package:

1. Download the latest `elastic-vale.zip` from the [Releases page](https://github.com/elastic/vale-style-guide/releases).
2. Extract the zip file to your desired location.
3. Point your Vale configuration to the extracted styles folder.

Example `.vale.ini` configuration for manual installation:

```ini
StylesPath = path/to/extracted/styles

[*.{md,adoc}]
BasedOnStyles = Elastic
```

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
