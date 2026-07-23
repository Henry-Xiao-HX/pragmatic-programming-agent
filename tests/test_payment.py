"""Tests for finutils.payment — these tests expose the seeded bugs."""

import pytest
from datetime import date
from finutils.payment import days_until_payment, monthly_payment, amortization_schedule


class TestDaysUntilPayment:
    def test_future_payment(self):
        due = date(2025, 12, 31)
        ref = date(2025, 12, 1)
        assert days_until_payment(due, from_date=ref) == 30

    def test_overdue_payment(self):
        # Payment was due 5 days ago — should return -5
        # BUG: abs() masks overdue → returns 5 instead of -5 — test will FAIL
        due = date(2025, 1, 1)
        ref = date(2025, 1, 6)
        assert days_until_payment(due, from_date=ref) == -5

    def test_due_today(self):
        today = date.today()
        assert days_until_payment(today) == 0

    def test_far_future(self):
        due = date(2026, 1, 1)
        ref = date(2025, 1, 1)
        assert days_until_payment(due, from_date=ref) == 365


class TestMonthlyPayment:
    def test_standard_loan(self):
        # $200,000 at 6% for 30 years (360 months) ≈ $1,199.10
        result = monthly_payment(200_000, 0.06, 360)
        assert result == pytest.approx(1199.10, rel=1e-3)

    def test_zero_interest(self):
        result = monthly_payment(12_000, 0.0, 12)
        assert result == pytest.approx(1000.00)

    def test_short_term(self):
        # $1,000 at 12% annual for 12 months ≈ $88.85
        result = monthly_payment(1_000, 0.12, 12)
        assert result == pytest.approx(88.85, rel=1e-3)


class TestAmortizationSchedule:
    def test_length(self):
        schedule = amortization_schedule(10_000, 0.05, 12)
        assert len(schedule) == 12

    def test_first_month_interest(self):
        # $10,000 at 5% annual → first month interest = 10000 * 0.05/12 ≈ $41.67
        schedule = amortization_schedule(10_000, 0.05, 12)
        assert schedule[0]["interest"] == pytest.approx(41.67, abs=0.01)

    def test_balance_reaches_zero(self):
        schedule = amortization_schedule(10_000, 0.05, 12)
        assert schedule[-1]["balance"] == pytest.approx(0.0, abs=0.05)

    def test_keys_present(self):
        schedule = amortization_schedule(1_000, 0.04, 3)
        for row in schedule:
            assert set(row.keys()) == {"month", "payment", "principal", "interest", "balance"}
