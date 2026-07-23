# pragmatic-programming-agent

A Python library of financial calculation utilities, used to demonstrate an
AI-powered GitHub Actions workflow that automatically reviews open issues,
applies code fixes, and opens pull requests — on a schedule, without human
involvement.

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

1. A GitHub Actions workflow runs on a daily schedule.
2. It fetches all open issues labelled `bot-fixable`.
3. For each issue, it checks out a new branch, calls an AI agent with the
   issue body and relevant source file, applies the suggested patch, then
   runs `ruff check` + `pytest`.
4. If both pass, the workflow opens a pull request referencing the issue.
5. If they fail, it posts a comment on the issue and moves on.
