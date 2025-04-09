[Vale](https://github.com/errata-ai/vale) is an open source prose linter that can check the content of documents in several formats against style guide rules. The goal of a prose linter is automating style guide checks in docs-as-code environments, so that style issues are detected before deploy or while editing documentation in a code editor. 

This repo contains a set of linting rules for Vale based on the Elastic style guide and recommendations.

# Get started

1. Clone the repository in your home directory.
2. Add this line to your `.zshrc` file: `export VALE_CONFIG_PATH=~/elastic-style-guide/.vale.ini`.
3. Install Vale with `brew install vale` on macOS. See [Installation](https://vale.sh/docs/vale-cli/installation/).
4. Install the [Vale add-on for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ChrisChinchilla.vale-vscode).
5. Restart Visual Studio Code.

# Folder structure

- `.vale.ini` contains the Vale settings. See [Configuration](https://vale.sh/docs/topics/config/).
- `styles/Elastic` contains the Elastic rules for Vale. See [Styles](https://vale.sh/docs/topics/styles/).

# Use as a git submodule

To use the contents of this repository as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules), run the following git commands from the target repo:

```bash
git submodule add git@github.com:elastic/vale-style-guide.git
git submodule update --init --recursive
git commit -m "Added the Vale submodule to the project."
git push
```

Copy the sample `.vale.ini` file to the root of your repository, and change the path to point to the submodule:

```ini
StylesPath = vale/styles
```

To update the submodule, run the following git command from the root folder of the repository:

```
git submodule update --remote --merge
```

# Resources

- [Vale's official documentation](https://vale.sh/docs/vale-cli/overview/)
- [Regex101, a web-based regular expressions editor](https://regex101.com/)

# License

This software is licensed under the Apache License 2.0. Details can be found in the file LICENSE.
