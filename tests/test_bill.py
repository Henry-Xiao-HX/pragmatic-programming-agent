"""Tests for finutils.bill — these tests expose the seeded bugs."""

import pytest
from finutils.bill import split_bill, apply_tip, itemized_total


class TestSplitBill:
    def test_even_split(self):
        shares = split_bill(30.00, 3)
        assert shares == [10.00, 10.00, 10.00]
        assert sum(shares) == pytest.approx(30.00)

    def test_uneven_split_remainder_goes_to_first(self):
        # $10 / 3 = $3.33 each, but 3.33*3 = $9.99, so $0.01 remainder
        # Correct: [3.34, 3.33, 3.33]
        # BUG: spreads remainder to all → [3.34, 3.34, 3.34] = $10.02 — test will FAIL
        shares = split_bill(10.00, 3)
        assert len(shares) == 3
        assert sum(shares) == pytest.approx(10.00)
        assert shares[0] == pytest.approx(3.34)
        assert shares[1] == pytest.approx(3.33)
        assert shares[2] == pytest.approx(3.33)

    def test_single_person(self):
        shares = split_bill(55.50, 1)
        assert shares == [55.50]

    def test_invalid_people(self):
        with pytest.raises(ValueError):
            split_bill(100, 0)

    def test_two_people_even_cents(self):
        # $10.00 split 2 ways: [5.00, 5.00]
        shares = split_bill(10.00, 2)
        assert shares == [5.00, 5.00]
        assert sum(shares) == pytest.approx(10.00)


class TestApplyTip:
    def test_18_percent(self):
        result = apply_tip(100.00, 18)
        assert result["tip"] == 18.00
        assert result["total"] == 118.00
        assert result["subtotal"] == 100.00

    def test_zero_tip(self):
        result = apply_tip(50.00, 0)
        assert result["tip"] == 0.0
        assert result["total"] == 50.00

    def test_rounding(self):
        result = apply_tip(33.33, 15)
        assert result["tip"] == pytest.approx(5.00, abs=0.01)


class TestItemizedTotal:
    def test_no_tax(self):
        result = itemized_total([10.00, 5.50, 3.25])
        assert result["subtotal"] == 18.75
        assert result["tax"] == 0.0
        assert result["total"] == 18.75

    def test_with_tax(self):
        result = itemized_total([100.00], tax_rate=0.08)
        assert result["tax"] == 8.00
        assert result["total"] == 108.00
