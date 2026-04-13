#!/usr/bin/env python3

# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

"""Tests for lint/run_vale.py."""

import tempfile
import unittest
from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import run_vale


class TestLoadFiles(unittest.TestCase):

    def test_load_files_deduplicates_and_preserves_order(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("a.md\n\nb.md\na.md\n")
            tmp_path = tmp.name
        try:
            self.assertEqual(run_vale.load_files(tmp_path), ["a.md", "b.md"])
        finally:
            Path(tmp_path).unlink()


class TestChunkFiles(unittest.TestCase):

    def test_chunks_by_max_files(self):
        files = [f"doc-{i}.md" for i in range(5)]
        chunks = run_vale.chunk_files(files, max_files_per_batch=2, max_arg_chars=1000)
        self.assertEqual(chunks, [["doc-0.md", "doc-1.md"], ["doc-2.md", "doc-3.md"], ["doc-4.md"]])

    def test_chunks_by_arg_length(self):
        files = ["a" * 8, "b" * 8, "c" * 8]
        chunks = run_vale.chunk_files(files, max_files_per_batch=10, max_arg_chars=18)
        self.assertEqual(chunks, [["a" * 8, "b" * 8], ["c" * 8]])

    def test_rejects_invalid_limits(self):
        with self.assertRaises(ValueError):
            run_vale.chunk_files(["a.md"], max_files_per_batch=0)
        with self.assertRaises(ValueError):
            run_vale.chunk_files(["a.md"], max_arg_chars=0)


class TestMergeValeOutput(unittest.TestCase):

    def test_merges_issue_lists_per_file(self):
        merged = {"docs/a.md": [{"Check": "One"}]}
        batch = {
            "docs/a.md": [{"Check": "Two"}],
            "docs/b.md": [{"Check": "Three"}],
        }
        result = run_vale.merge_vale_output(merged, batch)
        self.assertEqual(
            result,
            {
                "docs/a.md": [{"Check": "One"}, {"Check": "Two"}],
                "docs/b.md": [{"Check": "Three"}],
            },
        )


if __name__ == "__main__":
    unittest.main()
