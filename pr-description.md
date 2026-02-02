## Summary

Add `include_paths` input to the lint action, allowing users to filter which paths get linted. This enables teams sharing a docs folder to lint only their owned directories while excluding paths maintained by other teams.

## Changes

- Add `include_paths` input to `lint/action.yml` (optional, defaults to empty).
- Add path filtering step that supports both prefix matching and glob patterns.
- Update README with documentation and usage examples.

## Usage

```yaml
- name: Run Vale Linter
  uses: elastic/vale-rules/lint@main
  with:
    include_paths: "docs/team-a docs/team-b"
```

With glob patterns:

```yaml
- name: Run Vale Linter
  uses: elastic/vale-rules/lint@main
  with:
    include_paths: "docs/guides/** docs/reference/**"
```

## Backward compatibility

This change is fully backward compatible. Existing workflows that don't specify `include_paths` continue to work identically—all changed `.md` and `.adoc` files in the PR are linted as before.

## Test plan

- [ ] Verify existing workflows without `include_paths` work unchanged.
- [ ] Test with simple path prefixes (e.g., `docs/team-a`).
- [ ] Test with glob patterns (e.g., `docs/**/*.md`).
- [ ] Test with multiple paths (space-separated).
- [ ] Verify files outside `include_paths` are excluded from linting.
- [ ] Test edge case where no files match `include_paths` (should skip linting gracefully).
