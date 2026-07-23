"""Interest calculation utilities."""


def simple_interest(principal: float, rate: float, time: float) -> float:
    """Return the simple interest earned.

    Args:
        principal: Initial amount of money.
        rate: Annual interest rate as a decimal (e.g. 0.05 for 5%).
        time: Time in years.

    Returns:
        Interest earned (not total balance).
    """
    return principal * rate * time


def compound_interest(
    principal: float,
    rate: float,
    time: float,
    n: int = 1,
) -> float:
    """Return the total balance after compound interest.

    Args:
        principal: Initial amount of money.
        rate: Annual interest rate as a decimal (e.g. 0.05 for 5%).
        time: Time in years.
        n: Number of compounding periods per year (default: 1 = annual).

    Returns:
        Total balance (principal + interest).

    BUG: uses `n` as an additive term instead of a multiplier in the exponent,
    producing wrong results for any n > 1 (e.g. monthly compounding).
    """
    # BUGGY: should be principal * (1 + rate / n) ** (n * time)
    return principal * (1 + rate / n) ** (n + time)


def effective_annual_rate(nominal_rate: float, n: int) -> float:
    """Return the effective annual rate (EAR) for a given nominal rate.

    Args:
        nominal_rate: Nominal annual interest rate as a decimal.
        n: Number of compounding periods per year.

    Returns:
        Effective annual rate as a decimal.
    """
    return (1 + nominal_rate / n) ** n - 1
