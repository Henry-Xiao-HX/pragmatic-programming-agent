"""Loan payment and amortization utilities."""

from __future__ import annotations

from datetime import date


def days_until_payment(due_date: date, from_date: date | None = None) -> int:
    """Return the number of days until a payment is due.

    Args:
        due_date: The date the payment is due.
        from_date: The reference date (defaults to today).

    Returns:
        Number of days until due. Negative if overdue.

    BUG: returns absolute value, masking overdue payments by always
    returning a non-negative number.
    """
    if from_date is None:
        from_date = date.today()
    # BUGGY: should return (due_date - from_date).days (signed)
    return abs((due_date - from_date).days)


def monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """Calculate the fixed monthly payment for an amortizing loan.

    Uses the standard amortization formula:
        M = P * [r(1+r)^n] / [(1+r)^n - 1]

    Args:
        principal: Loan amount in dollars.
        annual_rate: Annual interest rate as a decimal (e.g. 0.06 for 6%).
        months: Loan term in months.

    Returns:
        Fixed monthly payment in dollars.
    """
    if annual_rate == 0:
        return round(principal / months, 2)
    r = annual_rate / 12
    payment = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return round(payment, 2)


def amortization_schedule(
    principal: float, annual_rate: float, months: int
) -> list[dict]:
    """Return a full amortization schedule as a list of monthly records.

    Args:
        principal: Loan amount in dollars.
        annual_rate: Annual interest rate as a decimal.
        months: Loan term in months.

    Returns:
        List of dicts, one per month, with keys:
        'month', 'payment', 'principal', 'interest', 'balance'.
    """
    schedule = []
    balance = principal
    r = annual_rate / 12
    payment = monthly_payment(principal, annual_rate, months)

    for month in range(1, months + 1):
        interest = round(balance * r, 2)
        principal_paid = round(payment - interest, 2)
        balance = round(balance - principal_paid, 2)
        schedule.append(
            {
                "month": month,
                "payment": payment,
                "principal": principal_paid,
                "interest": interest,
                "balance": max(balance, 0.0),
            }
        )

    return schedule
