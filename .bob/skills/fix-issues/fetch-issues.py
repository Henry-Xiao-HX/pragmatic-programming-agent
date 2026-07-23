#!/usr/bin/env python3
# ^ use python3 explicitly — `python` is not guaranteed on macOS/Linux PATH
"""
fetch-issues.py
Usage:
  python fetch-issues.py          → list all open issues labelled bot-fixable
  python fetch-issues.py 42       → fetch a single issue by number

Prints a JSON array to stdout. Bob parses this output directly.
Requires: gh CLI authenticated to GitHub.
"""

import json
import re
import subprocess
import sys

LABEL = "bot-fixable"
JSON_FIELDS = "number,title,body,labels,url"

issue_number = sys.argv[1] if len(sys.argv) > 1 else None

# Validate issue number early — prevents shell injection via argv
if issue_number and not re.fullmatch(r"\d+", issue_number):
    sys.stderr.write(f'Invalid issue number: "{issue_number}". Must be a positive integer.\n')
    sys.exit(1)


def run(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Command failed: {' '.join(args)}")
    return result.stdout.strip()


try:
    # Resolve the canonical repo (owner/name) from the authenticated gh CLI so that
    # forks and multi-remote workspaces always target the correct repository.
    repo = json.loads(run(["gh", "repo", "view", "--json", "nameWithOwner"]))["nameWithOwner"]

    if issue_number:
        # Single issue by number — fetch with state so we can reject closed issues
        raw = run(["gh", "issue", "view", issue_number, "--repo", repo, "--json", f"{JSON_FIELDS},state"])
        issue = json.loads(raw)

        # Reject closed issues
        if issue.get("state") and issue["state"] != "OPEN":
            print(json.dumps([]))
            sys.stderr.write(f"Issue #{issue_number} is {issue['state'].lower()} — only open issues can be auto-fixed.\n")
            sys.exit(0)

        # Confirm it carries the required label before returning
        has_label = any(l["name"] == LABEL for l in issue.get("labels", []))
        if not has_label:
            print(json.dumps([]))
            sys.stderr.write(f"Issue #{issue_number} does not have the '{LABEL}' label.\n")
            sys.exit(0)

        print(json.dumps([issue], indent=2))

    else:
        # All open issues with the label, sorted ascending by number
        raw = run(["gh", "issue", "list", "--repo", repo, "--label", LABEL,
                   "--state", "open", "--json", JSON_FIELDS, "--limit", "50"])
        issues = sorted(json.loads(raw), key=lambda i: i["number"])
        print(json.dumps(issues, indent=2))

except Exception as e:
    sys.stderr.write(f"fetch-issues error: {e}\n")
    sys.exit(1)
