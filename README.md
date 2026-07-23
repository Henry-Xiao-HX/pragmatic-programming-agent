# pragmatic-programming-agent

A Python library of financial calculation utilities, used to demonstrate an
AI-powered Bob skill that automatically reviews open GitHub Issues, applies
code fixes, and opens pull requests — triggered locally via IBM Bob, without
needing cloud CI.

## Modules

| Module | Functions |
|---|---|
| `finutils/interest.py` | `simple_interest`, `compound_interest`, `effective_annual_rate` |
| `finutils/tax.py` | `calculate_tax`, `marginal_rate`, `net_income` |
| `finutils/bill.py` | `split_bill`, `apply_tip`, `itemized_total` |
| `finutils/payment.py` | `days_until_payment`, `monthly_payment`, `amortization_schedule` |
| `finutils/currency.py` | `format_currency`, `convert_currency`, `round_to_cent` |

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

## Linting

```bash
ruff check .
```

## How the agent works

This repository includes intentionally seeded demo bugs and matching GitHub
issues labelled `bot-fixable`. The Bob auto-fix flow is designed to fetch and
attempt only those open issues.

Issue fetching is handled by [`fetch-issues.py`](.bob/skills/fix-issues/fetch-issues.py),
which uses the authenticated GitHub CLI to:

- list open issues with the `bot-fixable` label
- fetch a single issue by number
- reject closed issues or issues missing the required label

The `/fix-issues` workflow is defined in
[`SKILL.md`](.bob/skills/fix-issues/SKILL.md) and works like this:

1. Run `/fix-issues` (or `/fix-issues <number>`) inside IBM Bob.
2. Bob runs [`fetch-issues.py`](.bob/skills/fix-issues/fetch-issues.py) and
   presents the matching open `bot-fixable` issues.
3. After one explicit user confirmation, the skill checks scope and refuses
   issues that are too broad or marked with labels such as `needs-design` or
   `breaking-change`.
4. Before any investigation, the skill runs `git status --porcelain` (combined
   with `git rev-parse --abbrev-ref HEAD`) and stops if tracked files are already
   modified. The current branch name is stored and reused later.
5. Bob reads the referenced files, applies a minimal fix, then confirms the
   modified file list, branch availability, and remote in one command before
   validating with `ruff check .` and `pytest --tb=short -q` (using `.venv/bin`
   when available).
6. If validation passes, Bob creates a `fix/issue-{number}` branch, stages only
   the touched files, commits, and pushes — all as a single chained command —
   then opens a pull request.
7. If validation fails after repeated attempts, Bob reverts only the files it
   changed and stops without pushing broken code.

This setup is intended for local demonstrations of a bounded GitHub issue
triage-and-fix workflow rather than general autonomous maintenance.
