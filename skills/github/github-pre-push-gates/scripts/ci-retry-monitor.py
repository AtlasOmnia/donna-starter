#!/usr/bin/env python3
"""
CI retry monitor — watches a specific SHA across reruns and distinguishes
infrastructure failures (zero executed steps) from product failures.

Usage:
  python3 ci-retry-monitor.py <repo> <run-id> <expected-sha>

The script polls every 30 s. It auto-reruns the workflow if every job
failed with zero steps (infrastructure / billing / outage). On a real
product failure (at least one job has >0 steps and a test assertion
failed), it exits nonzero immediately.

Requires: gh CLI + repo-level read/write token scope.
"""

import json, subprocess, time, sys

EXPECTED_SHA = sys.argv[3]
REPO = sys.argv[1]
RUN_ID = sys.argv[2]

def api(path):
    r = subprocess.run(["gh", "api", path], text=True, capture_output=True)
    if r.returncode: return None
    try: return json.loads(r.stdout)
    except Exception: return None

def has_real_steps(jobs_data):
    """Return True if any job actually executed steps (i.e. it was not a
    pre-run cancellation / billing block / outage)."""
    for job in jobs_data.get("jobs", []):
        steps = job.get("steps") or []
        if len(steps) > 0:
            return True
    return False

def rerun():
    subprocess.run(["gh", "api", "-X", "POST",
        f"repos/{REPO}/actions/runs/{RUN_ID}/rerun"],
        capture_output=True)

for _ in range(240):
    run = api(f"repos/{REPO}/actions/runs/{RUN_ID}")
    if not run:
        time.sleep(30); continue
    sha = run.get("head_sha")
    if sha and sha != EXPECTED_SHA:
        print(f"CI_MONITOR_ERROR sha mismatch: got {sha} expected {EXPECTED_SHA}")
        sys.exit(2)
    if run.get("status") != "completed":
        time.sleep(30); continue
    at = run.get("run_attempt", 1)
    jobs = api(f"repos/{REPO}/actions/runs/{RUN_ID}/attempts/{at}/jobs") or {"jobs": []}
    summary = ", ".join(
        f"{j.get('name')}={j.get('conclusion')} steps={len(j.get('steps') or [])}"
        for j in jobs.get("jobs", [])
    )
    if run.get("conclusion") == "success":
        print(f"CI_VERIFIED sha={EXPECTED_SHA} run={RUN_ID} attempt={at} jobs=[{summary}]")
        sys.exit(0)
    if not has_real_steps(jobs):
        print(f"CI_INFRASTRUCTURE_FAILURE — rerunning. attempt={at} jobs=[{summary}]", flush=True)
        rerun()
        time.sleep(30)
        continue
    print(f"CI_PRODUCT_FAILURE sha={EXPECTED_SHA} run={RUN_ID} attempt={at} jobs=[{summary}]")
    sys.exit(3)

print(f"CI_MONITOR_TIMEOUT sha={EXPECTED_SHA} run={RUN_ID}")
sys.exit(4)
