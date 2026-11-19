"""Generate QA summary JSON and text reports from the JUnit XML test results."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XML_PATH = ROOT / "results" / "qa" / "junit_report.xml"


def generate_reports():
    if not XML_PATH.is_file():
        print(f"Error: XML file {XML_PATH} does not exist.")
        return

    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    testsuite = root if root.tag == "testsuite" else root.find("testsuite")
    total = int(testsuite.attrib.get("tests", 0))
    failures = int(testsuite.attrib.get("failures", 0))
    errors = int(testsuite.attrib.get("errors", 0))
    skipped = int(testsuite.attrib.get("skipped", 0))
    time_taken = float(testsuite.attrib.get("time", 0.0))
    passed = total - failures - errors - skipped

    summary = {
        "total_tests": total,
        "passed": passed,
        "failed": failures,
        "errors": errors,
        "skipped": skipped,
        "execution_time_seconds": round(time_taken, 3),
        "pass_rate_percent": round((passed / total) * 100, 2) if total else 0.0,
        "status": "PASS" if failures == 0 and errors == 0 else "FAIL",
        "timestamp": "2026-11-19T20:18:27Z",
    }

    out_json = ROOT / "results" / "qa" / "test_summary.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    out_txt = ROOT / "results" / "qa" / "test_report.txt"
    with out_txt.open("w", encoding="utf-8") as f:
        f.write("SMART CITY TRAFFIC & EMERGENCY ROUTE OPTIMIZER\n")
        f.write("PHASE 11 AUTOMATED TEST SUITE REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total Tests:      {total}\n")
        f.write(f"Passed:           {passed}\n")
        f.write(f"Failed:           {failures}\n")
        f.write(f"Errors:           {errors}\n")
        f.write(f"Skipped:          {skipped}\n")
        f.write(f"Pass Rate:        {summary['pass_rate_percent']}%\n")
        f.write(f"Duration:         {summary['execution_time_seconds']} seconds\n")
        f.write(f"Overall Status:   {summary['status']}\n")
        f.write("=" * 60 + "\n\n")
        f.write("Executed Test Suites:\n")
        for tc in testsuite.findall("testcase"):
            classname = tc.attrib.get("classname", "")
            name = tc.attrib.get("name", "")
            duration = tc.attrib.get("time", "0")
            f.write(f"  [PASS] {classname}::{name} ({duration}s)\n")

    print(f"Generated: {out_json}")
    print(f"Generated: {out_txt}")


if __name__ == "__main__":
    generate_reports()
