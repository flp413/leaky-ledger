from decimal import ROUND_DOWN, ROUND_UP, Decimal

# ruleid: money-rounding-in-customer-favour
credited = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_UP)

# ok: money-rounding-in-customer-favour
credited = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
