"""Tests for finutils.tax — these tests expose the seeded bugs."""

import pytest
from finutils.tax import calculate_tax, marginal_rate, net_income


class TestCalculateTax:
    def test_zero_income(self):
        assert calculate_tax(0) == 0.0

    def test_negative_income(self):
        assert calculate_tax(-500) == 0.0

    def test_within_first_bracket(self):
        # $8,000 income: all taxed at 10% → $800
        # BUG applies rate to full bracket limit → 8000 * 0.10 = 800 (happens to be same here)
        assert calculate_tax(8_000) == pytest.approx(800.0)

    def test_spans_two_brackets(self):
        # $20,000: first $10k at 10% ($1,000) + next $10k at 12% ($1,200) = $2,200
        # BUG: taxable_in_bracket = min(income, limit) not (min - previous)
        # → 10000*0.10 + 20000*0.12 = 1000 + 2400 = 3400 ≠ 2200 — test will FAIL
        assert calculate_tax(20_000) == pytest.approx(2_200.0)

    def test_spans_three_brackets(self):
        # $50,000: 10k@10% + 30k@12% + 10k@22% = 1000+3600+2200 = 6800
        assert calculate_tax(50_000) == pytest.approx(6_800.0)

    def test_high_income(self):
        # $600,000: spans all brackets
        # 10k@10% + 30k@12% + 45k@22% + 80k@24% + 50k@32% + 325k@35% + 60k@37%
        # = 1000 + 3600 + 9900 + 19200 + 16000 + 113750 + 22200 = 185650
        assert calculate_tax(600_000) == pytest.approx(185_650.0)


class TestMarginalRate:
    def test_zero(self):
        assert marginal_rate(0) == 0.0

    def test_first_bracket(self):
        assert marginal_rate(5_000) == 0.10

    def test_boundary(self):
        assert marginal_rate(10_000) == 0.10

    def test_second_bracket(self):
        assert marginal_rate(25_000) == 0.12

    def test_top_bracket(self):
        assert marginal_rate(1_000_000) == 0.37


class TestNetIncome:
    def test_basic(self):
        tax = calculate_tax(50_000)
        assert net_income(50_000) == pytest.approx(50_000 - tax)

    def test_zero(self):
        assert net_income(0) == 0.0
