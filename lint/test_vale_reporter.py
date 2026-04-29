#!/usr/bin/env python3

# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

"""Tests for lint/vale_reporter.py — sanitisation functions."""

import os
import sys
import unittest

# Allow importing the module under test
sys.path.insert(0, os.path.dirname(__file__))
import vale_reporter  # noqa: E402


class TestSanitizeAnnotation(unittest.TestCase):
    """Tests for sanitize_annotation() — strips workflow command sequences."""

    def test_strips_double_colon(self):
        self.assertEqual(
            vale_reporter.sanitize_annotation("text ::set-env name=X::Y"),
            "text  set-env name=X Y",
        )

    def test_strips_newlines(self):
        self.assertEqual(
            vale_reporter.sanitize_annotation("line1\nline2\rline3"),
            "line1 line2 line3",
        )

    def test_preserves_normal_text(self):
        msg = "Use 'Elasticsearch' instead of 'elasticsearch'"
        self.assertEqual(vale_reporter.sanitize_annotation(msg), msg)

    def test_coerces_non_string(self):
        self.assertEqual(vale_reporter.sanitize_annotation(42), "42")

    def test_combined_injection(self):
        payload = "bad\n::error::injected message"
        result = vale_reporter.sanitize_annotation(payload)
        self.assertNotIn("::", result)
        self.assertNotIn("\n", result)


class TestSanitizeText(unittest.TestCase):
    """Tests for sanitize_text() — strips HTML, links, and injection chars."""

    def test_strips_html_tags(self):
        self.assertEqual(
            vale_reporter.sanitize_text("<script>alert(1)</script>"),
            "alert1",
        )

    def test_strips_markdown_links(self):
        self.assertEqual(
            vale_reporter.sanitize_text("[click here](https://evil.com)"),
            "click here",
        )

    def test_strips_bare_urls(self):
        self.assertEqual(
            vale_reporter.sanitize_text("visit https://evil.com for info"),
            "visit  for info",
        )

    def test_escapes_pipe(self):
        self.assertEqual(
            vale_reporter.sanitize_text("col1 | col2"),
            "col1 \\| col2",
        )

    def test_preserves_normal_message(self):
        msg = "Use 'Elasticsearch' instead of 'elasticsearch'."
        self.assertEqual(vale_reporter.sanitize_text(msg), msg)


class TestSanitizePath(unittest.TestCase):
    """Tests for sanitize_path() — sanitizes paths while preserving slashes."""

    def test_preserves_normal_path(self):
        self.assertEqual(
            vale_reporter.sanitize_path("docs/guide.md"),
            "docs/guide.md",
        )

    def test_strips_html_in_path(self):
        self.assertEqual(
            vale_reporter.sanitize_path("docs/<img src=x>.md"),
            "docs/.md",
        )

    def test_escapes_pipe_in_path(self):
        self.assertEqual(
            vale_reporter.sanitize_path("docs/a|b.md"),
            "docs/a\\|b.md",
        )

    def test_strips_injection_chars(self):
        self.assertEqual(
            vale_reporter.sanitize_path("docs/[evil](url).md"),
            "docs/evilurl.md",
        )


if __name__ == "__main__":
    unittest.main()
