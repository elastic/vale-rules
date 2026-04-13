#!/usr/bin/env python3

# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

"""
Run Vale in bounded batches and merge JSON output.

This avoids "argument list too long" failures when a PR touches many files.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_MAX_FILES_PER_BATCH = 50
DEFAULT_MAX_ARG_CHARS = 16000


def load_files(path: str) -> list[str]:
    """Load newline-delimited file paths, preserving order and uniqueness."""
    seen: set[str] = set()
    files: list[str] = []
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        file_path = raw_line.strip()
        if not file_path or file_path in seen:
            continue
        seen.add(file_path)
        files.append(file_path)
    return files


def chunk_files(
    files: list[str],
    *,
    max_files_per_batch: int = DEFAULT_MAX_FILES_PER_BATCH,
    max_arg_chars: int = DEFAULT_MAX_ARG_CHARS,
) -> list[list[str]]:
    """Split file paths into batches with bounded size and argv length."""
    if max_files_per_batch < 1:
        raise ValueError("max_files_per_batch must be at least 1")
    if max_arg_chars < 1:
        raise ValueError("max_arg_chars must be at least 1")

    batches: list[list[str]] = []
    current: list[str] = []
    current_chars = 0

    for file_path in files:
        file_chars = len(file_path) + 1
        if current and (
            len(current) >= max_files_per_batch
            or current_chars + file_chars > max_arg_chars
        ):
            batches.append(current)
            current = []
            current_chars = 0

        current.append(file_path)
        current_chars += file_chars

    if current:
        batches.append(current)

    return batches


def merge_vale_output(merged: dict, batch_data: dict) -> dict:
    """Merge Vale's per-file JSON dictionaries across batches."""
    for path, issues in batch_data.items():
        merged.setdefault(path, [])
        merged[path].extend(issues)
    return merged


def run_batch(
    vale_bin: str,
    config: str,
    batch: list[str],
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    """Run Vale on one batch and capture JSON output."""
    command = [vale_bin, f"--config={config}", "--output=JSON", *batch]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Vale in bounded batches")
    parser.add_argument("--config", required=True, help="Path to Vale config")
    parser.add_argument("--input", required=True, help="Path to files_to_lint.txt")
    parser.add_argument("--output", required=True, help="Path to combined JSON output")
    parser.add_argument("--stderr", required=True, help="Path to captured stderr output")
    parser.add_argument("--vale-bin", default="vale", help="Vale executable to run")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="Per-batch timeout in seconds")
    parser.add_argument("--max-files-per-batch", type=int, default=DEFAULT_MAX_FILES_PER_BATCH)
    parser.add_argument("--max-arg-chars", type=int, default=DEFAULT_MAX_ARG_CHARS)
    args = parser.parse_args()

    files = load_files(args.input)
    batches = chunk_files(
        files,
        max_files_per_batch=args.max_files_per_batch,
        max_arg_chars=args.max_arg_chars,
    )

    merged_output: dict = {}
    stderr_chunks: list[str] = []
    highest_exit_code = 0

    for index, batch in enumerate(batches, start=1):
        print(
            f"Running Vale batch {index}/{len(batches)} on {len(batch)} file(s)",
            file=sys.stderr,
        )
        try:
            result = run_batch(args.vale_bin, args.config, batch, args.timeout_seconds)
        except subprocess.TimeoutExpired:
            Path(args.stderr).write_text(
                f"Vale timed out after {args.timeout_seconds} seconds\n",
                encoding="utf-8",
            )
            return 124

        highest_exit_code = max(highest_exit_code, result.returncode)
        if result.stderr:
            stderr_chunks.append(result.stderr)

        stdout = result.stdout.strip()
        if not stdout:
            continue

        try:
            batch_data = json.loads(stdout)
        except json.JSONDecodeError as exc:
            stderr_chunks.append(
                f"Failed to parse Vale JSON for batch {index}: {exc}\n{result.stdout}\n"
            )
            Path(args.stderr).write_text("".join(stderr_chunks), encoding="utf-8")
            return 2

        if not isinstance(batch_data, dict):
            stderr_chunks.append(
                f"Vale JSON for batch {index} was not an object: {type(batch_data).__name__}\n"
            )
            Path(args.stderr).write_text("".join(stderr_chunks), encoding="utf-8")
            return 2

        merge_vale_output(merged_output, batch_data)

    Path(args.output).write_text(
        json.dumps(merged_output, ensure_ascii=True),
        encoding="utf-8",
    )
    Path(args.stderr).write_text("".join(stderr_chunks), encoding="utf-8")
    return highest_exit_code


if __name__ == "__main__":
    sys.exit(main())
