#!/usr/bin/env python3
"""
scripts/log_analyser.py

Reads config/test_config.yaml to get the list of tests, parses each
test's simulation log (produced by the Makefile's `sim` target) using
plain string methods (count(), find(), splitlines() - no regex), and
builds a pass/fail summary.

The summary is written to:
    reports/summary.csv
    reports/summary.xlsx
    reports/summary.yaml
    reports/regression_summary.txt   (human-readable, opened by `make regress`)

and an overall PASS/FAIL count is printed to the console.

Only file-handling, string manipulation, os, pandas and PyYAML are used.
"""

import os
import sys
import yaml
import pandas as pd

# ---------------------------------------------------------------------------
# Paths - resolved relative to this script's own location (not the
# caller's current working directory), so it behaves the same whether
# it's invoked from sim/, scripts/, or anywhere else.
# ---------------------------------------------------------------------------
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CONFIG_PATH  = os.path.join(PROJECT_ROOT, "config", "test_config.yaml")
LOG_DIR      = os.path.join(PROJECT_ROOT, "logs")
REPORT_DIR   = os.path.join(PROJECT_ROOT, "reports")

RESULT_MARKER = "TEST_CASE"   # e.g. "TEST_CASE: counter_test RESULT : PASSED"


def load_tests(config_path):
    """Read config/test_config.yaml and return its list of test dicts."""
    if not os.path.isfile(config_path):
        print(f"ERROR: test config not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    return data.get("tests", [])


def analyse_log(log_path):
    """
    Parse a single simulation log using only string methods.
    Returns a dict with info/warning/error/fatal counts and the result.
    """
    counts = {
        "infos":    0,
        "warnings": 0,
        "errors":   0,
        "fatals":   0,
    }
    result = "FAIL"

    if not os.path.isfile(log_path):
        return counts, result

    with open(log_path, "r") as f:
        content = f.read()

    counts["infos"]    = content.count("UVM_INFO")
    counts["warnings"] = content.count("UVM_WARNING")
    counts["errors"]   = content.count("UVM_ERROR")
    counts["fatals"]   = content.count("UVM_FATAL")

    for line in content.splitlines():
        if RESULT_MARKER in line and "RESULT" in line:
            if line.find("PASSED") != -1:
                result = "PASS"
            elif line.find("FAILED") != -1:
                result = "FAIL"
            # last matching line in the file wins, in case of duplicates

    return counts, result


def build_summary(tests):
    """
    Build the summary list of dicts: one entry per test with keys
    test, errors, warnings, fatals, result.
    """
    summary = []

    for t in tests:
        name = t["name"]
        seed = t["seed"]
        log_path = os.path.join(LOG_DIR, f"sim_{name}_{seed}.log")

        counts, result = analyse_log(log_path)

        summary.append({
            "test":     name,
            "errors":   counts["errors"],
            "warnings": counts["warnings"],
            "fatals":   counts["fatals"],
            "result":   result,
        })

    return summary


def write_reports(summary):
    """Write the summary to CSV, XLSX, YAML and a human-readable .txt."""
    os.makedirs(REPORT_DIR, exist_ok=True)

    df = pd.DataFrame(summary, columns=["test", "errors", "warnings", "fatals", "result"])

    csv_path  = os.path.join(REPORT_DIR, "summary.csv")
    xlsx_path = os.path.join(REPORT_DIR, "summary.xlsx")
    yaml_path = os.path.join(REPORT_DIR, "summary.yaml")
    txt_path  = os.path.join(REPORT_DIR, "regression_summary.txt")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    with open(yaml_path, "w") as f:
        yaml.dump(summary, f, default_flow_style=False, sort_keys=False)

    passed = sum(1 for e in summary if e["result"] == "PASS")
    failed = len(summary) - passed

    with open(txt_path, "w") as f:
        f.write("Regression Summary\n")
        f.write("=" * 60 + "\n")
        for e in summary:
            f.write(
                "{test:<10} result={result:<5} "
                "errors={errors:<3} warnings={warnings:<3} fatals={fatals:<3}\n"
                .format(**e)
            )
        f.write("=" * 60 + "\n")
        f.write(f"TOTAL: {len(summary)}   PASSED: {passed}   FAILED: {failed}\n")

    return csv_path, xlsx_path, yaml_path, txt_path


def main():
    tests = load_tests(CONFIG_PATH)
    if not tests:
        print(f"No tests found in {CONFIG_PATH}")
        sys.exit(1)

    summary = build_summary(tests)
    csv_path, xlsx_path, yaml_path, txt_path = write_reports(summary)

    passed = sum(1 for e in summary if e["result"] == "PASS")
    failed = len(summary) - passed

    print("=" * 60)
    print("Regression results")
    print("=" * 60)
    for e in summary:
        print(
            "  {test:<10} result={result:<5} errors={errors} "
            "warnings={warnings} fatals={fatals}".format(**e)
        )
    print("-" * 60)
    print(f"TOTAL: {len(summary)}   PASSED: {passed}   FAILED: {failed}")
    print("=" * 60)
    print("Reports written to:")
    print(f"  {csv_path}")
    print(f"  {xlsx_path}")
    print(f"  {yaml_path}")
    print(f"  {txt_path}")


if __name__ == "__main__":
    main()
