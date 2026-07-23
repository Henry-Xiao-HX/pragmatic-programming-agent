"""
Agent fix script — called by the auto-fix GitHub Actions workflow.

For each open issue labelled 'bot-fixable':
  1. Parse the issue body for the target file and function.
  2. Send the issue + source file to the OpenAI API.
  3. Apply the returned unified diff.
  4. Run ruff + pytest.
  5. If both pass  → open a pull request.
  6. If either fails → post a comment on the issue and continue.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("openai package not installed — run: pip install openai")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
ISSUES_FILE = ROOT / "issues.json"
GH_TOKEN = os.environ["GH_TOKEN"]
REPO = os.environ.get("GITHUB_REPOSITORY", "")


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, check=check)


def gh(*args: str) -> str:
    result = run(["gh", *args], check=False)
    return result.stdout.strip()


def post_comment(issue_number: int, body: str) -> None:
    gh("issue", "comment", str(issue_number), "--body", body)


def attempt_fix(issue: dict) -> None:
    number = issue["number"]
    title = issue["title"]
    body = issue["body"] or ""

    print(f"\n=== Issue #{number}: {title} ===")

    # Extract file path from issue body (line starting with "finutils/")
    file_path: Path | None = None
    for line in body.splitlines():
        line = line.strip().strip("`")
        if line.startswith("finutils/") and line.endswith(".py"):
            file_path = ROOT / line
            break

    if file_path is None or not file_path.exists():
        print(f"  Could not determine source file — skipping.")
        post_comment(number, "⚠️ Agent could not determine the source file from this issue. Please add a **File** section with the relative path.")
        return

    source = file_path.read_text()

    # Build the prompt
    prompt = textwrap.dedent(f"""
        You are a Python bug-fix agent. You will be given a GitHub issue and the
        full source of the file it references. Return ONLY a unified diff (no
        explanations, no markdown fences) that fixes the described bug.

        The diff must apply cleanly with: patch -p1

        --- ISSUE #{number}: {title} ---
        {body}

        --- SOURCE: {file_path.relative_to(ROOT)} ---
        {source}
    """).strip()

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    diff_text = response.choices[0].message.content.strip()

    # Checkout a new branch
    branch = f"fix/issue-{number}"
    run(["git", "config", "user.email", "bot@github-actions"])
    run(["git", "config", "user.name", "auto-fix-bot"])
    run(["git", "checkout", "-b", branch])

    # Write diff to a temp file and apply it
    diff_file = ROOT / "fix.patch"
    diff_file.write_text(diff_text)
    patch_result = run(["patch", "-p1", "-i", "fix.patch"], check=False)
    diff_file.unlink(missing_ok=True)

    if patch_result.returncode != 0:
        print(f"  Patch failed:\n{patch_result.stderr}")
        run(["git", "checkout", "main"])
        run(["git", "branch", "-D", branch])
        post_comment(number, f"⚠️ Agent generated a patch that did not apply cleanly.\n\n```\n{patch_result.stderr[:500]}\n```")
        return

    # Validate: lint + test
    lint = run(["ruff", "check", "."], check=False)
    test = run(["pytest", "--tb=short", "-q"], check=False)

    if lint.returncode != 0 or test.returncode != 0:
        failures = []
        if lint.returncode != 0:
            failures.append(f"**Lint failures:**\n```\n{lint.stdout[:600]}\n```")
        if test.returncode != 0:
            failures.append(f"**Test failures:**\n```\n{test.stdout[:600]}\n```")
        detail = "\n\n".join(failures)
        print(f"  Validation failed.")
        run(["git", "checkout", "main"])
        run(["git", "branch", "-D", branch])
        post_comment(number, f"⚠️ Agent applied a patch but validation failed:\n\n{detail}")
        return

    # Commit and push
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", f"fix: resolve issue #{number} — {title}"])
    run(["git", "push", "origin", branch])

    # Open PR
    pr_body = textwrap.dedent(f"""
        Automated fix for issue #{number}.

        Closes #{number}

        ---
        *This PR was opened automatically by the auto-fix agent.*
    """).strip()

    gh(
        "pr", "create",
        "--title", f"fix: {title}",
        "--body", pr_body,
        "--base", "main",
        "--head", branch,
        "--label", "automated-pr",
    )
    print(f"  ✅ PR opened for issue #{number}.")

    # Switch back to main for the next issue
    run(["git", "checkout", "main"])


def main() -> None:
    if not ISSUES_FILE.exists():
        print("issues.json not found — nothing to do.")
        return

    issues = json.loads(ISSUES_FILE.read_text())
    if not issues:
        print("No bot-fixable issues found.")
        return

    print(f"Processing {len(issues)} issue(s)...")
    for issue in issues:
        attempt_fix(issue)


if __name__ == "__main__":
    main()
