"""Income tax calculation utilities (simplified US-style brackets)."""

# Simplified tax brackets: (upper_limit, rate)
# Last bracket has no upper limit (represented as float('inf'))
TAX_BRACKETS = [
    (10_000, 0.10),
    (40_000, 0.12),
    (85_000, 0.22),
    (165_000, 0.24),
    (215_000, 0.32),
    (540_000, 0.35),
    (float("inf"), 0.37),
]


def calculate_tax(income: float) -> float:
    """Return total income tax owed using progressive bracket taxation.

    Args:
        income: Gross annual income in dollars.

    Returns:
        Total tax owed in dollars.

    BUG: applies the bracket rate to the full income rather than only the
    income within that bracket, causing massive over-taxation.
    """
    if income <= 0:
        return 0.0

    tax = 0.0
    previous_limit = 0.0

    for limit, rate in TAX_BRACKETS:
        if income <= previous_limit:
            break
        # BUGGY: should be min(income, limit) - previous_limit
        taxable_in_bracket = min(income, limit)
        tax += taxable_in_bracket * rate
        previous_limit = limit

    return round(tax, 2)


def marginal_rate(income: float) -> float:
    """Return the marginal tax rate for the given income.

    Args:
        income: Gross annual income in dollars.

    Returns:
        Marginal tax rate as a decimal.
    """
    if income <= 0:
        return 0.0
    for limit, rate in TAX_BRACKETS:
        if income <= limit:
            return rate
    return TAX_BRACKETS[-1][1]


def net_income(income: float) -> float:
    """Return after-tax income.

    Args:
        income: Gross annual income in dollars.

    Returns:
        Net income after tax in dollars.
    """
    return round(income - calculate_tax(income), 2)
