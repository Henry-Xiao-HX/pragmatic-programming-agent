"""Tests for finutils.interest — these tests expose the seeded bugs."""

import pytest
from finutils.interest import simple_interest, compound_interest, effective_annual_rate


class TestSimpleInterest:
    def test_basic(self):
        assert simple_interest(1000, 0.05, 3) == pytest.approx(150.0)

    def test_zero_rate(self):
        assert simple_interest(1000, 0.0, 5) == 0.0

    def test_zero_time(self):
        assert simple_interest(1000, 0.05, 0) == 0.0

    def test_fractional_time(self):
        assert simple_interest(1200, 0.10, 0.5) == pytest.approx(60.0)


class TestCompoundInterest:
    def test_annual_compounding(self):
        # n=1: P*(1+r)^t  →  1000*(1.05)^2 = 1102.50
        assert compound_interest(1000, 0.05, 2, n=1) == pytest.approx(1102.50, rel=1e-4)

    def test_monthly_compounding(self):
        # n=12: 1000*(1+0.05/12)^(12*1) ≈ 1051.16
        # BUG will produce 1000*(1+0.05/12)^(12+1) ≈ 1055.63 — test will FAIL
        assert compound_interest(1000, 0.05, 1, n=12) == pytest.approx(1051.16, rel=1e-3)

    def test_quarterly_compounding(self):
        # n=4: 1000*(1+0.06/4)^(4*2) ≈ 1126.49
        assert compound_interest(1000, 0.06, 2, n=4) == pytest.approx(1126.49, rel=1e-3)

    def test_zero_rate(self):
        assert compound_interest(1000, 0.0, 5) == pytest.approx(1000.0)


class TestEffectiveAnnualRate:
    def test_annual_equals_nominal(self):
        # n=1: EAR should equal nominal rate
        assert effective_annual_rate(0.05, 1) == pytest.approx(0.05)

    def test_monthly(self):
        # 6% nominal, monthly: (1+0.06/12)^12 - 1 ≈ 0.06168
        assert effective_annual_rate(0.06, 12) == pytest.approx(0.06168, rel=1e-3)
