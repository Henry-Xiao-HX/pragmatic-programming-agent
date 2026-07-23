---
name: fix-issues
description: "Use when the user types /fix-issues or /fix-issues {number} — autonomously fetches open GitHub Issues labelled bot-fixable, applies a surgical code fix, validates it, commits to a branch, and opens a PR. One human confirmation required: which issue to fix."
metadata:
  argument-hint: "[issue-number]"
---

# Fix Issues

One confirmation point in the pipeline: always ask the user to confirm the selected issue before proceeding. All subsequent steps run without pausing.
The PR description is your audit trail — make it thorough.

---

## Step 1 — Fetch issues

Run:

```
python3 .bob/skills/fix-issues/fetch-issues.py [issue-number]
```

Use `execute_command`. Parse the JSON array printed to stdout.

- If the array is empty, report "No open issues with label `bot-fixable` found." and stop.
- If an issue number was supplied by the user (`/fix-issues 42`), display a one-line summary (`#number — title`) and ask: **"Proceed with fixing this issue? (yes/no)"**. Wait for their reply before continuing.
- If multiple issues are returned, present a numbered list (number, title, one-line body summary) and ask the user to pick one.

**In both cases, wait for the user's reply before proceeding to Step 2. This is the only confirmation point in the pipeline.**

---

## Step 2 — Scope guard

Verify all four conditions. If any fail, print a clear reason and stop — do not write any code:

1. Issue has the label `bot-fixable`.
2. Issue body references at least one specific file path or component name.
3. The issue body does not explicitly describe changes spanning more than 3 files (a definitive file-count check happens after investigation in Step 3).
4. Issue does not have the label `needs-design` or `breaking-change`.

---

## Step 2b — Pre-flight dirty-state check

Before reading or modifying any file, run:

```bash
git status --porcelain && git rev-parse --abbrev-ref HEAD
```

If any **tracked** files appear in the `git status` output (lines that do not start with `??`), stop immediately. Print the output and report:

> "Uncommitted changes detected in the working tree. Please stash or commit those changes before running `/fix-issues`, then try again."

Do **not** investigate or apply any fix. Exit the pipeline here.

Store the branch name printed by `git rev-parse` — reused in Step 6; do not run that command again.

---

## Step 3 — Investigate

Read every file explicitly mentioned in the issue body using `read_file`.
Use `grep` to locate component or symbol names referenced in the issue.
Use `GetSymbolsOverview` or `FindSymbol` to understand unfamiliar file structure.

Produce an internal summary (used later in the PR description):
- Root cause.
- Exact lines / symbols to change.
- **Explicit list** of every file that will be touched.

If this list contains more than 3 files, stop here. Report the files you found and explain that the change exceeds the 3-file scope limit — do not apply any fix.

---

## Step 4 — Apply the fix

Use `apply_diff` or `search_and_replace` for surgical edits.
Use `write_file` only when a full rewrite is clearly required.
Make the **minimal** change that resolves the issue.
Do not reformat, refactor, or touch unrelated code.

After applying the fix, capture the modified files and run the remaining pre-flight checks in one call:

```bash
git diff --name-only && git branch --list fix/issue-{number} && git remote get-url origin
```

- The `git diff --name-only` output is the **authoritative file list** used for revert (Step 5) and `git add` (Step 6). Store it.
- If `git branch --list` prints the branch name, stop: "Branch `fix/issue-{number}` already exists." Do **not** push.
- If `git remote get-url origin` fails or prints nothing, stop: "No `origin` remote found." Do **not** commit.

---

## Step 5 — Validate

Run from the repository root:

```bash
if [ -x .venv/bin/ruff ] && [ -x .venv/bin/pytest ]; then
  .venv/bin/ruff check . && .venv/bin/pytest --tb=short -q
else
  ruff check . && pytest --tb=short -q
fi
```

Capture the full output. If it fails:
- Read the error, apply a targeted fix, and re-run.
- Repeat up to **3 attempts total**.

If validation still fails after 3 attempts:
- Run `git checkout -- {authoritative file list from Step 4}` to revert only the files the skill touched.
- Open a PR-less comment or just stop, reporting the failure output so you can debug manually.
- Do **not** push broken code.

Record:
- Whether lint passed or failed (and on which attempt).
- Whether tests passed or failed (and on which attempt).
- Test counts: total, passed, failed, skipped.

This data goes into the PR description.

---

## Step 6 — Commit and push

All pre-flight checks (branch existence, remote, current branch) were already performed in Steps 2b and 4. Use the stored values — do **not** re-run those commands.

If the stored branch name (from Step 2b) is not `main` or `master`, stop: "You are not on main/master. Switch to the default branch before running `/fix-issues`." Do **not** branch or push.

Run the entire commit-and-push sequence as one chained command:

```bash
git checkout -b fix/issue-{number} && \
git add -- {authoritative file list from Step 4} && \
git commit -m "fix: resolve issue #{number} — {short title}" && \
git push -u origin fix/issue-{number}
```

Never use `git add -A` or `git add .` — this prevents untracked generated files (coverage reports, lock file changes, build artefacts) from being included in the commit.

---

## Step 7 — Open a PR via `create_pr_workflow`

Use `start_workflow` with `workflow_id: create_pr_workflow`.

The PR description **must** include all of the following sections:

```
## What

{one paragraph: what was broken and what was changed}

## Why

Closes #{number}

{one paragraph: root cause from investigation}

## Files changed

{bullet list of every file touched, with a one-line reason for each}

## Validation

| Check  | Result  | Attempts |
|--------|---------|----------|
| lint   | ✅ pass / ❌ fail | n |
| tests  | ✅ pass / ❌ fail | n |

Test run: {X passed, Y failed, Z skipped}

## Fix approach

{brief description of the surgical edit strategy — why apply_diff/search_and_replace
was used, what was preserved, what was not touched}
```

---

## Constraints

- Never push to `main` or `master`.
- Never label or un-label issues.
- If scope expands beyond 3 files during investigation, stop and report — do not attempt the fix.
- The PR is the only human-review surface. Make it complete.
