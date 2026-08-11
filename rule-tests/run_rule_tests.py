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
DEFAULT_CONFIG = REPO_ROOT / ".vale.ini"

ALL_RULES_EXPECTED = {
    "Elastic.Accessibility": [(43, "a victim of")],
    "Elastic.Articles": [(51, "a FAQ")],
    "Elastic.BritishSpellings": [(55, "optimise")],
    "Elastic.Clone": [(99, "Clone")],
    "Elastic.ConflictMarkers": [(157, "<<<<<<< HEAD")],
    "Elastic.DeviceAgnosticism": [(59, "tap")],
    "Elastic.Dimensions": [(63, "1920 x 1080")],
    "Elastic.DontUse": [(59, "Please")],
    "Elastic.Ellipses": [(67, "...")],
    "Elastic.EndPuntuaction": [(24, "!")],
    "Elastic.Exclamation": [(24, "Punctuation!")],
    "Elastic.Gender": [(103, "s/he")],
    "Elastic.GenderBias": [(107, "fireman")],
    "Elastic.HeadingColons": [(30, ": w")],
    "Elastic.Latinisms": [(67, "etc")],
    "Elastic.MappedPages": [(2, "mapped_pages:")],
    "Elastic.MeaningfulCTAs": [(117, "click here")],
    "Elastic.MenuArrows": [(167, "Find > Root")],
    "Elastic.Negations": [(121, "cannot proceed without")],
    "Elastic.OxfordComma": [(125, "indexing, searching and analytics.")],
    "Elastic.PluralAbbreviations": [(129, "API's are")],
    "Elastic.Repetition": [(137, "test test")],
    "Elastic.Semicolons": [(20, ";")],
    "Elastic.Versions": [(145, "and higher")],
    "Elastic.WordChoice": [(87, "whitelist")],
    "Elastic.Wordiness": [(153, "In order to")],
}

MISSING_RULES_EXPECTED = {
    "Elastic.DirectionalLanguage": [(3, "shown below")],
    "Elastic.KibanaChromeTerms": [(7, "side nav")],
    "Elastic.MenuArrowsBold": [(11, "Select **Stack Management** > **Index Management**.")],
    "Elastic.QuotesPunctuation": [(15, '"do not modify the file",')],
}


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


def assert_rule_contains(
    name: str,
    alerts: list[dict],
    rule: str,
    expected: list[tuple[int, str]],
) -> None:
    actual = [(alert["Line"], alert["Match"]) for alert in alerts if alert["Check"] == rule]
    missing = [match for match in expected if match not in actual]

    if missing:
        raise AssertionError(
            f"{name} expected {rule} to include {missing}, but got {actual}."
        )

    print(f"ok {name} {rule}")


def assert_all_rules_have_assertions(asserted_rules: set[str]) -> None:
    rule_files = sorted((REPO_ROOT / "styles" / "Elastic").glob("*.yml"))
    available_rules = {f"Elastic.{path.stem}" for path in rule_files}

    missing_assertions = sorted(available_rules - asserted_rules)
    stale_assertions = sorted(asserted_rules - available_rules)

    if missing_assertions or stale_assertions:
        problems = []
        if missing_assertions:
            problems.append(f"missing assertions for {missing_assertions}")
        if stale_assertions:
            problems.append(f"stale assertions for {stale_assertions}")
        raise AssertionError("; ".join(problems))

    print(f"ok all {len(available_rules)} rules have assertions")


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
    asserted_rules: set[str] = set()

    all_rule_alerts = run_vale(DEFAULT_CONFIG, REPO_ROOT / "test-all-rules.md")
    for rule, expected in ALL_RULES_EXPECTED.items():
        assert_rule_contains("test-all-rules.md", all_rule_alerts, rule, expected)
        asserted_rules.add(rule)

    missing_rule_alerts = run_vale(DEFAULT_CONFIG, FIXTURES / "missing-rules.md")
    for rule, expected in MISSING_RULES_EXPECTED.items():
        assert_rule_contains("missing-rules.md", missing_rule_alerts, rule, expected)
        asserted_rules.add(rule)

    first_person_alerts = run_vale(DEFAULT_CONFIG, FIXTURES / "first-person.md")
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
    asserted_rules.add("Elastic.FirstPerson")

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
    asserted_rules.add("Elastic.Spelling")

    assert_all_rules_have_assertions(asserted_rules)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"not ok {error}", file=sys.stderr)
        raise SystemExit(1)
