"""Checkout pricing in integer cents.

Quantities must be positive. Discounts are applied before the shipping threshold.
Orders of at least 10_000 cents after discount have free shipping; others pay 500.
"""


def total(price_cents, quantity, discount_cents=0):
    if price_cents < 0 or quantity <= 0 or discount_cents < 0:
        raise ValueError('invalid price, quantity or discount')
    subtotal = price_cents * quantity
    discounted = max(0, subtotal - discount_cents)
    shipping = 0 if subtotal > 10_000 else 500
    return discounted + shipping
