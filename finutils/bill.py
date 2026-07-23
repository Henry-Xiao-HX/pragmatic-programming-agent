"""Bill splitting and tip calculation utilities."""


def split_bill(total: float, people: int) -> list[float]:
    """Split a bill evenly across a number of people.

    Distributes any leftover cents (from rounding) to the first person.

    Args:
        total: Total bill amount in dollars.
        people: Number of people splitting the bill.

    Returns:
        List of amounts, one per person, that sum exactly to total.

    BUG: distributes remainder cents across ALL people instead of only
    the first person, causing the total to exceed the bill amount.
    """
    if people <= 0:
        raise ValueError("people must be a positive integer")

    base = round(total / people, 2)
    remainder = round(total - base * people, 2)

    # BUGGY: should only add remainder to shares[0]
    shares = [round(base + remainder, 2)] * people
    return shares


def apply_tip(subtotal: float, tip_percent: float) -> dict[str, float]:
    """Calculate tip and total for a given subtotal.

    Args:
        subtotal: Pre-tip bill amount in dollars.
        tip_percent: Tip percentage (e.g. 18 for 18%).

    Returns:
        Dict with keys 'subtotal', 'tip', and 'total'.
    """
    tip = round(subtotal * tip_percent / 100, 2)
    return {
        "subtotal": round(subtotal, 2),
        "tip": tip,
        "total": round(subtotal + tip, 2),
    }


def itemized_total(items: list[float], tax_rate: float = 0.0) -> dict[str, float]:
    """Return subtotal, tax, and total for a list of item prices.

    Args:
        items: List of item prices in dollars.
        tax_rate: Sales tax rate as a decimal (e.g. 0.08 for 8%).

    Returns:
        Dict with keys 'subtotal', 'tax', and 'total'.
    """
    subtotal = round(sum(items), 2)
    tax = round(subtotal * tax_rate, 2)
    return {
        "subtotal": subtotal,
        "tax": tax,
        "total": round(subtotal + tax, 2),
    }
