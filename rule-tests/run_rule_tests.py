#!/usr/bin/env python3
"""Run focused regression tests for local Vale rules."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "rule-tests" / "fixtures"


def run_vale(config: Path, fixture: Path) -> list[dict]:
    result = subprocess.run(
        [
            "vale",
            f"--config={config}",
            "--no-global",
            "--output=JSON",
            str(fixture),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    if result.returncode not in (0, 1):
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise AssertionError(f"Vale failed for {fixture} with exit code {result.returncode}.")

    if not result.stdout.strip():
        return []

    output = json.loads(result.stdout)
    return output.get(str(fixture), [])


def assert_rule_matches(
    name: str,
    alerts: list[dict],
    rule: str,
    expected: list[tuple[int, str]],
) -> None:
    actual = [(alert["Line"], alert["Match"]) for alert in alerts if alert["Check"] == rule]

    if actual != expected:
        raise AssertionError(
            f"{name} expected {rule} matches {expected}, but got {actual}."
        )

    print(f"ok {name}")


def spelling_config(tmp_dir: Path) -> Path:
    config = tmp_dir / "spelling.vale.ini"
    config.write_text(
        "\n".join(
            [
                f"StylesPath = {REPO_ROOT / 'styles'}",
                "MinAlertLevel = suggestion",
                "Vocab = ElasticTerms, ThirdPartyProducts, TechJargon, GeographicNames",
                "",
                "[*.md]",
                "BasedOnStyles = Elastic",
                "Elastic.Spelling = YES",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return config


def main() -> int:
    first_person_alerts = run_vale(REPO_ROOT / ".vale.ini", FIXTURES / "first-person.md")
    assert_rule_matches(
        "first-person boundaries",
        first_person_alerts,
        "Elastic.FirstPerson",
        [
            (2, "My"),
            (3, "me"),
            (4, "mine"),
            (7, "me"),
            (7, "my"),
            (7, "mine"),
        ],
    )

    with tempfile.TemporaryDirectory() as tmp:
        spelling_alerts = run_vale(
            spelling_config(Path(tmp)),
            FIXTURES / "spelling-cloud-regions.md",
        )

    assert_rule_matches(
        "cloud-region spelling vocabulary",
        spelling_alerts,
        "Elastic.Spelling",
        [(4, "Gatewaty")],
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"not ok {error}", file=sys.stderr)
        raise SystemExit(1)
