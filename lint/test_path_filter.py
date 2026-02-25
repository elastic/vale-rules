#!/usr/bin/env python3

# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

"""Tests for path_filter.py."""

import unittest

from path_filter import filter_files, matches_pattern, parse_patterns


class TestParsePatterns(unittest.TestCase):
    def test_simple_paths(self):
        includes, excludes = parse_patterns("docs/team-a docs/team-b")
        assert includes == ["docs/team-a", "docs/team-b"]
        assert excludes == []

    def test_multiline(self):
        includes, excludes = parse_patterns("docs/team-a\ndocs/team-b")
        assert includes == ["docs/team-a", "docs/team-b"]
        assert excludes == []

    def test_negation(self):
        includes, excludes = parse_patterns(
            "docs/reference/**\n!docs/reference/query-languages/esql/**"
        )
        assert includes == ["docs/reference/**"]
        assert excludes == ["docs/reference/query-languages/esql/**"]

    def test_mixed_negation_and_includes(self):
        includes, excludes = parse_patterns(
            "docs/** !docs/internal/** src/**"
        )
        assert includes == ["docs/**", "src/**"]
        assert excludes == ["docs/internal/**"]

    def test_trailing_slashes_stripped(self):
        includes, excludes = parse_patterns("docs/team-a/ !docs/team-b/")
        assert includes == ["docs/team-a"]
        assert excludes == ["docs/team-b"]

    def test_empty_input(self):
        includes, excludes = parse_patterns("")
        assert includes == []
        assert excludes == []

    def test_bare_negation_ignored(self):
        includes, excludes = parse_patterns("docs/** !")
        assert includes == ["docs/**"]
        assert excludes == []


class TestMatchesPattern(unittest.TestCase):
    def test_glob_match(self):
        assert matches_pattern("docs/reference/api.md", "docs/reference/**")

    def test_prefix_match(self):
        assert matches_pattern("docs/team-a/guide.md", "docs/team-a")

    def test_no_match(self):
        assert not matches_pattern("src/main.py", "docs/**")

    def test_exact_match(self):
        assert matches_pattern("README.md", "README.md")


class TestFilterFiles(unittest.TestCase):
    FILES = [
        "docs/reference/api.md",
        "docs/reference/setup.md",
        "docs/reference/query-languages/esql/overview.md",
        "docs/reference/query-languages/esql/syntax.md",
        "docs/reference/query-languages/kql/overview.md",
        "docs/guides/getting-started.md",
        "src/main.py",
    ]

    def test_include_only(self):
        result = filter_files(self.FILES, ["docs/reference/**"])
        assert result == [
            "docs/reference/api.md",
            "docs/reference/setup.md",
            "docs/reference/query-languages/esql/overview.md",
            "docs/reference/query-languages/esql/syntax.md",
            "docs/reference/query-languages/kql/overview.md",
        ]

    def test_include_with_exclusion(self):
        result = filter_files(
            self.FILES,
            ["docs/reference/**"],
            ["docs/reference/query-languages/esql/**"],
        )
        assert result == [
            "docs/reference/api.md",
            "docs/reference/setup.md",
            "docs/reference/query-languages/kql/overview.md",
        ]

    def test_multiple_excludes(self):
        result = filter_files(
            self.FILES,
            ["docs/**"],
            ["docs/reference/query-languages/esql/**", "docs/guides/**"],
        )
        assert result == [
            "docs/reference/api.md",
            "docs/reference/setup.md",
            "docs/reference/query-languages/kql/overview.md",
        ]

    def test_exclude_without_includes_returns_nothing(self):
        result = filter_files(self.FILES, [], ["docs/**"])
        assert result == []

    def test_no_excludes(self):
        result = filter_files(self.FILES, ["docs/guides/**"], [])
        assert result == ["docs/guides/getting-started.md"]

    def test_exclude_none(self):
        result = filter_files(self.FILES, ["docs/guides/**"])
        assert result == ["docs/guides/getting-started.md"]

    def test_prefix_include_with_glob_exclude(self):
        result = filter_files(
            self.FILES,
            ["docs/reference"],
            ["docs/reference/query-languages/**"],
        )
        assert result == [
            "docs/reference/api.md",
            "docs/reference/setup.md",
        ]


if __name__ == "__main__":
    unittest.main()
