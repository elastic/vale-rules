#!/usr/bin/env python3

# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

"""Tests for report/render_report.py — validation, sanitisation, and rendering."""

import hashlib
import json
import os
import sys
import tempfile
import unittest

# Allow importing the module under test from the repo root
sys.path.insert(0, os.path.dirname(__file__))
import render_report  # noqa: E402


def _valid_data(issues=None):
    """Return a minimal valid vale_results.json structure."""
    if issues is None:
        issues = [
            {
                "path": "docs/guide.md",
                "line": 42,
                "rule": "Elastic.Articles",
                "severity": "error",
                "message": "Use 'an' instead of 'a'.",
            }
        ]
    counts = {"error": 0, "warning": 0, "suggestion": 0}
    for issue in issues:
        counts[issue["severity"]] += 1
    return {
        "summary": {
            "errors": counts["error"],
            "warnings": counts["warning"],
            "suggestions": counts["suggestion"],
        },
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

class TestValidation(unittest.TestCase):

    def test_valid_data_passes(self):
        self.assertEqual(render_report.validate(_valid_data()), [])

    def test_empty_issues_passes(self):
        self.assertEqual(render_report.validate(_valid_data(issues=[])), [])

    def test_not_a_dict(self):
        errors = render_report.validate([])
        self.assertTrue(any("root must be an object" in e for e in errors))

    def test_missing_top_level_keys(self):
        errors = render_report.validate({"summary": {"errors": 0, "warnings": 0, "suggestions": 0}})
        self.assertTrue(any("missing top-level keys" in e for e in errors))

    def test_extra_top_level_keys(self):
        data = _valid_data()
        data["extra"] = "bad"
        errors = render_report.validate(data)
        self.assertTrue(any("unexpected top-level keys" in e for e in errors))

    def test_summary_wrong_type(self):
        data = _valid_data()
        data["summary"] = "not a dict"
        errors = render_report.validate(data)
        self.assertTrue(len(errors) > 0)

    def test_summary_wrong_keys(self):
        data = _valid_data(issues=[])
        data["summary"]["extra_key"] = 0
        errors = render_report.validate(data)
        self.assertTrue(any("summary keys" in e for e in errors))

    def test_summary_negative_count(self):
        data = _valid_data(issues=[])
        data["summary"]["errors"] = -1
        errors = render_report.validate(data)
        self.assertTrue(any("non-negative integer" in e for e in errors))

    def test_issues_not_a_list(self):
        data = _valid_data()
        data["issues"] = "not a list"
        errors = render_report.validate(data)
        self.assertTrue(any("must be a list" in e for e in errors))

    def test_too_many_issues(self):
        issues = [
            {"path": "f.md", "line": 1, "rule": "R.X", "severity": "error", "message": "m"}
            for _ in range(1001)
        ]
        data = _valid_data(issues=issues)
        errors = render_report.validate(data)
        self.assertTrue(any("too many issues" in e for e in errors))

    def test_issue_wrong_keys(self):
        data = _valid_data()
        data["issues"][0]["extra"] = "bad"
        errors = render_report.validate(data)
        self.assertTrue(any("keys must be exactly" in e for e in errors))

    def test_path_too_long(self):
        data = _valid_data()
        data["issues"][0]["path"] = "a" * 257
        errors = render_report.validate(data)
        self.assertTrue(any("path" in e for e in errors))

    def test_path_null_byte(self):
        data = _valid_data()
        data["issues"][0]["path"] = "docs/\x00evil.md"
        errors = render_report.validate(data)
        self.assertTrue(any("null byte" in e for e in errors))

    def test_path_traversal(self):
        data = _valid_data()
        data["issues"][0]["path"] = "../../etc/passwd"
        errors = render_report.validate(data)
        self.assertTrue(any("traversal" in e for e in errors))

    def test_line_zero(self):
        data = _valid_data()
        data["issues"][0]["line"] = 0
        errors = render_report.validate(data)
        self.assertTrue(any("positive integer" in e for e in errors))

    def test_line_negative(self):
        data = _valid_data()
        data["issues"][0]["line"] = -5
        errors = render_report.validate(data)
        self.assertTrue(any("positive integer" in e for e in errors))

    def test_rule_invalid_chars(self):
        data = _valid_data()
        data["issues"][0]["rule"] = "; rm -rf /"
        errors = render_report.validate(data)
        self.assertTrue(any("invalid characters" in e for e in errors))

    def test_rule_too_long(self):
        data = _valid_data()
        data["issues"][0]["rule"] = "A" * 129
        errors = render_report.validate(data)
        self.assertTrue(any("rule" in e for e in errors))

    def test_invalid_severity(self):
        data = _valid_data()
        data["issues"][0]["severity"] = "critical"
        # Fix summary to avoid double error
        data["summary"]["errors"] = 0
        errors = render_report.validate(data)
        self.assertTrue(any("severity" in e for e in errors))

    def test_message_too_long(self):
        data = _valid_data()
        data["issues"][0]["message"] = "x" * 513
        errors = render_report.validate(data)
        self.assertTrue(any("message" in e for e in errors))

    def test_summary_count_mismatch(self):
        data = _valid_data()
        data["summary"]["errors"] = 999
        errors = render_report.validate(data)
        self.assertTrue(any("summary.errors" in e for e in errors))


# ---------------------------------------------------------------------------
# Sanitisation tests
# ---------------------------------------------------------------------------

class TestSanitisation(unittest.TestCase):

    def test_html_stripped(self):
        self.assertEqual(
            render_report.sanitize_text('<script>alert(1)</script>'),
            "alert1"
        )

    def test_markdown_link_stripped(self):
        self.assertEqual(
            render_report.sanitize_text('[click here](https://evil.com)'),
            "click here"
        )

    def test_bare_url_stripped(self):
        result = render_report.sanitize_text('visit https://evil.com now')
        self.assertNotIn("https://", result)

    def test_pipe_escaped(self):
        result = render_report.sanitize_text('a | b')
        self.assertEqual(result, 'a \\| b')

    def test_injection_chars_removed(self):
        result = render_report.sanitize_text('![img](x) <div>')
        self.assertNotIn('<', result)
        self.assertNotIn('>', result)
        self.assertNotIn('[', result)
        self.assertNotIn(']', result)
        self.assertNotIn('(', result)
        self.assertNotIn(')', result)

    def test_path_preserves_slashes(self):
        result = render_report.sanitize_path('docs/team-a/guide.md')
        self.assertEqual(result, 'docs/team-a/guide.md')

    def test_path_strips_html(self):
        result = render_report.sanitize_path('docs/<b>evil</b>.md')
        self.assertEqual(result, 'docs/evil.md')


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------

class TestRendering(unittest.TestCase):

    def test_empty_issues_no_issues_found(self):
        data = _valid_data(issues=[])
        report = render_report.render(data, "owner/repo", "1")
        self.assertIn("No issues found", report)
        self.assertIn("Vale Linting Results", report)

    def test_single_error_renders(self):
        data = _valid_data()
        report = render_report.render(data, "owner/repo", "1")
        self.assertIn("1 error found", report)
        self.assertIn("docs/guide.md", report)
        self.assertIn("Elastic.Articles", report)
        self.assertIn("<details>", report)

    def test_multiple_severities(self):
        issues = [
            {"path": "a.md", "line": 1, "rule": "Elastic.A", "severity": "error", "message": "err"},
            {"path": "b.md", "line": 2, "rule": "Elastic.B", "severity": "warning", "message": "warn"},
            {"path": "c.md", "line": 3, "rule": "Elastic.C", "severity": "suggestion", "message": "sug"},
        ]
        data = _valid_data(issues=issues)
        report = render_report.render(data, "owner/repo", "1")
        self.assertIn("1 error", report)
        self.assertIn("1 warning", report)
        self.assertIn("1 suggestion", report)
        self.assertIn("Errors", report)
        self.assertIn("Warnings", report)
        self.assertIn("Suggestions", report)

    def test_diff_link_generated(self):
        data = _valid_data()
        report = render_report.render(data, "owner/repo", "42")
        expected_hash = hashlib.sha256("docs/guide.md".encode()).hexdigest()
        self.assertIn(f"diff-{expected_hash}R42", report)

    def test_no_link_without_pr(self):
        data = _valid_data()
        report = render_report.render(data, "", "")
        self.assertNotIn("https://github.com", report)
        self.assertIn("| 42 |", report)

    def test_html_in_message_sanitised_in_render(self):
        issues = [
            {
                "path": "f.md",
                "line": 1,
                "rule": "Elastic.X",
                "severity": "error",
                "message": '<img src=x onerror="alert(1)">',
            }
        ]
        data = _valid_data(issues=issues)
        report = render_report.render(data, "", "")
        self.assertNotIn("<img", report)
        self.assertNotIn("onerror", report)

    def test_footer_included(self):
        data = _valid_data(issues=[])
        report = render_report.render(data, "", "")
        self.assertIn("Elastic Docs style guide", report)

    def test_diff_hash_matches_lint_algorithm(self):
        """Verify our diff hash matches the algorithm in lint/vale_reporter.py."""
        path = "docs/guide.md"
        normalized = path.lstrip('./')
        expected = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        self.assertEqual(render_report.generate_diff_hash(path), expected)

        path_dotslash = "./docs/guide.md"
        self.assertEqual(render_report.generate_diff_hash(path_dotslash), expected)


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

class TestCLI(unittest.TestCase):

    def test_valid_json_produces_output(self):
        data = _valid_data()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as inp:
            json.dump(data, inp)
            inp_path = inp.name
        out_path = inp_path + ".md"
        try:
            rc = render_report.main.__wrapped__(inp_path, out_path, "owner/repo", "1") if hasattr(render_report.main, '__wrapped__') else None
            # Fall back to calling via subprocess-like approach using argparse
            sys.argv = ["render_report.py", "--input", inp_path, "--output", out_path, "--repo", "owner/repo", "--pr", "1"]
            rc = render_report.main()
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.exists(out_path))
            with open(out_path) as f:
                content = f.read()
            self.assertIn("Vale Linting Results", content)
        finally:
            os.unlink(inp_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_invalid_json_returns_nonzero(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as inp:
            inp.write("not json")
            inp_path = inp.name
        out_path = inp_path + ".md"
        try:
            sys.argv = ["render_report.py", "--input", inp_path, "--output", out_path]
            rc = render_report.main()
            self.assertEqual(rc, 1)
            self.assertFalse(os.path.exists(out_path))
        finally:
            os.unlink(inp_path)

    def test_oversized_file_rejected(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as inp:
            # Write > 100KB
            inp.write(" " * (render_report.MAX_FILE_SIZE + 1))
            inp_path = inp.name
        out_path = inp_path + ".md"
        try:
            sys.argv = ["render_report.py", "--input", inp_path, "--output", out_path]
            rc = render_report.main()
            self.assertEqual(rc, 1)
        finally:
            os.unlink(inp_path)

    def test_symlink_input_rejected(self):
        """Refuse to read input if it is a symlink."""
        # Create a real file, then symlink to it
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as real:
            json.dump(_valid_data(), real)
            real_path = real.name
        link_path = real_path + ".link"
        os.symlink(real_path, link_path)
        out_path = real_path + ".md"
        try:
            sys.argv = ["render_report.py", "--input", link_path, "--output", out_path]
            rc = render_report.main()
            self.assertEqual(rc, 1)
            self.assertFalse(os.path.exists(out_path))
        finally:
            os.unlink(link_path)
            os.unlink(real_path)

    def test_symlink_output_rejected(self):
        """Refuse to write output if the path is already a symlink."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as inp:
            json.dump(_valid_data(), inp)
            inp_path = inp.name
        # Create a symlink where the output would go
        target_path = inp_path + ".target"
        link_path = inp_path + ".md"
        with open(target_path, 'w') as f:
            f.write("")
        os.symlink(target_path, link_path)
        try:
            sys.argv = ["render_report.py", "--input", inp_path, "--output", link_path]
            rc = render_report.main()
            self.assertEqual(rc, 1)
        finally:
            os.unlink(link_path)
            os.unlink(target_path)
            os.unlink(inp_path)

    def test_schema_violation_returns_nonzero(self):
        data = _valid_data()
        data["extra_key"] = "bad"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as inp:
            json.dump(data, inp)
            inp_path = inp.name
        out_path = inp_path + ".md"
        try:
            sys.argv = ["render_report.py", "--input", inp_path, "--output", out_path]
            rc = render_report.main()
            self.assertEqual(rc, 1)
        finally:
            os.unlink(inp_path)
            if os.path.exists(out_path):
                os.unlink(out_path)


if __name__ == '__main__':
    unittest.main()
