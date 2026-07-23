"""Tests for finutils.currency — these tests expose the seeded bugs."""

import pytest
from finutils.currency import format_currency, convert_currency, round_to_cent


class TestFormatCurrency:
    def test_positive_amount(self):
        assert format_currency(1234.56) == "$1,234.56"

    def test_zero(self):
        assert format_currency(0) == "$0.00"

    def test_negative_amount(self):
        # Correct: '-$1,234.56'
        # BUG: produces '$-1,234.56' — test will FAIL
        assert format_currency(-1234.56) == "-$1,234.56"

    def test_custom_symbol(self):
        assert format_currency(99.99, symbol="€") == "€99.99"

    def test_negative_with_custom_symbol(self):
        assert format_currency(-50.00, symbol="£") == "-£50.00"

    def test_zero_decimals(self):
        assert format_currency(1000, decimals=0) == "$1,000"

    def test_large_amount(self):
        assert format_currency(1_000_000.00) == "$1,000,000.00"


class TestConvertCurrency:
    def test_usd_to_eur(self):
        # 1 USD = 0.92 EUR → 100 USD = 92 EUR
        assert convert_currency(100, 0.92) == pytest.approx(92.0)

    def test_reverse_conversion(self):
        assert convert_currency(92, 0.92, reverse=True) == pytest.approx(100.0)

    def test_identity_rate(self):
        assert convert_currency(50, 1.0) == pytest.approx(50.0)


class TestRoundToCent:
    def test_round_down(self):
        assert round_to_cent(1.234) == 1.23

    def test_round_up(self):
        assert round_to_cent(1.235) == 1.24

    def test_bankers_rounding(self):
        # 0.5 rounds to 0 (nearest even), 1.5 rounds to 2
        assert round_to_cent(2.225) == 2.22  # banker's rounding

    def test_already_rounded(self):
        assert round_to_cent(10.00) == 10.00
