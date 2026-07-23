"""Currency formatting and conversion utilities."""


def format_currency(amount: float, symbol: str = "$", decimals: int = 2) -> str:
    """Format a numeric amount as a currency string.

    Args:
        amount: The monetary value (can be negative).
        symbol: Currency symbol prefix (default: '$').
        decimals: Number of decimal places (default: 2).

    Returns:
        Formatted string, e.g. '$1,234.56' or '-$1,234.56'.

    BUG: places the negative sign after the currency symbol for negative
    amounts, producing '$-1,234.56' instead of '-$1,234.56'.
    """
    formatted = f"{abs(amount):,.{decimals}f}"
    # BUGGY: should be f"-{symbol}{formatted}" when amount < 0
    if amount < 0:
        return f"{symbol}-{formatted}"
    return f"{symbol}{formatted}"


def convert_currency(
    amount: float, rate: float, reverse: bool = False
) -> float:
    """Convert an amount between two currencies using an exchange rate.

    Args:
        amount: Amount in the source currency.
        rate: Exchange rate (units of target currency per 1 unit of source).
        reverse: If True, divide by rate instead of multiplying (convert back).

    Returns:
        Converted amount rounded to 4 decimal places.
    """
    if reverse:
        return round(amount / rate, 4)
    return round(amount * rate, 4)


def round_to_cent(amount: float) -> float:
    """Round a float to exactly two decimal places (banker's rounding).

    Args:
        amount: Monetary value to round.

    Returns:
        Value rounded to 2 decimal places using ROUND_HALF_EVEN.
    """
    from decimal import Decimal, ROUND_HALF_EVEN

    return float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
