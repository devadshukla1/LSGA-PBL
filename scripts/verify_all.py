"""Master verification runner orchestrating all individual phase verification suites."""

import subprocess
import sys
import time
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VERIFICATION_SCRIPTS = (
    "scripts/verify_setup.py",
    "scripts/verify_traversal.py",
    "scripts/verify_routing.py",
    "scripts/verify_advanced_routing.py",
    "scripts/verify_simulation.py",
    "scripts/verify_analytics.py",
    "scripts/verify_partitioning.py",
    "scripts/verify_benchmarks.py",
    "scripts/verify_dashboard.py",
)


def run_all_verifications() -> bool:
    print("=" * 70)
    print("SMART CITY TRAFFIC & EMERGENCY ROUTE OPTIMIZER")
    print("PHASE 11: Master Multi-Phase Verification Suite")
    print("=" * 70)

    results = []
    overall_success = True

    for rel_path in VERIFICATION_SCRIPTS:
        full_path = ROOT / rel_path
        if not full_path.is_file():
            results.append((rel_path, -1, 0.0, "NOT VERIFIED", "File not found"))
            overall_success = False
            continue

        print(f"\n[RUNNING] {rel_path}...")
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        duration = time.perf_counter() - t0

        passed = proc.returncode == 0
        status = "PASS" if passed else "FAIL"
        err_msg = "" if passed else (proc.stderr.strip() or proc.stdout.strip()[-200:])

        results.append((rel_path, proc.returncode, duration, status, err_msg))
        if not passed:
            overall_success = False

    print("\n" + "=" * 70)
    print("MASTER VERIFICATION SUMMARY:")
    print("=" * 70)
    print(f"{'Verification Suite':<35} | {'Status':<6} | {'Duration':<9} | {'Details'}")
    print("-" * 70)
    for path, code, dur, status, err in results:
        status_tag = f"[{status}]"
        detail = "OK" if status == "PASS" else f"Exit code {code}: {err[:30]}"
        print(f"{path:<35} | {status_tag:<6} | {dur:>7.2f} s | {detail}")
    print("=" * 70)

    if overall_success:
        print("ALL VERIFICATION SUITES PASSED: 100% SUCCESS")
    else:
        print("VERIFICATION SUITES FAILED")
    print("=" * 70)

    return overall_success


if __name__ == "__main__":
    success = run_all_verifications()
    sys.exit(0 if success else 1)
