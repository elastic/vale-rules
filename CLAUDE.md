# Development notes

## Testing local rule changes

When modifying Vale rules in this repo, use the `--no-global` flag to ensure Vale uses the local `styles/` directory instead of the globally installed rules:

```bash
vale --config .vale.ini --no-global <file>
```

Without this flag, Vale may load rules from `~/Library/Application Support/vale/styles/Elastic/` (macOS) instead of your local changes.

## Rule file format

Vale rules use YAML. Key rule types in this repo:

- **`conditional`** — Checks that when pattern A appears, pattern B must also exist (e.g., acronym definitions).
- **`existence`** — Flags matches of a pattern (e.g., banned words).
- **`substitution`** — Suggests replacements for matched patterns.
- **`consistency`** — Ensures consistent usage between two alternatives.

## Releasing

Releases can be created in two ways:

### Option 1: Manual workflow dispatch (recommended)

1. Go to the [Actions tab](https://github.com/elastic/vale-rules/actions/workflows/release.yml) in GitHub
2. Click "Run workflow"
3. Enter the version number (e.g., `v1.0.x`)
4. Click "Run workflow"

The workflow will create the tag and release automatically.

### Option 2: Push a tag manually

```bash
git tag v1.0.x
git push origin v1.0.x
```

The GitHub Actions workflow creates a release with the `elastic-vale.zip` package.

